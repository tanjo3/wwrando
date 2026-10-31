import binascii
import html
import io
import json
import lzma
import zipfile
import zlib
from base64 import b64decode
from dataclasses import fields

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ruamel.yaml import YAML

yaml = YAML(typ="safe")
from ruamel.yaml.error import YAMLError

from options.wwrando_options import EntranceMixMode, KeyLunacyMode, Options, SwordMode, TrickDifficulty
from randomizer import Plando
from version import VERSION_WITHOUT_COMMIT
from wwr_ui.update_checker import string_to_version

try:
  from keys.ap_rsa_private_key import AP_RSA_PRIVATE_KEY # type: ignore
except ImportError:
  AP_RSA_PRIVATE_KEY = ""

# The APWorld versions (major, minor) this build can patch.
SUPPORTED_APWORLD_VERSIONS = [(3, 0), (3, 1)]

# The randomizer build to use for each APWorld version (major, minor).
# (2, 2) stands in for every APWorld before v2.3.0, since those don't record their version.
APWORLD_VERSION_TO_BUILD = {
  (2, 2): "2.0.0",
  (2, 3): "2.1.0",
  (2, 4): "2.2.0",
  (2, 5): "2.3.0",
  (2, 6): "2.4.0",
  (3, 0): "2.6.0",
  (3, 1): "2.6.0",
}

RELEASES_PAGE_URL = "https://github.com/tanjo3/wwrando/releases?q=tag%3Aap_2"

REQUIRED_KEYS = ["Seed", "Slot", "Name", "Options", "Required Bosses", "Locations", "Entrances", "Charts"]

CORRUPTED_MESSAGE = """There was an error trying to read the APTWW file.<br><br>
  Please ensure that the file has not been modified or corrupted and try again."""

class APTWWFileError(Exception): pass

def get_link(url: str) -> str:
  return f"<a href=\"{url}\">{url}</a>"

def get_invalid_option_error(option_name: str, value) -> APTWWFileError:
  return APTWWFileError(f"The APTWW file has an invalid value for the {option_name} option: {html.escape(str(value))}")

def get_older_build_error(apworld_version_text: str, apworld_version: tuple[int, int]) -> APTWWFileError:
  build = APWORLD_VERSION_TO_BUILD[apworld_version]
  error_msg = f"""The APTWW file appears to have been generated on {apworld_version_text} of the APWorld.<br><br>
    You should use the {build} version of the randomizer build instead.<br>
    Download here: {get_link(f"https://github.com/tanjo3/wwrando/releases/tag/ap_{build}")}"""
  if apworld_version[0] == 2:
    error_msg += """<br><br>
      However, The Wind Waker is now officially supported in Archipelago. Consider updating Archipelago and regenerating your multiworld."""
  return APTWWFileError(error_msg)

def check_apworld_version(version: tuple[int, ...]):
  major_minor = version[:2]
  if major_minor in SUPPORTED_APWORLD_VERSIONS:
    return
  
  version_text = ".".join(str(part) for part in version)
  if major_minor in APWORLD_VERSION_TO_BUILD:
    raise get_older_build_error(f"v{version_text}", major_minor)
  
  if major_minor > max(SUPPORTED_APWORLD_VERSIONS):
    supported_text = " and ".join(f"v{major}.{minor}.x" for major, minor in SUPPORTED_APWORLD_VERSIONS)
    raise APTWWFileError(
      f"""The APTWW file was generated on v{version_text} of the APWorld, which is newer than this randomizer build (v{VERSION_WITHOUT_COMMIT}, made for {supported_text}).<br><br>
      Download a newer build here: {get_link(RELEASES_PAGE_URL)}"""
    )
  
  raise APTWWFileError(
    f"""The APTWW file was generated on v{version_text} of the APWorld, which this randomizer build (v{VERSION_WITHOUT_COMMIT}) doesn't recognize.<br><br>
    Check the release notes for the build to use: {get_link(RELEASES_PAGE_URL)}"""
  )

