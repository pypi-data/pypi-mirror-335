"""
Module for processing Grype scan results and loading them into RegScale.
"""

import logging
import traceback
from datetime import datetime
from typing import List, Optional, Union

import click
from pathlib import Path

from regscale.core.app.utils.file_utils import (
    download_from_s3,
    find_files,
    iterate_files,
    move_file,
)
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.integration_models.grype_import import GrypeImport

logger = logging.getLogger(__name__)


class GrypeProcessingError(Exception):
    """Custom exception for Grype processing errors."""

    pass


@click.group()
def grype():
    """Performs actions from the Grype scanner integration."""
    pass


@grype.command("import_scans")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Grype .json files to process to RegScale.",
    prompt="File path for Grype files",
    import_name="grype",
)
@click.option("--destination", "-d", type=click.Path(exists=True, dir_okay=True), required=False)
@click.option("--file_pattern", "-p", type=str, required=False, default="grype*.json")
def import_scans(
    destination: Optional[Path],
    file_pattern: str,
    folder_path: Path,
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
) -> None:
    """
    Process Grype scan results from a folder containing Grype scan files and load into RegScale.
    """
    import_grype_scans(
        destination=destination,
        file_pattern=file_pattern,
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def import_grype_scans(
    folder_path: Path,
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Optional[Path] = None,
    disable_mapping: Optional[bool] = False,
    s3_bucket: Optional[str] = None,
    s3_prefix: Optional[str] = None,
    aws_profile: Optional[str] = None,
    destination: Optional[Path] = None,
    file_pattern: Optional[str] = "grype*.json",
    upload_file: Optional[bool] = True,
) -> None:
    """
    Process Grype scan results from a folder container grype scan files and load into RegScale.

    :param Path folder_path: Path to the Grype scan results JSON file
    :param int regscale_ssp_id: RegScale SSP ID
    :param datetime scan_date: The date of the scan
    :param Optional[Path] mappings_path: Path to the header mapping file, default: None
    :param Optional[bool] disable_mapping: Disable the header mapping, default: False
    :param Optional[str] s3_bucket: S3 bucket to download scan files from, default: None
    :param Optional[str] s3_prefix: Prefix (folder path) within the S3 bucket, default: None
    :param Optional[str] aws_profile: AWS profile to use for S3 access, default: None
    :param Optional[Path] destination: Destination folder for processed files, default: None
    :param Optional[str] file_pattern: File pattern to search for in the directory, default: grype*.json
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, default: True
    :raises GrypeProcessingError: If there is an error processing the Grype results
    :rtype: None
    """
    from regscale.exceptions import ValidationException
    from regscale.core.app.application import Application

    try:
        if s3_bucket and s3_prefix and aws_profile:
            download_from_s3(bucket=s3_bucket, prefix=s3_prefix, local_path=destination, aws_profile=aws_profile)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Downloaded all Grype scan files from S3. Processing...")
        elif destination and not s3_bucket:
            logger.info("Moving Grype scan files to %s", destination)
            stored_file_collection = find_files(path=folder_path, pattern=file_pattern)
            move_all_files(stored_file_collection, destination)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Done moving files")
        else:
            stored_file_collection = find_files(path=folder_path, pattern=file_pattern)
            files = stored_file_collection
        if not files:
            logger.error("No Grype scan results found in the specified directory")
            return

    except Exception as e:
        logger.error(f"Error processing Grype results: {str(e)}")
        logger.error(traceback.format_exc())
        raise GrypeProcessingError(f"Failed to process Grype results: {str(e)}")

    for file in files:
        try:
            GrypeImport(
                name="Grype",
                app=Application(),
                file_path=str(file),
                file_type=file.suffix,
                parent_id=regscale_ssp_id,
                parent_module="securityplans",
                scan_date=scan_date,
                mappings_path=mappings_path,
                disable_mapping=disable_mapping,
                upload_file=upload_file,
                file_name=file.name,
            )
        except ValidationException as e:
            logger.error(f"Validation error on {file}: {e}")
            continue
    logger.info("Completed Grype processing.")


def move_all_files(file_collection: List[Union[Path, str]], destination: Union[Path, str]) -> None:
    """
    Move all Grype files in the current directory to a folder called 'processed'.

    :param List[Union[Path, str]] file_collection: A list of file paths or S3 URIs
    :param Union[Path, str] destination: The destination folder
    :rtype: None
    """
    for file in iterate_files(file_collection):
        file_path = Path(file)
        new_filename = f"{file_path.stem}{file_path.suffix}"
        new_file_path = Path(destination) / new_filename
        move_file(file, new_file_path)
