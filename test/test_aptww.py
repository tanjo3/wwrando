import base64
import io
import json
import os
import zipfile

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from ruamel.yaml import YAML

from wwrando import make_argparser
import aptww
from aptww import APTWWFileError, load_and_validate_aptww_file, read_ap_plando_file
from options.wwrando_options import Options, SwordMode, EntranceMixMode, TrickDifficulty, KeyLunacyMode
from randomizer import WWRandomizer

DEFAULT_MANIFEST = {"game": "The Wind Waker", "player": 1}

def to_pem(key, encryption=serialization.NoEncryption()) -> str:
  return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, encryption).decode("utf-8")

@pytest.fixture(scope="module")
def rsa_key():
  return rsa.generate_private_key(public_exponent=65537, key_size=2048)

@pytest.fixture(autouse=True)
def no_installed_key(monkeypatch):
  # Results must not depend on whether the real key happens to be on this machine.
  monkeypatch.setattr(aptww, "AP_RSA_PRIVATE_KEY", "")

@pytest.fixture
def installed_key(rsa_key, monkeypatch):
  monkeypatch.setattr(aptww, "AP_RSA_PRIVATE_KEY", to_pem(rsa_key))
  return rsa_key

def make_plando_dict(version=(3, 1, 0), **overrides) -> dict:
  plando_dict = {
    "Version": list(version),
    "Seed": "12345678901234567890",
    "Slot": 1,
    "Name": "Player1",
    "Options": {},
    "Required Bosses": [],
    "Locations": {},
    "Entrances": {},
    "Charts": list(range(1, 49+1)),
  }
  plando_dict.update(overrides)
  return plando_dict

def encrypt_like_apworld(data: bytes, key) -> bytes:
  # Mirrors TWWContainer._encrypt_payload in worlds/tww/__init__.py of Archipelago.
  aes_key = os.urandom(32)
  nonce = os.urandom(12)
  ciphertext = AESGCM(aes_key).encrypt(nonce, data, None)
  encrypted_aes_key = key.public_key().encrypt(
    aes_key,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None,
    ),
  )
  return encrypted_aes_key + nonce + ciphertext

def write_zip(path, plando_member: bytes | None, manifest=DEFAULT_MANIFEST, compression=zipfile.ZIP_DEFLATED) -> str:
  with zipfile.ZipFile(path, "w", compression) as zf:
    if isinstance(manifest, bytes):
      zf.writestr("archipelago.json", manifest)
    elif manifest is not None:
      zf.writestr("archipelago.json", json.dumps(manifest))
    if plando_member is not None:
      zf.writestr("plando", plando_member)
  return str(path)

def write_encrypted(path, plando_dict: dict, key, manifest=DEFAULT_MANIFEST) -> str:
  return write_zip(path, encrypt_like_apworld(json.dumps(plando_dict).encode("utf-8"), key), manifest)

def to_yaml_bytes(plando_dict: dict) -> bytes:
  stream = io.BytesIO()
  YAML(typ="safe").dump(plando_dict, stream)
  return stream.getvalue()

def write_base64_yaml(path, plando_dict: dict, compression=zipfile.ZIP_DEFLATED) -> str:
  return write_zip(path, base64.b64encode(to_yaml_bytes(plando_dict)), compression=compression)

def write_file_without_key(tmp_path, **overrides) -> str:
  return write_base64_yaml(tmp_path / "file.aptww", make_plando_dict(**overrides))

def write_plain_yaml(path, plando_dict: dict) -> str:
  path.write_bytes(to_yaml_bytes(plando_dict))
  return str(path)

def read_error(plando_file: str) -> str:
  with pytest.raises(APTWWFileError) as e:
    load_and_validate_aptww_file(plando_file)
  return str(e.value)

#region Text the APWorld's YAML writer leaves unquoted
@pytest.mark.parametrize("text", ["1e3", "0o17", "09", "-08", "+09"])
def test_text_that_looks_like_a_number_stays_text(text):
  assert aptww.read_plando_from_yaml(f"Name: {text}".encode()) == {"Name": text}

def test_real_values_keep_their_types():
  assert aptww.read_plando_from_yaml(b"Slot: 1\nCharts: [-1, 0, 49]\n") == {"Slot": 1, "Charts": [-1, 0, 49]}

