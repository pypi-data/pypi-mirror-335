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


class PostPublicNotificationDefinitionRequestCalloutHttpMethod(str, Enum):
    """
    The HTTP method of the callout.
    """

    """
    allowed enum values
    """
    GET = 'GET'
    PUT = 'PUT'
    POST = 'POST'
    DELETE = 'DELETE'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of PostPublicNotificationDefinitionRequestCalloutHttpMethod from a JSON string"""
        return cls(json.loads(json_str))


