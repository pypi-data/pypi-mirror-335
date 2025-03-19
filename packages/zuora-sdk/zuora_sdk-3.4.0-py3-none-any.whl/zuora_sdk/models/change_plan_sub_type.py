# coding: utf-8

"""
    Zuora API Reference

    REST API reference for the Zuora Billing, Payments, and Central Platform! Check out the [REST API Overview](https://www.zuora.com/developer/api-references/api/overview/).

    The version of the OpenAPI document: 2024-05-20
    Contact: docs@zuora.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class ChangePlanSubType(str, Enum):
    """
    Use this field to choose the sub type for your change plan order action.  However, if you do not set this field, the field will be automatically generated by the system according to the following rules:  When the old and new rate plans are within the same Grading catalog group: * If the grade of new plan is greater than that of the old plan, this is an \"Upgrade\". * If the grade of new plan is less than that of the old plan, this is a \"Downgrade\". * If the grade of new plan equals that of the old plan, this is a \"Crossgrade\".  When the old and new rate plans are not in the same Grading catalog group, or either has no group, this is \"PlanChanged\". 
    """

    """
    allowed enum values
    """
    UPGRADE = 'Upgrade'
    DOWNGRADE = 'Downgrade'
    CROSSGRADE = 'Crossgrade'
    PLANCHANGED = 'PlanChanged'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ChangePlanSubType from a JSON string"""
        return cls(json.loads(json_str))