def load_private_key() -> rsa.RSAPrivateKey:
  try:
    private_key = serialization.load_pem_private_key(AP_RSA_PRIVATE_KEY.encode("utf-8"), password=None)
  except (ValueError, TypeError):
    private_key = None
  
  # Without a usable key this isn't an official build, which isn't the file's fault.
  if not isinstance(private_key, rsa.RSAPrivateKey):
    raise APTWWFileError(
      f"""This randomizer build can't read APTWW files because it was made without the decryption key.<br><br>
      Download an official build here: {get_link(RELEASES_PAGE_URL)}"""
    )
  return private_key

def decrypt_payload(payload: bytes) -> bytes:
  private_key = load_private_key()
  
  # The payload is the RSA-encrypted AES key, followed by the 12 byte nonce, followed by the AES-GCM ciphertext.
  rsa_block_size = private_key.key_size // 8
  encrypted_aes_key = payload[:rsa_block_size]
  nonce = payload[rsa_block_size:rsa_block_size+12]
  ciphertext = payload[rsa_block_size+12:]
  
  aes_key = private_key.decrypt(
    encrypted_aes_key,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None,
    ),
  )
  return AESGCM(aes_key).decrypt(nonce, ciphertext, None)

def read_encrypted_plando(payload: bytes) -> dict:
  try:
    return json.loads(decrypt_payload(payload))
  except (ValueError, InvalidTag):
    raise APTWWFileError(
      f"""The APTWW file could not be decrypted.<br><br>
      Please ensure that the file has not been modified or corrupted and try again.<br>
      If it was generated on a newer version of the APWorld, you may need a newer randomizer build: {get_link(RELEASES_PAGE_URL)}"""
    )

def check_manifest_version(zf: zipfile.ZipFile):
  # Newer APWorlds state their version outside of the encrypted payload, so a build that can't read the payload can still name the right build to use.
  try:
    manifest = json.loads(zf.read("archipelago.json"))
    version = string_to_version(manifest["world_version"])
  except (KeyError, TypeError, ValueError, AttributeError):
    return
  check_apworld_version(version)

def read_plando_from_zip(zf: zipfile.ZipFile) -> dict:
  check_manifest_version(zf)
  
  try:
    payload = zf.read("plando")
  except KeyError:
    raise APTWWFileError(CORRUPTED_MESSAGE)
  
  try:
    # v3.0.x writes base64-encoded YAML.
    # The encrypted payload of v3.1.x and newer is never valid base64.
    decoded_payload = b64decode(payload, validate=True)
  except binascii.Error:
    return read_encrypted_plando(payload)
  
  return read_plando_from_yaml(decoded_payload)

def read_plando_from_yaml(data: bytes) -> dict:
  try:
    return yaml.load(data)
  except (YAMLError, ValueError):
    raise APTWWFileError(CORRUPTED_MESSAGE)

def check_legacy_version(plando_dict: dict):
  # APWorlds before v2.5.0 don't record their version, so tell them apart by the shape of the data.
  if "Name" in plando_dict:
    raise get_older_build_error("v2.4.0", (2, 4))
  
  test_location = plando_dict["Locations"].get("Outset Island - Underneath Link's House")
  if isinstance(test_location, dict):
    raise get_older_build_error("v2.3.x", (2, 3))
  if test_location is None:
    raise APTWWFileError(CORRUPTED_MESSAGE)
  raise get_older_build_error("a pre-v2.3.0", (2, 2))

def check_plando_contents(plando_dict: dict):
  if any(key not in plando_dict for key in REQUIRED_KEYS) or not isinstance(plando_dict["Options"], dict):
    raise APTWWFileError(CORRUPTED_MESSAGE)
  
  for item_info in plando_dict["Locations"].values():
    if not isinstance(item_info, dict) or any(not isinstance(item_info.get(key), str) for key in ["name", "game", "classification"]):
      raise APTWWFileError(CORRUPTED_MESSAGE)

