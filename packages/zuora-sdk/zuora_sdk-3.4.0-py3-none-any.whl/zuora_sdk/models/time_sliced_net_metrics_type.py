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


class TimeSlicedNetMetricsType(str, Enum):
    """
    Indicates whether this metrics is for a regular charge or a discount charge.
    """

    """
    allowed enum values
    """
    REGULAR = 'Regular'
    DISCOUNT = 'Discount'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of TimeSlicedNetMetricsType from a JSON string"""
        return cls(json.loads(json_str))


