#!/usr/bin/env python3
"""Turns the findings of the security scanners into GitHub issues (label "security").

Usage: security_issues.py SARIF_DIR [--dry-run]

Every scanner of .github/workflows/security.yml writes SARIF (the standard format
for static analysis results). Findings are grouped per (tool, rule, file): one
issue each, identified by a fingerprint in a hidden marker in the issue body, so
weekly runs don't create duplicates. The issue state is the triage:

- open: known, not fixed yet (left alone, its body is not rewritten);
- closed as "not planned": dismissed (accepted risk / false positive), never reopened;
- closed as "completed": fixed; reopened with a comment if the finding comes back.

Open issues whose finding is no longer reported are closed as completed, but only
for tools that ran in this scan (a failed scanner must not close its issues).

Needs the GitHub CLI (gh) with GH_TOKEN; GITHUB_REPOSITORY, GITHUB_SHA,
GITHUB_SERVER_URL and GITHUB_RUN_ID (set by GitHub Actions) are used for links.
"""

import glob
import hashlib
import json
import os
import re
import subprocess
import sys

LABEL = "security"
MARKER = re.compile(r"<!-- security-scan: (?P<fingerprint>[0-9a-f]{16}) tool=(?P<tool>[^ ]+) -->")
MAX_TITLE = 200
MAX_LINES_LISTED = 20


class Finding:
    def __init__(self, tool, rule_id, path, rule):
        self.tool = tool
        self.rule_id = rule_id
        self.path = path
        self.rule = rule or {}
        self.lines = []
        self.messages = []
        self.level = "none"

    @property
    def fingerprint(self):
        key = "\n".join((self.tool, self.rule_id, self.path))
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    @property
    def severity(self):
        """GitHub's security-severity (CVSS score) if the tool gives one, else the SARIF level."""
        score = self.rule.get("properties", {}).get("security-severity")
        try:
            score = float(score)
        except (TypeError, ValueError):
            return {"error": "high", "warning": "medium", "note": "low"}.get(self.level, "medium")
        if score >= 9:
            return "critical"
        if score >= 7:
            return "high"
        if score >= 4:
            return "medium"
        return "low"

    @property
    def title(self):
        description = _text(self.rule.get("shortDescription"))
        where = self.path or "repository"
        if not description or self.rule_id in description:
            # e.g. Semgrep: "Semgrep Finding: python.lang.security.audit.x" -> "x"
            title = "[%s] %s: %s (%s)" % (self.severity, self.tool, self.rule_id.rsplit(".", 1)[-1], where)
        else:
            title = "[%s] %s %s: %s (%s)" % (self.severity, self.tool, self.rule_id, description, where)
        return title if len(title) <= MAX_TITLE else title[:MAX_TITLE - 1] + "…"

    def body(self, repository, sha, server):
        rule = self.rule
        lines = ["%s found **%s** (severity: %s)." % (self.tool, self.rule_id, self.severity), ""]
        description = _text(rule.get("fullDescription")) or _text(rule.get("shortDescription"))
        if description:
            lines += [description, ""]
        if self.path:
            locations = []
            for line in sorted(set(self.lines))[:MAX_LINES_LISTED]:
                locations.append("[line %d](%s/%s/blob/%s/%s#L%d)" % (line, server, repository, sha,
                                                                      self.path, line))
            where = ", ".join(locations) if locations else "the file"
            lines += ["**File:** `%s` (%s)" % (self.path, where), ""]
        for message in list(dict.fromkeys(self.messages))[:5]:
            lines += ["> " + message.replace("\n", "\n> "), ""]
        help_uri = rule.get("helpUri")
        if help_uri:
            lines += ["More information: " + help_uri, ""]
        lines += [
            "---",
            "Created by the scheduled security scan (`.github/workflows/security.yml`). "
            "Fix it and close this issue as *completed*, or close it as *not planned* to "
            "dismiss the finding (it is then not reported again).",
            "",
            "<!-- security-scan: %s tool=%s -->" % (self.fingerprint, _tool_key(self.tool)),
        ]
        return "\n".join(lines)


def _text(message):
    if not isinstance(message, dict):
        return ""
    return (message.get("text") or message.get("markdown") or "").strip()


def _tool_key(tool):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", tool).lower()


LEVELS = ("none", "note", "warning", "error")


def _relative(uri, workspace):
    """Repository-relative path of a SARIF artifact URI."""
    if uri.startswith("file://"):
        uri = uri[len("file://"):]
    if workspace and uri.startswith(workspace.rstrip("/") + "/"):
        uri = uri[len(workspace.rstrip("/")) + 1:]
    while uri.startswith("./"):
        uri = uri[2:]
    return uri


def _location(result, workspace):
    for location in result.get("locations") or ():
        physical = location.get("physicalLocation") or {}
        uri = (physical.get("artifactLocation") or {}).get("uri", "")
        line = (physical.get("region") or {}).get("startLine")
        return _relative(uri, workspace), line
    return "", None


