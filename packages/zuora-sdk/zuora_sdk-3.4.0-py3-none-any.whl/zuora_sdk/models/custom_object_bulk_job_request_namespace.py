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


class CustomObjectBulkJobRequestNamespace(str, Enum):
    """
    The namespace of the object. Custom objects belong to the `default` namespace. Zuora standard objects belong to the `com_zuora` namespace. Bulk job operations on the following Zuora standard objects are supported: * SavedQuery 
    """

    """
    allowed enum values
    """
    DEFAULT = 'default'
    COM_ZUORA = 'com_zuora'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of CustomObjectBulkJobRequestNamespace from a JSON string"""
        return cls(json.loads(json_str))