@pytest.mark.parametrize("tag", ["!!int", "!!float"])
def test_number_tag_on_a_list_is_reported_as_corrupted(tag):
  with pytest.raises(APTWWFileError) as e:
    aptww.read_plando_from_yaml(f"Name: {tag} [1]".encode())
  assert str(e.value) == aptww.CORRUPTED_MESSAGE

def test_name_and_item_that_look_like_numbers_are_read_from_a_file(tmp_path):
  item_info = {"player": 2, "name": "UNQUOTED", "game": "Other Game", "classification": "filler"}
  plando_dict = make_plando_dict(version=(3, 0, 2), Name="UNQUOTED", Locations={"Some Location": item_info})
  yaml_text = to_yaml_bytes(plando_dict).replace(b"UNQUOTED", b"1e3")
  plando_file = write_zip(tmp_path / "file.aptww", base64.b64encode(yaml_text))
  loaded = load_and_validate_aptww_file(plando_file)
  assert loaded["Name"] == "1e3"
  assert loaded["Locations"]["Some Location"]["name"] == "1e3"
#endregion

#region Formats this build can read
@pytest.mark.parametrize("version", [(3, 1, 0), (3, 1, 9)])
def test_encrypted_file_is_read(tmp_path, installed_key, version):
  plando_dict = make_plando_dict(version=version)
  plando_file = write_encrypted(tmp_path / "file.aptww", plando_dict, installed_key)
  assert load_and_validate_aptww_file(plando_file) == plando_dict

@pytest.mark.parametrize("version", [(3, 0, 0), (3, 0, 2)])
def test_base64_yaml_file_is_read_without_a_key(tmp_path, version):
  plando_dict = make_plando_dict(version=version)
  plando_file = write_base64_yaml(tmp_path / "file.aptww", plando_dict)
  assert load_and_validate_aptww_file(plando_file) == plando_dict

def test_location_without_a_player_is_valid(tmp_path):
  # The APWorld leaves out the player for locations that have no item.
  location_info = {"name": "Nothing", "game": "The Wind Waker", "classification": "filler"}
  plando_dict = make_plando_dict(version=(3, 0, 0), Locations={"Dragon Roost Cavern - First Room": location_info})
  plando_file = write_base64_yaml(tmp_path / "file.aptww", plando_dict)
  assert load_and_validate_aptww_file(plando_file) == plando_dict

def test_decryption_does_not_assume_the_key_size(tmp_path, monkeypatch):
  key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
  monkeypatch.setattr(aptww, "AP_RSA_PRIVATE_KEY", to_pem(key))
  plando_dict = make_plando_dict()
  plando_file = write_encrypted(tmp_path / "file.aptww", plando_dict, key)
  assert load_and_validate_aptww_file(plando_file) == plando_dict
#endregion

#region Sending the player to the right build
@pytest.mark.parametrize("version, build", [((2, 6, 0), "2.4.0"), ((2, 5, 1), "2.3.0")])
def test_older_version_names_its_build(tmp_path, version, build):
  plando_file = write_plain_yaml(tmp_path / "file.aptww", make_plando_dict(version=version))
  message = read_error(plando_file)
  assert f"the {build} version" in message
  assert f"releases/tag/ap_{build}" in message
  assert "officially supported" in message

@pytest.mark.parametrize("plando_dict, build", [
  ({"Name": "Player1", "Locations": {}}, "2.2.0"),
  ({"Locations": {"Outset Island - Underneath Link's House": {"name": "Deku Leaf"}}}, "2.1.0"),
  ({"Locations": {"Outset Island - Underneath Link's House": "Deku Leaf"}}, "2.0.0"),
], ids=["v2.4.0", "v2.3.x", "pre-v2.3.0"])
def test_versionless_file_names_its_build(tmp_path, plando_dict, build):
  plando_file = write_plain_yaml(tmp_path / "file.aptww", plando_dict)
  message = read_error(plando_file)
  assert f"the {build} version" in message
  assert f"releases/tag/ap_{build}" in message

@pytest.mark.parametrize("version", [(3, 2, 0), (4, 0, 0)])
def test_newer_version_links_the_releases_page(tmp_path, installed_key, version):
  plando_file = write_encrypted(tmp_path / "file.aptww", make_plando_dict(version=version), installed_key)
  message = read_error(plando_file)
  assert "newer than this randomizer build" in message
  assert aptww.LATEST_RELEASE_DOWNLOAD_PAGE_URL in message

