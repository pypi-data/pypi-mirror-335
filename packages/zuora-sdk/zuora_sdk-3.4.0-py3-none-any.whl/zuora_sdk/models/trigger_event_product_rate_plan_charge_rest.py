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


class TriggerEventProductRatePlanChargeRest(str, Enum):
    """
    Specifies when to start billing the customer for the charge.  **Values**:   - `ContractEffective` is the date when the subscription's contract goes into effect and the charge is ready to be billed.   - `ServiceActivation` is the date when the services or products for a subscription have been activated and the customers have access.   - `CustomerAcceptance` is when the customer accepts the services or products for a subscription. 
    """

    """
    allowed enum values
    """
    CONTRACTEFFECTIVE = 'ContractEffective'
    SERVICEACTIVATION = 'ServiceActivation'
    CUSTOMERACCEPTANCE = 'CustomerAcceptance'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TriggerEventProductRatePlanChargeRest from a JSON string"""
        return cls(json.loads(json_str))


