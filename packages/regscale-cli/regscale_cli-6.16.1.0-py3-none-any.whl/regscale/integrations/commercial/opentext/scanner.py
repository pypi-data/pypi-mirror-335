"""
Web inspect Scanner Class
"""

import logging
from typing import Iterator
from typing import List, Optional

from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models import IssueSeverity, IssueStatus, regscale_models
from regscale.models.integration_models.flat_file_importer import FlatFileImporter

logger = logging.getLogger("regscale")
XML = "*.xml"


class WebInspect(FlatFileImporter):
    finding_severity_map = {
        4: regscale_models.IssueSeverity.Critical,
        3: regscale_models.IssueSeverity.High,
        2: regscale_models.IssueSeverity.Moderate,
        1: regscale_models.IssueSeverity.Low,
        0: regscale_models.IssueSeverity.NotAssigned,
    }

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Web Inspect")
        self.required_headers = [
            "Issues",
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping, xml_tag="Scan"
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        data = self.mapping.get_value(self.validater.data, "Issues", {}).get("Issue", [])
        vuln_count = 0
        for item in data:
            severity_int = int(item.get("Severity", 0))
            severity = self.finding_severity_map.get(severity_int, IssueSeverity.NotAssigned)

            if severity in (IssueSeverity.High, IssueSeverity.Moderate, IssueSeverity.Low):
                vuln_count += 1
        super().__init__(
            logger=logger,
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=True,
            finding_severity_map=self.finding_severity_map,
            asset_count=len(data),
            vuln_count=vuln_count,
            **kwargs,
        )

    def create_asset(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the processed XML files

        :yields: Iterator[IntegrationAsset]
        """
        # Get a list of issues from xml node Issues
        if data := self.mapping.get_value(self.validater.data, "Issues", {}):
            issues_dict = data.get("Issue", [])
            for issue in issues_dict:
                yield from self.parse_asset(issue)

    def parse_asset(self, issue: dict) -> Iterator[IntegrationAsset]:
        """
        Parse the asset from an element

        :param dict issue: The Issue element
        :yields: IntegrationAsset
        """
        host = issue.get("Host")
        if host:
            yield IntegrationAsset(name=host, asset_type="Other", asset_category="Hardware", identifier=host)

    def create_vuln(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the XML files

        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        # Get a list of issues from xml node Issues
        if data := self.mapping.get_value(self.validater.data, "Issues", {}):
            issues_dict = data.get("Issue", [])
            for issue in issues_dict:
                if res := self.parse_finding(issue):
                    yield res

    @staticmethod
    def _parse_report_section(sections: List[dict], section_name: str) -> str:
        """
        Extract text from a specific report section.

        :param List[dict] sections: List of report sections
        :param str section_name: Name of the section to extract text from
        :return: Text from the specified section
        :rtype: str
        """
        return next((section.get("SectionText", "") for section in sections if section.get("Name") == section_name), "")

    def parse_finding(self, issue: dict) -> Optional[IntegrationFinding]:
        """
        Parse the dict to an Integration Finding

        :param dict issue: The Issue element
        :returns The Integration Finding
        :rtype Optional[IntegrationFinding]
        """
        severity_int = int(issue.get("Severity", 3))
        severity = self.finding_severity_map.get(severity_int, IssueSeverity.High)
        title = issue.get("Name", "")
        host = issue.get("Host", "")
        plugin_id = issue.get("VulnerabilityID", "")
        external_id = str(host + plugin_id)
        sections = issue.get("ReportSection")
        description = self._parse_report_section(sections, "Summary")
        mitigation = self._parse_report_section(sections, "Fix")

        if severity in (IssueSeverity.Critical, IssueSeverity.High, IssueSeverity.Moderate, IssueSeverity.Low):
            return IntegrationFinding(
                external_id=external_id,
                asset_identifier=host,
                control_labels=[],
                description=description,
                status=IssueStatus.Open,
                title=title,
                severity=severity,
                severity_int=severity_int,
                category=f"{self.name} Vulnerability",
                plugin_id=plugin_id,
                plugin_name=title,
                rule_id=plugin_id,
                recommendation_for_mitigation=mitigation,
                source_report=self.name,
            )
        return None