def load_and_validate_aptww_file(plando_file: str) -> dict:
  try:
    with open(plando_file, "rb") as f:
      file_data = f.read()
  except OSError:
    raise APTWWFileError(
      """The APTWW file could not be opened.<br><br>
      Please ensure that the program has read permissions for the file and try again."""
    )
  
  try:
    with zipfile.ZipFile(io.BytesIO(file_data), "r") as zf:
      plando_dict = read_plando_from_zip(zf)
  except (zipfile.BadZipFile, zlib.error, lzma.LZMAError, OSError, RuntimeError, ValueError):
    # This is either a damaged zip, which won't parse as YAML either, or the plain YAML file of an APWorld before v3.0.0.
    plando_dict = read_plando_from_yaml(file_data)
  
  if not isinstance(plando_dict, dict) or not isinstance(plando_dict.get("Locations"), dict):
    raise APTWWFileError(CORRUPTED_MESSAGE)
  
  if "Version" not in plando_dict:
    check_legacy_version(plando_dict)
  
  version = plando_dict["Version"]
  if not isinstance(version, list) or len(version) != 3 or not all(type(part) is int for part in version):
    raise APTWWFileError(CORRUPTED_MESSAGE)
  check_apworld_version(tuple(version))
  
  check_plando_contents(plando_dict)
  
  return plando_dict

def read_ap_plando_file(plando_file: str, options: Options) -> Plando:
  plando_file = load_and_validate_aptww_file(plando_file)
  
  # Set options dataclass from the plando file
  for field in fields(options):
    if field.name in plando_file["Options"]:
      value = plando_file["Options"][field.name]
      
      if field.type is int:
        setattr(options, field.name, value)
      elif field.type is bool:
        setattr(options, field.name, bool(value))
      elif field.type is SwordMode:
        match value:
          case 0: setattr(options, field.name, SwordMode.START_WITH_SWORD)
          case 1: setattr(options, field.name, SwordMode.NO_STARTING_SWORD)
          case 2: setattr(options, field.name, SwordMode.SWORDS_OPTIONAL)
          case 3: setattr(options, field.name, SwordMode.SWORDLESS)
          case _: raise get_invalid_option_error(field.name, value)
      elif field.type is EntranceMixMode:
          match value:
            case 0: setattr(options, field.name, EntranceMixMode.SEPARATE_DUNGEONS)
            case 1: setattr(options, field.name, EntranceMixMode.MIX_DUNGEONS)
            case _: raise get_invalid_option_error(field.name, value)
      elif field.type is TrickDifficulty:
          match value:
            case 0: setattr(options, field.name, TrickDifficulty.NONE)
            case 1: setattr(options, field.name, TrickDifficulty.NORMAL)
            case 2: setattr(options, field.name, TrickDifficulty.HARD)
            case 3: setattr(options, field.name, TrickDifficulty.VERY_HARD)
            case _: raise get_invalid_option_error(field.name, value)
      elif field.type is KeyLunacyMode:
          match value:
            case 0: setattr(options, field.name, KeyLunacyMode.START_WITH)
            case 1: setattr(options, field.name, KeyLunacyMode.VANILLA)
            case 2: setattr(options, field.name, KeyLunacyMode.DUNGEON)
            case 3: setattr(options, field.name, KeyLunacyMode.ANY_DUNGEON)
            case 4: setattr(options, field.name, KeyLunacyMode.LOCAL)
            case 5: setattr(options, field.name, KeyLunacyMode.KEYLUNACY)
            case _: raise get_invalid_option_error(field.name, value)
      else:
        print(f"Bad option: {field.name} = {value}")
    else:
      if field.name in ["randomized_gear", "starting_gear"]:
        setattr(options, field.name, field.default_factory())
      if getattr(options, field.name) is None:
        setattr(options, field.name, field.default)
  
  # Item names from other games can contain characters the message font can't encode.
  for item_info in plando_file["Locations"].values():
    if item_info["game"] != "The Wind Waker":
      item_info["name"] = item_info["name"].encode("cp1252", "replace").decode("latin-1")
  
  # Save the rest of the plando in a dataclass
  return Plando(
    f"AP_{plando_file['Seed']}_P{plando_file['Slot']}",
    plando_file["Slot"],
    plando_file["Name"],
    plando_file["Required Bosses"],
    plando_file["Locations"],
    plando_file["Entrances"],
    plando_file["Charts"]
  )
