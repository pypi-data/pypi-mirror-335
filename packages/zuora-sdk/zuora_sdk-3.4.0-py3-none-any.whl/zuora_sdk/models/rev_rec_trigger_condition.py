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


class RevRecTriggerCondition(str, Enum):
    """
    Specifies the revenue recognition trigger condition.    * `Contract Effective Date`    * `Service Activation Date`   * `Customer Acceptance Date` 
    """

    """
    allowed enum values
    """
    CONTRACT_EFFECTIVE_DATE = 'Contract Effective Date'
    SERVICE_ACTIVATION_DATE = 'Service Activation Date'
    CUSTOMER_ACCEPTANCE_DATE = 'Customer Acceptance Date'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of RevRecTriggerCondition from a JSON string"""
        return cls(json.loads(json_str))