@pytest.mark.parametrize("version", [(2, 7, 0), (1, 0, 0)])
def test_unrecognized_version_links_the_releases_page(tmp_path, version):
  plando_file = write_plain_yaml(tmp_path / "file.aptww", make_plando_dict(version=version))
  message = read_error(plando_file)
  assert "doesn't recognize" in message
  assert aptww.LATEST_RELEASE_DOWNLOAD_PAGE_URL in message
#endregion

#region The version in the manifest
@pytest.mark.parametrize("world_version, expected_message", [
  ("3.2.0", "newer than this randomizer build"),
  ("2.6.0", "the 2.4.0 version"),
], ids=["newer", "older"])
def test_unsupported_manifest_version_is_reported_without_decrypting(tmp_path, rsa_key, world_version, expected_message):
  manifest = {**DEFAULT_MANIFEST, "world_version": world_version}
  plando_file = write_encrypted(tmp_path / "file.aptww", make_plando_dict(), rsa_key, manifest)
  assert expected_message in read_error(plando_file)

def test_supported_manifest_version_is_accepted(tmp_path, installed_key):
  plando_dict = make_plando_dict()
  manifest = {**DEFAULT_MANIFEST, "world_version": "3.1.1"}
  plando_file = write_encrypted(tmp_path / "file.aptww", plando_dict, installed_key, manifest)
  assert load_and_validate_aptww_file(plando_file) == plando_dict

@pytest.mark.parametrize("manifest", [
  None,
  b"not json",
  ["not", "a", "dict"],
  {**DEFAULT_MANIFEST, "world_version": "not a version"},
  {**DEFAULT_MANIFEST, "world_version": None},
], ids=["absent", "invalid JSON", "not a mapping", "invalid version", "version not text"])
def test_unusable_manifest_is_ignored(tmp_path, installed_key, manifest):
  plando_dict = make_plando_dict()
  plando_file = write_encrypted(tmp_path / "file.aptww", plando_dict, installed_key, manifest)
  assert load_and_validate_aptww_file(plando_file) == plando_dict
#endregion

#region Decryption failures
UNUSABLE_KEYS = {
  "missing": lambda key: "",
  "malformed": lambda key: "not a key",
  "password protected": lambda key: to_pem(key, serialization.BestAvailableEncryption(b"password")),
  "not RSA": lambda key: to_pem(ec.generate_private_key(ec.SECP256R1())),
}

@pytest.mark.parametrize("make_key", UNUSABLE_KEYS.values(), ids=UNUSABLE_KEYS.keys())
def test_unusable_key_is_not_reported_as_corruption(tmp_path, rsa_key, monkeypatch, make_key):
  monkeypatch.setattr(aptww, "AP_RSA_PRIVATE_KEY", make_key(rsa_key))
  plando_file = write_encrypted(tmp_path / "file.aptww", make_plando_dict(), rsa_key)
  message = read_error(plando_file)
  assert "without the decryption key" in message
  assert "modified or corrupted" not in message

def test_file_for_a_different_key_cannot_be_decrypted(tmp_path, installed_key):
  other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
  plando_file = write_encrypted(tmp_path / "file.aptww", make_plando_dict(), other_key)
  assert "could not be decrypted" in read_error(plando_file)

def test_tampered_payload_cannot_be_decrypted(tmp_path, installed_key):
  payload = bytearray(encrypt_like_apworld(json.dumps(make_plando_dict()).encode("utf-8"), installed_key))
  payload[-1] ^= 0xFF
  plando_file = write_zip(tmp_path / "file.aptww", bytes(payload))
  assert "could not be decrypted" in read_error(plando_file)

def test_truncated_payload_cannot_be_decrypted(tmp_path, installed_key):
  payload = encrypt_like_apworld(json.dumps(make_plando_dict()).encode("utf-8"), installed_key)
  plando_file = write_zip(tmp_path / "file.aptww", payload[:100])
  assert "could not be decrypted" in read_error(plando_file)

def test_decrypted_payload_that_is_not_json_cannot_be_read(tmp_path, installed_key):
  plando_file = write_zip(tmp_path / "file.aptww", encrypt_like_apworld(b"not json", installed_key))
  assert "could not be decrypted" in read_error(plando_file)
#endregion

