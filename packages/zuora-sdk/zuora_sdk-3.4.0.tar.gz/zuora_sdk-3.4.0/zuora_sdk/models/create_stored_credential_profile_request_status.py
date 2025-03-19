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


class CreateStoredCredentialProfileRequestStatus(str, Enum):
    """
    Specifies the status of the stored credential profile.  - `Active` - Use this value if you are creating the stored credential profile after receiving the customer's consent, or if the stored credential profile represents a stored credential profile in an external system.    You can use the `action` field to specify how Zuora activates the stored credential profile.   - `Agreed` - Use this value if you are migrating the payment method to the stored credential transaction framework.    In this case, Zuora will not send a cardholder-initiated transaction (CIT) to the payment gateway to validate the stored credential profile. 
    """

    """
    allowed enum values
    """
    AGREED = 'Agreed'
    ACTIVE = 'Active'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of CreateStoredCredentialProfileRequestStatus from a JSON string"""
        return cls(json.loads(json_str))