def load_findings(paths, workspace=None):
    """(findings by fingerprint, tool keys that ran) from SARIF files."""
    findings = {}
    tools = set()
    for path in paths:
        with open(path, encoding="utf-8") as f:
            sarif = json.load(f)
        for run in sarif.get("runs", ()):
            driver = run.get("tool", {}).get("driver", {})
            tool = driver.get("name") or os.path.splitext(os.path.basename(path))[0]
            tools.add(_tool_key(tool))
            rules = {rule.get("id"): rule for rule in driver.get("rules", ()) if rule.get("id")}
            for result in run.get("results", ()):
                if result.get("suppressions"):
                    continue
                rule_id = result.get("ruleId") or "finding"
                uri, line = _location(result, workspace)
                finding = Finding(tool, rule_id, uri, rules.get(rule_id))
                finding = findings.setdefault(finding.fingerprint, finding)
                if line:
                    finding.lines.append(int(line))
                message = _text(result.get("message"))
                if message:
                    finding.messages.append(message)
                level = result.get("level") or (rules.get(rule_id) or {}).get(
                    "defaultConfiguration", {}).get("level", "warning")
                if level in LEVELS and LEVELS.index(level) > LEVELS.index(finding.level):
                    finding.level = level
    return findings, tools


class GitHub:
    """The few gh calls needed (replaced by a fake in the tests)."""

    def __init__(self, repository, dry_run=False):
        self.repository = repository
        self.dry_run = dry_run

    def _gh(self, *args, read=False):
        command = ["gh"] + list(args) + ["--repo", self.repository]
        if self.dry_run and not read:
            print("dry run:", " ".join(command[:4]), "...")
            return ""
        return subprocess.run(command, check=True, stdout=subprocess.PIPE, universal_newlines=True).stdout

    def ensure_label(self):
        self._gh("label", "create", LABEL, "--color", "B60205", "--force",
                 "--description", "Found by the scheduled security scan")

    def issues(self):
        output = self._gh("issue", "list", "--label", LABEL, "--state", "all", "--limit", "1000",
                          "--json", "number,state,stateReason,body", read=True)
        return json.loads(output or "[]")

    def create(self, title, body):
        self._gh("issue", "create", "--title", title, "--body", body, "--label", LABEL)

    def reopen(self, number, comment):
        self._gh("issue", "reopen", str(number), "--comment", comment)

    def close(self, number, comment):
        self._gh("issue", "close", str(number), "--reason", "completed", "--comment", comment)


def sync(findings, tools, github, context):
    """Creates, reopens and closes issues. Returns a summary {action: [titles or numbers]}."""
    summary = {"created": [], "reopened": [], "closed": [], "known": [], "dismissed": []}
    existing = {}
    for issue in github.issues():
        match = MARKER.search(issue.get("body") or "")
        if match:
            existing[match.group("fingerprint")] = (issue, match.group("tool"))
    run_link = context["run_url"]
    for fingerprint, finding in sorted(findings.items(), key=lambda item: item[1].title):
        issue = existing.get(fingerprint, (None, None))[0]
        if issue is None:
            github.create(finding.title, finding.body(context["repository"], context["sha"], context["server"]))
            summary["created"].append(finding.title)
        elif issue["state"].upper() == "OPEN":
            summary["known"].append(issue["number"])
        elif (issue.get("stateReason") or "").upper() == "NOT_PLANNED":
            summary["dismissed"].append(issue["number"])
        else:
            github.reopen(issue["number"], "Found again by the security scan (%s)." % run_link)
            summary["reopened"].append(issue["number"])
    for fingerprint, (issue, tool) in existing.items():
        if issue["state"].upper() == "OPEN" and fingerprint not in findings and tool in tools:
            github.close(issue["number"], "No longer found by the security scan (%s)." % run_link)
            summary["closed"].append(issue["number"])
    return summary


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    paths = sorted(glob.glob(os.path.join(args[0], "**", "*.sarif"), recursive=True))
    findings, tools = load_findings(paths, os.environ.get("GITHUB_WORKSPACE"))
    print("%d SARIF file(s), tools: %s, %d finding(s)" % (len(paths), ", ".join(sorted(tools)) or "-",
                                                         len(findings)))
    for finding in findings.values():
        print("  " + finding.title)
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    context = {
        "repository": repository,
        "sha": os.environ.get("GITHUB_SHA", "main"),
        "server": server,
        "run_url": "%s/%s/actions/runs/%s" % (server, repository, os.environ.get("GITHUB_RUN_ID", "")),
    }
    github = GitHub(repository, dry_run)
    github.ensure_label()
    summary = sync(findings, tools, github, context)
    for action, items in summary.items():
        print("%s: %d" % (action, len(items)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
