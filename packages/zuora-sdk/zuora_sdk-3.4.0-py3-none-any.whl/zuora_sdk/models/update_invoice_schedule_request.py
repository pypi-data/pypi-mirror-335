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
import pprint
import re  # noqa: F401
import json

from datetime import date
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from zuora_sdk.models.invoice_schedule_subscription import InvoiceScheduleSubscription
from zuora_sdk.models.update_invoice_schedule_item import UpdateInvoiceScheduleItem
from typing import Optional, Set
from typing_extensions import Self

class UpdateInvoiceScheduleRequest(BaseModel):
    """
    UpdateInvoiceScheduleRequest
    """ # noqa: E501
    # avoid validation
    def __init__(self, **kwargs):
        # Directly assign values without validation using `construct()`
        model = self.construct(**kwargs)
        self.__dict__.update(model.__dict__)

        _dict_all = convert_snake_dict_to_camel(kwargs, self.model_fields, self.__properties)

        _dict = self.to_alias_dict(_dict_all)
        for field_name, field_info in self.model_fields.items():
            alias = field_info.alias or field_name
            if alias in _dict:
                self.__dict__[field_name] = _dict.get(alias)
        self.update_additional_properties(self, _dict_all)
        pass

    def __setattr__(self, name, value):
        # Override setattr to bypass validation when setting attributes
        object.__setattr__(self, name, value)

    additional_subscriptions_to_bill: Optional[List[StrictStr]] = Field(default=None, description="A list of the numbers of the subscriptions that need to be billed together with the invoice schedule.   One invoice schedule can have at most 600 additional subscriptions. ", alias="additionalSubscriptionsToBill")
    invoice_separately: Optional[StrictBool] = Field(default=None, description="Whether the invoice items created from the invoice schedule appears on a separate invoice when Zuora generates invoices. ", alias="invoiceSeparately")
    next_run_date: Optional[date] = Field(default=None, description="The run date of the next execution of the invoice schedule.   By default, the next run date is the same as the run date of next pending invoice schedule item. The date can be overwritten by a different date other than the default value. If the invoice schedule has completed the execution, the next run date is `null`. ", alias="nextRunDate")
    notes: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Comments on the invoice schedule. ")
    orders: Optional[List[StrictStr]] = Field(default=None, description="A list of the IDs or numbers of the orders associated with the invoice schedule. One invoice schedule can be associated with at most 10 orders.  The orders specified in this field override all the existing orders associated with the invoice schedule. ")
    schedule_items: Optional[List[UpdateInvoiceScheduleItem]] = Field(default=None, description="Container for invoice schedule items. The maximum number of schedule items is 50.  The invoice schedule items specified in this field override all the existing invoice schedule items. ", alias="scheduleItems")
    specific_subscriptions: Optional[List[InvoiceScheduleSubscription]] = Field(default=None, description="A list of the numbers of specific subscriptions associated with the invoice schedule.  - If the subscriptions specified in this field belong to the orders specified in the `orders` field, only the specific subscriptions instead of the orders are associated with the invoice schedule.  - If only the `orders` field is specified, all the subscriptions from the order are associated with the invoice schedule.    The specific subscriptions specified in this field override all the existing specific subscriptions associated with the invoice schedule.  Example: ``` {   \"orders\": [     \"O-00000001\", \"O-00000002\"   ],   \"specificSubscriptions\": [     {       \"orderKey\": \"O-00000001\",       \"subscriptionKey\": \"S-00000001\"     }   ] } ``` - For the order with number O-00000001, only subscription S-00000001 contained in the order is associated with the invoice schedule. - For the order with number O-00000002, all subscriptions contained in the order are associated with the invoice schedule. ", alias="specificSubscriptions")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["additionalSubscriptionsToBill", "invoiceSeparately", "nextRunDate", "notes", "orders", "scheduleItems", "specificSubscriptions"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of UpdateInvoiceScheduleRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * Fields in `self.additional_properties` are added to the output dict.
        """
        excluded_fields: Set[str] = set([
            "additional_properties",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in schedule_items (list)
        _items = []
        if self.schedule_items:
            for _item_schedule_items in self.schedule_items:
                if _item_schedule_items:
                    _items.append(_item_schedule_items.to_dict())
            _dict['scheduleItems'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in specific_subscriptions (list)
        _items = []
        if self.specific_subscriptions:
            for _item_specific_subscriptions in self.specific_subscriptions:
                if _item_specific_subscriptions:
                    _items.append(_item_specific_subscriptions.to_dict())
            _dict['specificSubscriptions'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UpdateInvoiceScheduleRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        obj = convert_snake_dict_to_camel(obj, cls.model_fields, cls.__properties)

        _obj = cls.model_validate(cls.to_alias_dict(obj))
        return cls.update_additional_properties(_obj, obj)

    @classmethod
    def update_additional_properties(cls, obj, _dict: Optional[Dict[str, Any]]):
        # store additional fields in additional_properties

        # store additional fields in additional_properties
        for _key in _dict.keys():
            if _key not in cls.__properties:
                obj.additional_properties[_key] = _dict.get(_key)


        return obj
        pass

    @classmethod
    def to_alias_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        return {
            "additionalSubscriptionsToBill": obj.get("additionalSubscriptionsToBill"),
            "invoiceSeparately": obj.get("invoiceSeparately"),
            "nextRunDate": obj.get("nextRunDate"),
            "notes": obj.get("notes"),
            "orders": obj.get("orders"),
            "scheduleItems": [UpdateInvoiceScheduleItem.from_dict(_item) for _item in obj["scheduleItems"]] if obj.get("scheduleItems") is not None else None,
            "specificSubscriptions": [InvoiceScheduleSubscription.from_dict(_item) for _item in obj["specificSubscriptions"]] if obj.get("specificSubscriptions") is not None else None
        }
        return _obj


def convert_snake_dict_to_camel(_dict: dict, model_fields, properties):
    if not isinstance(_dict, dict):
        return _dict
    new_dict = {}
    for k, v in _dict.items():
        if k in model_fields:
            # model_fields: key is attribute name like bill_to_contact,
            alias = model_fields.get(k).alias or k
            new_dict[alias] = v
            pass
        else:
            new_key = snake_to_camel(k)
            if properties is not None and isinstance(properties, list) and new_key in properties:
                new_dict[new_key] = v
            else:
                new_dict[k] = v
    return new_dict
    pass


def snake_to_camel(name):
    if name is None or '_' not in name:
        return name
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
