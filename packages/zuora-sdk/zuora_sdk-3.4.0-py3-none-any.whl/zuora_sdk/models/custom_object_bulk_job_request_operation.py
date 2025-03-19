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


class CustomObjectBulkJobRequestOperation(str, Enum):
    """
    The operation that the bulk job performs. Only the users that have the \"Delete Custom Objects\" permission can submit a `delete` bulk job request. Only the users that have the \"Edit Custom Objects\" permission can submit a `create` or `update` bulk job request. See [Platform Permissions](https://knowledgecenter.zuora.com/Billing/Tenant_Management/A_Administrator_Settings/User_Roles/h_Platform_Roles#Platform_Permissions) for more information.
    """

    """
    allowed enum values
    """
    DELETE = 'delete'
    CREATE = 'create'
    UPDATE = 'update'

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of CustomObjectBulkJobRequestOperation from a JSON string"""
        return cls(json.loads(json_str))


