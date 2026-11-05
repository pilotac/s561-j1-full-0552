"""Integration tests run after the staging deployment."""
import json
import os
import urllib.request

import pytest

from calc import add, mul

STAGING_URL = os.environ.get("STAGING_URL", "https://api.github.com/repos/pilotac/s561-j1-full-0552")


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "integration-tests"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, json.loads(resp.read().decode())


def test_staging_target_reachable():
    status, body = _get(STAGING_URL)
    assert status == 200
    assert body["full_name"] == "pilotac/s561-j1-full-0552"


def test_deployed_package_add_and_mul():
    assert add(2, 3) == 5
    assert mul(4, 5) == 20


def test_round_trip_calc_through_json():
    payload = json.loads(json.dumps({"a": 7, "b": 6}))
    assert add(payload["a"], payload["b"]) == 13


@pytest.mark.skipif(os.environ.get("INTEG_FAIL") != "1", reason="failure case only when INTEG_FAIL=1")
def test_deliberate_failure_checkout_total():
    assert add(2, 2) == 5, "deliberate integration failure"
