#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RegScale STIG Integration
"""

import click

from regscale.integrations.commercial.stigv2.stig_integration import StigIntegration


@click.group(name="stigv2")
def stigv2():
    """STIG Integrations"""


@stigv2.command(name="sync_findings")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def sync_findings(regscale_ssp_id, stig_directory):
    """Sync GCP Findings to RegScale."""
    StigIntegration.sync_findings(plan_id=regscale_ssp_id, path=stig_directory)


@stigv2.command(name="sync_assets")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def sync_assets(regscale_ssp_id, stig_directory):
    """Sync GCP Assets to RegScale."""
    StigIntegration.sync_assets(plan_id=regscale_ssp_id, path=stig_directory)


@stigv2.command(name="process_checklist")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def process_checklist(regscale_ssp_id, stig_directory):
    """Process GCP Checklist."""
    StigIntegration.sync_assets(plan_id=regscale_ssp_id, path=stig_directory)
    StigIntegration.sync_findings(plan_id=regscale_ssp_id, path=stig_directory)


@stigv2.command(name="cci_assessment")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def cci_assessment(regscale_ssp_id):
    """Run CCI Assessment."""
    StigIntegration.cci_assessment(plan_id=regscale_ssp_id)
