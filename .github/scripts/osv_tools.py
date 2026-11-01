#!/usr/bin/env python3
"""Checks the build tools installed by the CI against the OSV vulnerability database.

Usage: osv_tools.py WORKFLOW OUTPUT.sarif

The WiX Toolset and its extensions are NuGet packages installed with
`dotnet tool install` / `wix extension add` in WORKFLOW (build.yml); no lock file
knows them, so OSV-Scanner and Dependabot can't. This script reads the versions
from the workflow, asks https://api.osv.dev for known vulnerabilities and writes
them as SARIF (one result per vulnerability, located at the install line).
"""

import json
import re
import sys
import urllib.request

API = "https://api.osv.dev/v1"
TOOL_NAME = "OSV build tools"

# dotnet tool install --global wix --version 5.0.2 / wix extension add --global WixToolset.UI.wixext/5.0.2
PATTERNS = (
    re.compile(r"dotnet tool install\b.*?\s(?P<name>[A-Za-z0-9_.-]+)\s+--version\s+(?P<version>[0-9][^\s]*)"),
    re.compile(r"wix extension add\b.*?\s(?P<name>[A-Za-z0-9_.-]+)/(?P<version>[0-9][^\s]*)"),
)

# GitHub advisories give a severity word, no numeric score: map it for the issue titles.
SEVERITY_SCORES = {"CRITICAL": "9.5", "HIGH": "7.5", "MODERATE": "5.0", "MEDIUM": "5.0", "LOW": "2.0"}


def packages(workflow_text):
    """[(name, version, line)] of the NuGet tools installed by the workflow (first occurrence)."""
    found = {}
    for number, line in enumerate(workflow_text.splitlines(), 1):
        for pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                found.setdefault((match.group("name"), match.group("version")), number)
    return [(name, version, line) for (name, version), line in found.items()]


def _check_url(url):
    if not url.startswith(API + "/"):
        raise ValueError("unexpected URL: " + url)


def _post(url, data):
    _check_url(url)
    request = urllib.request.Request(url, json.dumps(data).encode(), {"Content-Type": "application/json"})
    # Bandit B310 / Semgrep dynamic-urllib-use: _check_url allows https://api.osv.dev only.
    # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
    with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
        return json.load(response)


def _get(url):
    _check_url(url)
    # Bandit B310 / Semgrep dynamic-urllib-use: _check_url allows https://api.osv.dev only.
    # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
    with urllib.request.urlopen(url, timeout=60) as response:  # nosec B310
        return json.load(response)


def query(package_list, post=_post, get=_get):
    """{(name, version): [vulnerability records]} for the packages."""
    batch = {"queries": [{"package": {"name": name, "ecosystem": "NuGet"}, "version": version}
                         for name, version, _ in package_list]}
    results = post(API + "/querybatch", batch).get("results", [])
    found = {}
    for (name, version, _), result in zip(package_list, results):
        found[(name, version)] = [get("%s/vulns/%s" % (API, vuln["id"])) for vuln in result.get("vulns") or ()]
    return found


def _score(vuln):
    severity = (vuln.get("database_specific") or {}).get("severity", "")
    return SEVERITY_SCORES.get(str(severity).upper())


def _fixed_versions(vuln, name):
    fixed = []
    for affected in vuln.get("affected") or ():
        if (affected.get("package") or {}).get("name", "").lower() != name.lower():
            continue
        for affected_range in affected.get("ranges") or ():
            fixed += [event["fixed"] for event in affected_range.get("events", ()) if "fixed" in event]
    return fixed


def sarif(package_list, vulnerabilities, workflow_path):
    rules, results = {}, []
    for name, version, line in package_list:
        for vuln in vulnerabilities.get((name, version), ()):
            vuln_id = vuln["id"]
            rule = {"id": vuln_id,
                    "shortDescription": {"text": vuln.get("summary") or vuln_id},
                    "fullDescription": {"text": (vuln.get("details") or vuln.get("summary") or vuln_id)[:4000]},
                    "helpUri": "https://osv.dev/vulnerability/" + vuln_id}
            score = _score(vuln)
            if score:
                rule["properties"] = {"security-severity": score}
            rules[vuln_id] = rule
            fixed = _fixed_versions(vuln, name)
            message = "%s %s is affected by %s." % (name, version, vuln_id)
            if fixed:
                message += " Fixed in: %s." % ", ".join(sorted(set(fixed)))
            results.append({
                "ruleId": vuln_id,
                "level": "error",
                "message": {"text": message},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": workflow_path},
                                                    "region": {"startLine": line}}}],
            })
    return {"version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{"tool": {"driver": {"name": TOOL_NAME, "informationUri": "https://osv.dev",
                                          "rules": list(rules.values())}},
                      "results": results}]}


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    workflow_path, output = argv[1], argv[2]
    with open(workflow_path, encoding="utf-8") as f:
        package_list = packages(f.read())
    if not package_list:
        print("No tools found in %s: the install commands changed, update osv_tools.py." % workflow_path,
              file=sys.stderr)
        return 1
    vulnerabilities = query(package_list)
    for name, version, _ in package_list:
        ids = [v["id"] for v in vulnerabilities.get((name, version), ())]
        print("%s %s: %s" % (name, version, ", ".join(ids) or "no known vulnerabilities"))
    with open(output, "w", encoding="utf-8") as f:
        json.dump(sarif(package_list, vulnerabilities, workflow_path), f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