#region Files that aren't valid
@pytest.mark.parametrize("contents", [
  b"",
  b"hello",
  b"42",
  b"- a list",
  b"Slot: 1",
  b"Locations: 5",
  b"Locations: {}",
  b"Locations: {}\nVersion: 3",
  b"Locations: 2020-13-45",
  b"\xFF\xFE\x00\x01 binary \x80\x81",
  b"PK\x03\x04 not really a zip",
], ids=[
  "empty",
  "text",
  "number",
  "list",
  "no locations",
  "locations not a mapping",
  "no version or test location",
  "version not a list",
  "invalid date",
  "binary",
  "fake zip",
])
def test_invalid_plain_file_is_reported_as_corrupted(tmp_path, contents):
  plando_file = tmp_path / "file.aptww"
  plando_file.write_bytes(contents)
  assert read_error(str(plando_file)) == aptww.CORRUPTED_MESSAGE

@pytest.mark.parametrize("missing_key", ["Seed", "Slot", "Name", "Options", "Required Bosses", "Entrances", "Charts"])
def test_file_missing_a_required_key_is_reported_as_corrupted(tmp_path, missing_key):
  plando_dict = make_plando_dict()
  del plando_dict[missing_key]
  plando_file = write_plain_yaml(tmp_path / "file.aptww", plando_dict)
  assert read_error(plando_file) == aptww.CORRUPTED_MESSAGE

@pytest.mark.parametrize("version", [[3, 1], [3, 1, 0, 0], ["3", "1", "0"], [3, True, 0], [3.0, 1.0, 0.0]])
def test_malformed_version_is_reported_as_corrupted(tmp_path, version):
  # Everything except the version is valid, so only the version check can reject these.
  plando_dict = make_plando_dict()
  plando_dict["Version"] = version
  plando_file = write_plain_yaml(tmp_path / "file.aptww", plando_dict)
  assert read_error(plando_file) == aptww.CORRUPTED_MESSAGE

@pytest.mark.parametrize("overrides", [
  {"Options": None},
  {"Locations": {"Dragon Roost Cavern - First Room": "Deku Leaf"}},
  {"Locations": {"Dragon Roost Cavern - First Room": None}},
  {"Locations": {"Dragon Roost Cavern - First Room": {"name": 5, "game": "The Wind Waker", "classification": "progression"}}},
  {"Locations": {"Dragon Roost Cavern - First Room": {"name": "Deku Leaf", "classification": "progression"}}},
  {"Locations": {"Dragon Roost Cavern - First Room": {"name": "Deku Leaf", "game": "The Wind Waker"}}},
], ids=["null options", "location is text", "location is null", "item name not text", "no game", "no classification"])
def test_malformed_contents_are_reported_as_corrupted(tmp_path, overrides):
  plando_file = write_file_without_key(tmp_path, **overrides)
  assert read_error(plando_file) == aptww.CORRUPTED_MESSAGE

def test_zip_without_plando_is_reported_as_corrupted(tmp_path):
  assert read_error(write_zip(tmp_path / "file.aptww", None)) == aptww.CORRUPTED_MESSAGE

def test_invalid_yaml_in_base64_is_reported_as_corrupted(tmp_path):
  plando_file = write_zip(tmp_path / "file.aptww", base64.b64encode(b"a: [unterminated"))
  assert read_error(plando_file) == aptww.CORRUPTED_MESSAGE

def test_missing_file_cannot_be_opened(tmp_path):
  assert "could not be opened" in read_error(str(tmp_path / "missing.aptww"))

def test_folder_cannot_be_opened(tmp_path):
  # A folder fails to open on every platform, the same way a file without read permission does.
  assert "could not be opened" in read_error(str(tmp_path))

