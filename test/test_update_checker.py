import io
import json
import urllib.error

import pytest

from wwr_ui import update_checker

PUBLISHED_TAGS = [
  "dev_tanjo3.1.10.7.3",
  "s8-v2",
  "ap_2.5.1",
  "ap_2.5.0",
  "miniblins-2025",
  "ap_2.4.0",
  "RS_v1.3.1",
  "1.9.10_dev",
]

def make_release(tag_name, draft=False, prerelease=False):
  return {"tag_name": tag_name, "draft": draft, "prerelease": prerelease}

def make_releases(*tag_names):
  return [make_release(tag_name) for tag_name in tag_names]

def fake_github(monkeypatch, response_body, version):
  requests = []
  
  def fake_urlopen(url, **kwargs):
    requests.append((url, kwargs))
    return io.BytesIO(response_body)
  
  monkeypatch.setattr(update_checker.urllib.request, "urlopen", fake_urlopen)
  monkeypatch.setattr(update_checker, "VERSION", version)
  return requests

#region Finding the latest Archipelago release
def test_latest_version_ignores_other_kinds_of_build():
  assert update_checker.get_latest_ap_version(make_releases(*PUBLISHED_TAGS)) == (2, 5, 1)

def test_latest_version_is_the_highest_not_the_first():
  assert update_checker.get_latest_ap_version(make_releases("ap_2.4.0", "ap_2.5.1", "ap_2.5.0")) == (2, 5, 1)

def test_latest_version_compares_numbers_not_text():
  assert update_checker.get_latest_ap_version(make_releases("ap_2.9.0", "ap_2.10.0")) == (2, 10, 0)

@pytest.mark.parametrize("unfinished_release", [
  make_release("ap_9.9.9", draft=True),
  make_release("ap_9.9.9", prerelease=True),
], ids=["draft", "prerelease"])
def test_latest_version_skips_unfinished_releases(unfinished_release):
  releases = [unfinished_release, make_release("ap_2.5.1")]
  assert update_checker.get_latest_ap_version(releases) == (2, 5, 1)

@pytest.mark.parametrize("tag_name", ["ap_test", "ap_9.9.9_dev", "ap_9.9.9-BETA"])
def test_latest_version_skips_tags_that_are_not_full_releases(tag_name):
  assert update_checker.get_latest_ap_version(make_releases(tag_name, "ap_2.5.1")) == (2, 5, 1)

def test_latest_version_is_none_without_an_ap_release():
  assert update_checker.get_latest_ap_version(make_releases("dev_tanjo3.1.10.7.3", "s8-v2", "1.9.10_dev")) is None
#endregion

#region Checking for updates
@pytest.mark.parametrize("current_version, latest_tag, expected", [
  ("2.6.0", "ap_2.7.0", "2.7.0"),
  ("2.6.0", "ap_2.6.1", "2.6.1"),
  ("2.6.0", "ap_2.6.0", None),
  ("2.6.0", "ap_2.5.1", None),
  ("2.6.0_abc1234", "ap_2.6.0", None),
  ("2.6.0-BETA", "ap_2.6.0", "2.6.0"),
  ("2.6.0-BETA", "ap_2.5.1", None),
])
def test_check_for_updates_compares_with_the_running_version(monkeypatch, current_version, latest_tag, expected):
  fake_github(monkeypatch, json.dumps(make_releases("dev_tanjo3.1.10.7.3", latest_tag)).encode(), current_version)
  assert update_checker.check_for_updates() == expected

def test_check_for_updates_without_an_ap_release_is_not_an_error(monkeypatch):
  fake_github(monkeypatch, json.dumps(make_releases("dev_tanjo3.1.10.7.3")).encode(), "2.6.0")
  assert update_checker.check_for_updates() is None

def test_check_for_updates_asks_this_repository_with_a_timeout(monkeypatch):
  requests = fake_github(monkeypatch, b"[]", "2.6.0")
  update_checker.check_for_updates()
  assert len(requests) == 1
  url, kwargs = requests[0]
  assert url == "https://api.github.com/repos/tanjo3/wwrando/releases?per_page=100"
  assert kwargs["timeout"] == update_checker.UPDATE_CHECK_TIMEOUT_SECONDS

@pytest.mark.parametrize("response_body", [
  b"not json",
  b'{"message": "API rate limit exceeded"}',
  b'[{"name": "A release without the expected fields"}]',
], ids=["not json", "rate limit message", "unexpected fields"])
def test_check_for_updates_reports_a_bad_response_as_an_error(monkeypatch, response_body):
  fake_github(monkeypatch, response_body, "2.6.0")
  assert update_checker.check_for_updates() == "error"

def test_check_for_updates_reports_a_network_failure_as_an_error(monkeypatch):
  def fail_to_connect(url, **kwargs):
    raise urllib.error.URLError("no connection")
  
  monkeypatch.setattr(update_checker.urllib.request, "urlopen", fail_to_connect)
  assert update_checker.check_for_updates() == "error"
#endregion
