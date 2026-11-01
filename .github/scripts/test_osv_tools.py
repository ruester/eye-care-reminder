"""Tests for osv_tools.py (no network: the OSV API is faked)."""

import os
import unittest

import osv_tools

BUILD_YML = os.path.join(os.path.dirname(__file__), "..", "workflows", "build.yml")

WORKFLOW = """steps:
  - run: |
      dotnet tool install --global wix --version 5.0.2
      wix extension add --global WixToolset.Util.wixext/5.0.2
      wix extension add --global WixToolset.UI.wixext/5.0.2
"""

VULN = {"id": "GHSA-xxxx", "summary": "Bad thing in wix", "details": "Long text",
        "database_specific": {"severity": "HIGH"},
        "affected": [{"package": {"name": "wix", "ecosystem": "NuGet"},
                      "ranges": [{"type": "ECOSYSTEM", "events": [{"introduced": "0"}, {"fixed": "5.0.3"}]}]}]}


class OsvToolsTests(unittest.TestCase):
    def test_packages(self):
        self.assertEqual(osv_tools.packages(WORKFLOW), [
            ("wix", "5.0.2", 3), ("WixToolset.Util.wixext", "5.0.2", 4), ("WixToolset.UI.wixext", "5.0.2", 5)])

    def test_build_yml_is_still_parsed(self):
        with open(BUILD_YML, encoding="utf-8") as f:
            names = [name for name, _, _ in osv_tools.packages(f.read())]
        self.assertEqual(names, ["wix", "WixToolset.Util.wixext", "WixToolset.UI.wixext"])

    def test_query_and_sarif(self):
        package_list = osv_tools.packages(WORKFLOW)
        posted = []

        def post(url, data):
            posted.append(data)
            return {"results": [{"vulns": [{"id": "GHSA-xxxx"}]}, {}, {"vulns": []}]}

        vulnerabilities = osv_tools.query(package_list, post, lambda url: VULN)
        self.assertEqual(posted[0]["queries"][0], {"package": {"name": "wix", "ecosystem": "NuGet"},
                                                   "version": "5.0.2"})
        document = osv_tools.sarif(package_list, vulnerabilities, ".github/workflows/build.yml")
        run = document["runs"][0]
        self.assertEqual(run["tool"]["driver"]["rules"][0]["properties"]["security-severity"], "7.5")
        self.assertEqual(len(run["results"]), 1)
        result = run["results"][0]
        self.assertEqual(result["message"]["text"], "wix 5.0.2 is affected by GHSA-xxxx. Fixed in: 5.0.3.")
        self.assertEqual(result["locations"][0]["physicalLocation"]["region"]["startLine"], 3)

    def test_no_vulnerabilities_gives_an_empty_run(self):
        package_list = osv_tools.packages(WORKFLOW)
        document = osv_tools.sarif(package_list, {}, "build.yml")
        self.assertEqual(document["runs"][0]["results"], [])


if __name__ == "__main__":
    unittest.main()