@pytest.mark.parametrize("write_file, offset_step", [
  (lambda path, plando_dict, key: write_encrypted(path, plando_dict, key), 5),
  (lambda path, plando_dict, key: write_base64_yaml(path, plando_dict), 1),
  (lambda path, plando_dict, key: write_base64_yaml(path, plando_dict, zipfile.ZIP_BZIP2), 1),
  (lambda path, plando_dict, key: write_base64_yaml(path, plando_dict, zipfile.ZIP_LZMA), 1),
], ids=["encrypted", "deflate", "bzip2", "lzma"])
def test_damaged_file_is_rejected_or_read_correctly(tmp_path, installed_key, write_file, offset_step):
  plando_dict = make_plando_dict()
  with open(write_file(tmp_path / "file.aptww", plando_dict, installed_key), "rb") as f:
    data = f.read()
  variants = {f"truncated to {length} bytes": data[:length] for length in range(0, len(data), 16)}
  for offset in range(0, len(data), offset_step):
    damaged = bytearray(data)
    damaged[offset] ^= 0xFF
    variants[f"byte {offset} flipped"] = bytes(damaged)
  
  damaged_file = tmp_path / "damaged.aptww"
  for description, variant in variants.items():
    damaged_file.write_bytes(variant)
    try:
      result = load_and_validate_aptww_file(str(damaged_file))
    except APTWWFileError:
      continue
    except Exception as e:
      # Anything else would reach the generic stack trace dialog.
      pytest.fail(f"{description}: {e!r}")
    assert result == plando_dict, description
#endregion

#region Reading options
# These values come from the Choice classes in the APWorld's Options.py.
OPTION_VALUES = [
  ("sword_mode", 0, SwordMode.START_WITH_SWORD),
  ("sword_mode", 1, SwordMode.NO_STARTING_SWORD),
  ("sword_mode", 2, SwordMode.SWORDS_OPTIONAL),
  ("sword_mode", 3, SwordMode.SWORDLESS),
  ("mix_entrances", 0, EntranceMixMode.SEPARATE_DUNGEONS),
  ("mix_entrances", 1, EntranceMixMode.MIX_DUNGEONS),
  ("logic_obscurity", 0, TrickDifficulty.NONE),
  ("logic_obscurity", 1, TrickDifficulty.NORMAL),
  ("logic_obscurity", 2, TrickDifficulty.HARD),
  ("logic_obscurity", 3, TrickDifficulty.VERY_HARD),
  ("randomize_smallkeys", 0, KeyLunacyMode.START_WITH),
  ("randomize_smallkeys", 1, KeyLunacyMode.VANILLA),
  ("randomize_smallkeys", 2, KeyLunacyMode.DUNGEON),
  ("randomize_smallkeys", 3, KeyLunacyMode.ANY_DUNGEON),
  ("randomize_smallkeys", 4, KeyLunacyMode.LOCAL),
  ("randomize_smallkeys", 5, KeyLunacyMode.KEYLUNACY),
  ("progression_dungeons", 1, True),
  ("progression_dungeons", 0, False),
  ("num_required_bosses", 3, 3),
]

@pytest.mark.parametrize("option_name, value, expected", OPTION_VALUES)
def test_option_value_is_mapped(tmp_path, option_name, value, expected):
  plando_file = write_file_without_key(tmp_path, Options={option_name: value})
  options = Options()
  read_ap_plando_file(plando_file, options)
  assert getattr(options, option_name) == expected
  assert type(getattr(options, option_name)) is type(expected)

@pytest.mark.parametrize("option_name", ["sword_mode", "mix_entrances", "logic_precision", "randomize_smallkeys"])
def test_out_of_range_option_value_is_rejected(tmp_path, option_name):
  plando_file = write_file_without_key(tmp_path, Options={option_name: 99})
  with pytest.raises(APTWWFileError) as e:
    read_ap_plando_file(plando_file, Options())
  assert option_name in str(e.value)

def test_option_value_is_escaped_in_error_message(tmp_path):
  plando_file = write_file_without_key(tmp_path, Options={"sword_mode": "<b>bold</b>"})
  with pytest.raises(APTWWFileError) as e:
    read_ap_plando_file(plando_file, Options())
  assert "<b>" not in str(e.value)
  assert "&lt;b&gt;" in str(e.value)

def test_option_without_a_widget_falls_back_to_its_default(tmp_path):
  plando_file = write_file_without_key(tmp_path)
  options = Options()
  options.num_path_hints = None # The window gives None for options without a widget.
  read_ap_plando_file(plando_file, options)
  assert options.num_path_hints == Options().num_path_hints

@pytest.mark.parametrize("option_name", ["starting_gear", "randomized_gear"])
def test_gear_from_settings_is_discarded(tmp_path, option_name):
  plando_file = write_file_without_key(tmp_path)
  options = Options()
  setattr(options, option_name, ["Some Item"])
  read_ap_plando_file(plando_file, options)
  assert getattr(options, option_name) == getattr(Options(), option_name)

