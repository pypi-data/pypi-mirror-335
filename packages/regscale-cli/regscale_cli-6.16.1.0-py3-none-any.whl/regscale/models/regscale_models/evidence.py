#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for evidence model in RegScale platform"""

from typing import Optional
from pydantic import ConfigDict, Field

from regscale.models.regscale_models.regscale_model import RegScaleModel


class Evidence(RegScaleModel):
    """Evidence Model"""

    _module_slug = "evidence"
    _unique_fields: list[str] = [["title"]]

    id: int = 0
    isPublic: Optional[bool] = True
    uuid: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    evidenceOwnerId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    updateFrequency: Optional[int] = 365
    lastEvidenceUpdate: Optional[str] = None  # YY-mm-dd
    dueDate: Optional[str] = None  # YY-mm-dd

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Evidence model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_count="/api/{model_slug}/getCount",
            graph="/api/{model_slug}/graph",
            graph_by_date="/api/{model_slug}/graphByDate/{strGroupBy}/{year}",
            get_evidence_by_date="/api/{model_slug}/getEvidenceByDate/{intDays}",
            get_controls_by_evidence="/api/{model_slug}/getControlsByEvidence/{intEvidenceId}",
            get_evidence_by_control="/api/{model_slug}/getEvidenceByControl/{intControl}",
            get_evidence_by_security_plan="/api/{model_slug}/getEvidenceBySecurityPlan/{intId}",
            filter_evidence="/api/{model_slug}/filterEvidence",
            query_by_custom_field="/api/{model_slug}/queryByCustomField/{strFieldName}/{strValue}",
            mega_api="/api/{model_slug}/megaApi/{intId}",
            get_my_evidence_due_soon="/api/{model_slug}/getMyEvidenceDueSoon/{intDays}/{intPage}/{intPageSize}",
        )
