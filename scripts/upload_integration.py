"""Send integration-test results to LaneSync (POST /api/evidence/upload)."""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

junit = sys.argv[1]
root = ET.parse(junit).getroot()
suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
total = sum(int(s.get("tests", 0)) for s in suites)
skipped = sum(int(s.get("skipped", 0)) for s in suites)
failed = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
total -= skipped
passed = total - failed

metrics = {"integration_tests": {"total": total, "passed": passed, "failed": failed}}
html = f"<html><body><h1>Integration tests (staging)</h1><p>{passed}/{total} passed, {failed} failed</p></body></html>"
body = {
    "org": os.environ["GITHUB_REPOSITORY"].split("/")[0],
    "repo": os.environ["GITHUB_REPOSITORY"].split("/")[1],
    "version": os.environ["LANESYNC_VERSION"],
    "environment": "staging",
    "pipeline": "Integration Tests",
    "run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "metrics": metrics,
    "reports": {"integration_tests": html},
}
if os.environ.get("ATTACH_JUNIT") == "1":
    with open(junit, encoding="utf-8") as fh:
        body["test_report_files"] = [{"filename": "integration-junit.xml", "content": fh.read()}]

print("Sending metrics:", json.dumps(metrics), "attach_junit:", os.environ.get("ATTACH_JUNIT") == "1")
req = urllib.request.Request(
    os.environ["SDLC_API_URL"].rstrip("/") + "/api/evidence/upload",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["LANESYNC_TOKEN"]},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        print("HTTP", resp.status, resp.read().decode()[:2000])
except urllib.error.HTTPError as err:
    print("HTTP", err.code, err.read().decode()[:2000])
    sys.exit(0)
