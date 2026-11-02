"""Tests for security_issues.py: python3 -m unittest discover -s .github/scripts"""

import json
import os
import tempfile
import unittest

import security_issues as si

CONTEXT = {"repository": "o/r", "sha": "abc", "server": "https://github.com", "run_url": "RUN"}


def sarif(tool, results, rules=()):
    return {"version": "2.1.0", "runs": [{"tool": {"driver": {"name": tool, "rules": list(rules)}},
                                          "results": results}]}


def result(rule_id, uri, line=None, message="msg", level=None, suppressed=False):
    region = {"startLine": line} if line else {}
    item = {"ruleId": rule_id, "message": {"text": message},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": uri}, "region": region}}]}
    if level:
        item["level"] = level
    if suppressed:
        item["suppressions"] = [{"kind": "inSource"}]
    return item


class FakeGitHub:
    def __init__(self, issues=()):
        self.existing = list(issues)
        self.created, self.reopened, self.closed = [], [], []

    def issues(self):
        return self.existing

    def create(self, title, body):
        self.created.append((title, body))

    def reopen(self, number, comment):
        self.reopened.append(number)

    def close(self, number, comment):
        self.closed.append(number)


def issue(number, finding, state="OPEN", reason=None):
    return {"number": number, "state": state, "stateReason": reason,
            "body": finding.body("o/r", "abc", "https://github.com")}


class LoadTests(unittest.TestCase):
    def load(self, *documents, workspace=None):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for i, document in enumerate(documents):
                path = os.path.join(directory, "%d.sarif" % i)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(document, f)
                paths.append(path)
            return si.load_findings(paths, workspace)

    def test_groups_by_tool_rule_and_file(self):
        findings, tools = self.load(sarif("Bandit", [
            result("B602", "src/a.py", 3), result("B602", "src/a.py", 9),
            result("B602", "src/b.py", 1), result("B101", "src/a.py", 4)]))
        self.assertEqual(tools, {"bandit"})
        self.assertEqual(len(findings), 3)
        grouped = [f for f in findings.values() if f.rule_id == "B602" and f.path == "src/a.py"][0]
        self.assertEqual(grouped.lines, [3, 9])

    def test_paths_are_repository_relative(self):
        findings, _ = self.load(sarif("t", [result("r", "./.github/workflows/x.yml"),
                                            result("r", "file:///work/repo/src/y.cs")]), workspace="/work/repo")
        self.assertEqual(sorted(f.path for f in findings.values()), [".github/workflows/x.yml", "src/y.cs"])

    def test_suppressed_results_are_skipped_but_the_tool_counts(self):
        findings, tools = self.load(sarif("zizmor", [result("r", "a.yml", suppressed=True)]))
        self.assertEqual(findings, {})
        self.assertEqual(tools, {"zizmor"})

    def test_severity_from_score_or_level(self):
        rules = [{"id": "GHSA-1", "shortDescription": {"text": "Bad package"},
                  "properties": {"security-severity": "9.8"}}]
        findings, _ = self.load(sarif("osv-scanner", [result("GHSA-1", "packages.lock.json")], rules),
                                sarif("Semgrep", [result("x", "a.cs", level="note"), result("x", "a.cs", level="error")]))
        by_rule = {f.rule_id: f for f in findings.values()}
        self.assertEqual(by_rule["GHSA-1"].severity, "critical")
        self.assertEqual(by_rule["x"].severity, "high")  # most severe level wins
        self.assertEqual(by_rule["GHSA-1"].title,
                         "[critical] osv-scanner GHSA-1: Bad package (packages.lock.json)")

    def test_body_has_links_and_marker(self):
        findings, _ = self.load(sarif("Bandit", [result("B602", "src/a.py", 3, message="shell=True")]))
        finding = list(findings.values())[0]
        body = finding.body("o/r", "abc", "https://github.com")
        self.assertIn("https://github.com/o/r/blob/abc/src/a.py#L3", body)
        self.assertIn("> shell=True", body)
        match = si.MARKER.search(body)
        self.assertEqual((match.group("fingerprint"), match.group("tool")), (finding.fingerprint, "bandit"))

    def test_title_without_repeated_rule_id(self):
        rule = {"id": "python.lang.security.audit.x-detected",
                "shortDescription": {"text": "Semgrep Finding: python.lang.security.audit.x-detected"}}
        finding = si.Finding("Semgrep OSS", rule["id"], "a.py", rule)
        self.assertEqual(finding.title, "[medium] Semgrep OSS: x-detected (a.py)")
        self.assertEqual(si.Finding("Bandit", "B602", "a.py", None).title, "[medium] Bandit: B602 (a.py)")

    def test_long_titles_are_cut(self):
        finding = si.Finding("t", "r", "x" * 300, None)
        self.assertEqual(len(finding.title), si.MAX_TITLE)


class SyncTests(unittest.TestCase):
    def finding(self, rule="r1", path="a.py", tool="Bandit"):
        return si.Finding(tool, rule, path, None)

    def test_new_findings_create_issues(self):
        new = self.finding()
        github = FakeGitHub()
        summary = si.sync({new.fingerprint: new}, {"bandit"}, github, CONTEXT)
        self.assertEqual([title for title, _ in github.created], [new.title])
        self.assertEqual(summary["created"], [new.title])

    def test_open_and_dismissed_issues_are_left_alone(self):
        known, dismissed = self.finding("r1"), self.finding("r2")
        github = FakeGitHub([issue(1, known), issue(2, dismissed, "CLOSED", "NOT_PLANNED")])
        summary = si.sync({f.fingerprint: f for f in (known, dismissed)}, {"bandit"}, github, CONTEXT)
        self.assertEqual((github.created, github.reopened, github.closed), ([], [], []))
        self.assertEqual((summary["known"], summary["dismissed"]), ([1], [2]))

    def test_fixed_findings_that_come_back_are_reopened(self):
        again = self.finding()
        github = FakeGitHub([issue(3, again, "CLOSED", "COMPLETED")])
        si.sync({again.fingerprint: again}, {"bandit"}, github, CONTEXT)
        self.assertEqual(github.reopened, [3])

    def test_gone_findings_are_closed_only_for_tools_that_ran(self):
        gone_bandit, gone_semgrep = self.finding(tool="Bandit"), self.finding(tool="Semgrep")
        github = FakeGitHub([issue(4, gone_bandit), issue(5, gone_semgrep)])
        si.sync({}, {"bandit"}, github, CONTEXT)
        self.assertEqual(github.closed, [4])

    def test_issues_without_marker_are_ignored(self):
        github = FakeGitHub([{"number": 6, "state": "OPEN", "stateReason": None, "body": "manual report"}])
        si.sync({}, {"bandit"}, github, CONTEXT)
        self.assertEqual(github.closed, [])


if __name__ == "__main__":
    unittest.main()
