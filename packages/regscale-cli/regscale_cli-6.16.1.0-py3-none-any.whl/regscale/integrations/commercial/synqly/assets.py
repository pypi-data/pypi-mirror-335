# flake8: noqa E501
# pylint: disable=line-too-long

"""Assets connector commands for the RegScale CLI"""

import click
from regscale.models import regscale_ssp_id


@click.group()
def assets() -> None:
    """Assets connector commands for the RegScale CLI"""
    pass


@assets.command(name="sync_armis_centrix")
@regscale_ssp_id()
def sync_armis_centrix(regscale_ssp_id: int) -> None:
    """Sync Assets from Armis Centrix to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Assets

    assets_armis_centrix = Assets("armis_centrix")
    assets_armis_centrix.run_sync(regscale_ssp_id=regscale_ssp_id)


@assets.command(name="sync_nozomi_vantage")
@regscale_ssp_id()
def sync_nozomi_vantage(regscale_ssp_id: int) -> None:
    """Sync Assets from Nozomi Vantage to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Assets

    assets_nozomi_vantage = Assets("nozomi_vantage")
    assets_nozomi_vantage.run_sync(regscale_ssp_id=regscale_ssp_id)


@assets.command(name="sync_servicenow")
@regscale_ssp_id()
def sync_servicenow(regscale_ssp_id: int) -> None:
    """Sync Assets from Servicenow to RegScale."""
    from regscale.models.integration_models.synqly_models.connectors import Assets

    assets_servicenow = Assets("servicenow")
    assets_servicenow.run_sync(regscale_ssp_id=regscale_ssp_id)


# pylint: enable=line-too-long