def test_cosmetic_option_from_settings_is_kept(tmp_path):
  plando_file = write_file_without_key(tmp_path)
  options = Options()
  options.custom_player_model = "Some Custom Model"
  read_ap_plando_file(plando_file, options)
  assert options.custom_player_model == "Some Custom Model"
#endregion

#region Building the plando
def test_plando_holds_the_contents_of_the_file(tmp_path):
  location_info = {"player": 2, "name": "Lantern", "game": "Other Game", "classification": "progression"}
  plando_dict = make_plando_dict(
    version=(3, 0, 0),
    Slot=7,
    Name="Some Player",
    Locations={"Dragon Roost Cavern - First Room": location_info},
    Entrances={"Dungeon Entrance on Dragon Roost Island": "Forbidden Woods"},
    Charts=list(reversed(range(1, 49+1))),
    **{"Required Bosses": ["Dragon Roost Cavern - Gohma Heart Container"]},
  )
  plando_file = write_base64_yaml(tmp_path / "file.aptww", plando_dict)
  plando = read_ap_plando_file(plando_file, Options())
  assert plando.seed == "AP_12345678901234567890_P7"
  assert plando.slot == 7
  assert plando.name == "Some Player"
  assert plando.required_bosses == plando_dict["Required Bosses"]
  assert plando.locations == plando_dict["Locations"]
  assert plando.entrances == plando_dict["Entrances"]
  assert plando.charts == plando_dict["Charts"]

@pytest.mark.parametrize("game, name, expected", [
  ("Other Game", "Pokémon ñandú", "Pokémon ñandú"),
  ("Other Game", "‘Hero’s’ “Sword”–—…™", "'Hero's' \"Sword\"--...TM"),
  ("Other Game", "€ ‚ „ Š", "? ? ? ?"),
  ("Other Game", "Sword \U0001F5E1 日本語", "Sword ? ???"),
  ("Other Game", "AC\\DC", "AC/DC"),
  ("Other Game", "\\{1A 05}", "/(1A 05)"),
  ("Other Game", "a\tb\nc\0d\x1Ae\x1Ff\x7Fg", "a b c d e f g"),
  ("Other Game", "a\x80b\x9Fc", "a b c"),
  ("Other Game", "Poke\u0301mon", "Pokémon"),
  ("Other Game", "x" * 101, "x" * 100),
  ("The Wind Waker", "Hero’s Sword", "Hero’s Sword"),
], ids=["font characters", "typographic characters", "symbols outside the font", "characters outside the font", "backslash", "control code", "control characters", "bytes the game reads as pairs", "decomposed accent", "too long", "own game untouched"])
def test_item_name_is_made_encodable_for_other_games(tmp_path, game, name, expected):
  location_info = {"player": 2, "name": name, "game": game, "classification": "progression"}
  plando_dict = make_plando_dict(version=(3, 0, 0), Locations={"Dragon Roost Cavern - First Room": location_info})
  plando_file = write_base64_yaml(tmp_path / "file.aptww", plando_dict)
  plando = read_ap_plando_file(plando_file, Options())
  assert plando.locations["Dragon Roost Cavern - First Room"]["name"] == expected

def test_sanitized_item_names_only_contain_bytes_the_message_system_treats_as_plain_text():
  allowed = set(range(0x20, 0x7F)) | set(range(0xA0, 0x100))
  allowed -= {ord("\\"), ord("{"), ord("}")}
  for code_point in range(0x110000):
    name = aptww.sanitize_foreign_item_name(chr(code_point))
    assert all(ord(character) in allowed for character in name), hex(code_point)

def test_encrypted_file_can_be_randomized(tmp_path, installed_key):
  location_info = {"player": 2, "name": "Lantern", "game": "Other Game", "classification": "progression"}
  plando_dict = make_plando_dict(Locations={"Dragon Roost Cavern - First Room": location_info}, Options={"progression_dungeons": 1})
  plando_file = write_encrypted(tmp_path / "file.aptww", plando_dict, installed_key)
  options = Options()
  plando = read_ap_plando_file(plando_file, options)
  args = make_argparser().parse_args(args=["--dry"])
  rando = WWRandomizer(plando.seed, None, str(tmp_path), options, plando, cmd_line_args=args)
  rando.randomize_all()
  assert rando.logic.done_item_locations["Dragon Roost Cavern - First Room"] == "Archipelago Item"
#endregion
