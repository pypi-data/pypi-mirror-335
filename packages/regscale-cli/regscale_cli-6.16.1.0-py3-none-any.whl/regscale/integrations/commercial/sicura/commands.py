"""
This module contains the Click command group for Sicura.
"""

import logging

import click
from rich.console import Console
from regscale.models import regscale_id

logger = logging.getLogger("regscale")
console = Console()


@click.group()
def sicura():
    """
    Sicura Integration

    Commands for interacting with Sicura security scanning platform.
    """


@sicura.command(name="sync_assets")
@regscale_id(help="RegScale will create and update assets as children of this record.")
def sync_assets(regscale_id):
    """
    Sync Sicura assets to RegScale.

    Fetches all devices from Sicura and synchronizes them as assets into RegScale.
    """
    try:
        from regscale.integrations.commercial.sicura.scanner import SicuraIntegration

        integration = SicuraIntegration(
            plan_id=regscale_id,
        )

        with console.status("[bold green]Syncing assets from Sicura to RegScale..."):
            # Using import_assets method which handles the synchronization
            integration.sync_assets(plan_id=regscale_id)

        console.print("[bold green]Asset synchronization complete.")

    except Exception as e:
        logger.error(f"Error syncing assets: {e}", exc_info=True)
        console.print(f"[bold red]Error syncing assets: {e}")


@sicura.command(name="sync_findings")
@regscale_id(help="RegScale will create and update findings as children of this record.")
def sync_findings(regscale_id):
    """
    Sync Sicura findings to RegScale.

    Fetches all scan results from Sicura and synchronizes them as findings into RegScale.
    """
    try:
        from regscale.integrations.commercial.sicura.scanner import SicuraIntegration

        integration = SicuraIntegration(
            plan_id=regscale_id,
        )

        with console.status("[bold green]Syncing findings from Sicura to RegScale..."):
            # Using import_findings method which handles the synchronization
            integration.sync_findings(plan_id=regscale_id)

        console.print("[bold green]Finding synchronization complete.")

    except Exception as e:
        logger.error(f"Error syncing findings: {e}", exc_info=True)
        console.print(f"[bold red]Error syncing findings: {e}")
