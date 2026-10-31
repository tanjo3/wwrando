
import urllib.request
import ssl
import certifi
import json
import re
import traceback

from version import VERSION

LATEST_RELEASE_DOWNLOAD_PAGE_URL = "https://github.com/tanjo3/wwrando/releases?q=tag%3Aap_2"
LATEST_RELEASE_API_URL = "https://api.github.com/repos/tanjo3/wwrando/releases?per_page=100"

AP_RELEASE_TAG_PATTERN = re.compile(r"ap_(\d+(?:\.\d+)*)")

UPDATE_CHECK_TIMEOUT_SECONDS = 10

def string_to_version(string: str):
  string = string.removeprefix('v')
  if "-BETA" in string:
    string = string.split("-BETA")[0]
  if "_" in string:
    string = string.split("_")[0]
  version = tuple(int(e) for e in string.split('.'))
  return version

def get_latest_ap_version(releases):
  versions = []
  for release in releases:
    tag_match = AP_RELEASE_TAG_PATTERN.fullmatch(release["tag_name"])
    if tag_match and not release["draft"] and not release["prerelease"]:
      versions.append(string_to_version(tag_match.group(1)))
  return max(versions, default=None)

def check_for_updates():
  try:
    with urllib.request.urlopen(LATEST_RELEASE_API_URL, timeout=UPDATE_CHECK_TIMEOUT_SECONDS, context=ssl.create_default_context(cafile=certifi.where())) as page:
      data = json.loads(page.read().decode())
      
      curr_version = string_to_version(VERSION)
      latest_version = get_latest_ap_version(data)
      if latest_version is None:
        return None
      
      if "-BETA" in VERSION:
        print(latest_version >= curr_version)
        if latest_version >= curr_version:
          return '.'.join(str(e) for e in latest_version)
        else:
          return None
      else:
        if latest_version > curr_version:
          return '.'.join(str(e) for e in latest_version)
        else:
          return None
  except Exception as e:
    stack_trace = traceback.format_exc()
    error_message = "Error when checking for updates:\n" + str(e) + "\n\n" + stack_trace
    print(error_message)
    return "error"
