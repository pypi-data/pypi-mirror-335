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

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from zuora_sdk.models.create_order_response_order_line_items import CreateOrderResponseOrderLineItems
from zuora_sdk.models.create_order_response_ramps import CreateOrderResponseRamps
from zuora_sdk.models.create_order_response_refunds import CreateOrderResponseRefunds
from zuora_sdk.models.create_order_response_subscriptions import CreateOrderResponseSubscriptions
from zuora_sdk.models.create_order_response_write_off import CreateOrderResponseWriteOff
from zuora_sdk.models.order_status import OrderStatus
from typing import Optional, Set
from typing_extensions import Self

class CreateOrderResult(BaseModel):
    """
    CreateOrderResult
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

    account_id: Optional[StrictStr] = Field(default=None, description="The account ID for the order. This field is returned instead of the `accountNumber` field if the `returnIds` query parameter is set to `true`.", alias="accountId")
    account_number: Optional[StrictStr] = Field(default=None, description="The account number for the order.", alias="accountNumber")
    credit_memo_ids: Optional[List[StrictStr]] = Field(default=None, description="An array of the credit memo IDs generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled. This field is returned instead of the `creditMemoNumbers` field if the `returnIds` query parameter is set to `true`.", alias="creditMemoIds")
    credit_memo_numbers: Optional[List[StrictStr]] = Field(default=None, description="An array of the credit memo numbers generated in this order request. The credit memo is only available if you have the Invoice Settlement feature enabled.", alias="creditMemoNumbers")
    invoice_ids: Optional[List[StrictStr]] = Field(default=None, description="An array of the invoice IDs generated in this order request. Normally it includes one invoice ID only, but can include multiple items when a subscription was tagged as invoice separately. This field is returned instead of the `invoiceNumbers` field if the `returnIds` query parameter is set to `true`.", alias="invoiceIds")
    invoice_numbers: Optional[List[StrictStr]] = Field(default=None, description="An array of the invoice numbers generated in this order request. Normally it includes one invoice number only, but can include multiple items when a subscription was tagged as invoice separately.", alias="invoiceNumbers")
    order_id: Optional[StrictStr] = Field(default=None, description="The ID of the order created. This field is returned instead of the `orderNumber` field if the `returnIds` query parameter is set to `true`.", alias="orderId")
    order_line_items: Optional[List[CreateOrderResponseOrderLineItems]] = Field(default=None, alias="orderLineItems")
    order_number: Optional[StrictStr] = Field(default=None, description="The order number of the order created.", alias="orderNumber")
    paid_amount: Optional[StrictStr] = Field(default=None, description="The total amount collected in this order request.", alias="paidAmount")
    payment_id: Optional[StrictStr] = Field(default=None, description="The payment Id that is collected in this order request. This field is returned instead of the `paymentNumber` field if the `returnIds` query parameter is set to `true`.", alias="paymentId")
    payment_number: Optional[StrictStr] = Field(default=None, description="The payment number that is collected in this order request.", alias="paymentNumber")
    ramps: Optional[List[CreateOrderResponseRamps]] = Field(default=None, description="**Note**: This field is only available if you have the Ramps feature enabled. The [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) feature must be enabled before you can access the [Ramps](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Ramps_and_Ramp_Metrics/A_Overview_of_Ramps_and_Ramp_Metrics) feature. The Ramps feature is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information coming October 2020.  The ramp definitions created by this order request. ")
    refunds: Optional[List[CreateOrderResponseRefunds]] = None
    status: Optional[OrderStatus] = None
    subscription_ids: Optional[List[StrictStr]] = Field(default=None, description="Container for the subscription IDs of the subscriptions in an order. This field is returned if the `returnIds` query parameter is set to `true`.", alias="subscriptionIds")
    subscription_numbers: Optional[List[StrictStr]] = Field(default=None, description="Container for the subscription numbers of the subscriptions in an order. Subscriptions in the response are displayed in the same sequence as the subscriptions defined in the request. This field is in Zuora REST API version control. Supported minor versions are `206.0` and earlier.", alias="subscriptionNumbers")
    subscriptions: Optional[List[CreateOrderResponseSubscriptions]] = Field(default=None, description="**Note:** This field is in Zuora REST API version control. Supported minor versions are 223.0 or later. To use this field in the method, you must set the `zuora-version` parameter to the minor version number in the request header.  Container for the subscription numbers and statuses in an order. ")
    write_off: Optional[List[CreateOrderResponseWriteOff]] = Field(default=None, alias="writeOff")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["accountId", "accountNumber", "creditMemoIds", "creditMemoNumbers", "invoiceIds", "invoiceNumbers", "orderId", "orderLineItems", "orderNumber", "paidAmount", "paymentId", "paymentNumber", "ramps", "refunds", "status", "subscriptionIds", "subscriptionNumbers", "subscriptions", "writeOff"]

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
        """Create an instance of CreateOrderResult from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in order_line_items (list)
        _items = []
        if self.order_line_items:
            for _item_order_line_items in self.order_line_items:
                if _item_order_line_items:
                    _items.append(_item_order_line_items.to_dict())
            _dict['orderLineItems'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in ramps (list)
        _items = []
        if self.ramps:
            for _item_ramps in self.ramps:
                if _item_ramps:
                    _items.append(_item_ramps.to_dict())
            _dict['ramps'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in refunds (list)
        _items = []
        if self.refunds:
            for _item_refunds in self.refunds:
                if _item_refunds:
                    _items.append(_item_refunds.to_dict())
            _dict['refunds'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in subscriptions (list)
        _items = []
        if self.subscriptions:
            for _item_subscriptions in self.subscriptions:
                if _item_subscriptions:
                    _items.append(_item_subscriptions.to_dict())
            _dict['subscriptions'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in write_off (list)
        _items = []
        if self.write_off:
            for _item_write_off in self.write_off:
                if _item_write_off:
                    _items.append(_item_write_off.to_dict())
            _dict['writeOff'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CreateOrderResult from a dict"""
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
            "accountId": obj.get("accountId"),
            "accountNumber": obj.get("accountNumber"),
            "creditMemoIds": obj.get("creditMemoIds"),
            "creditMemoNumbers": obj.get("creditMemoNumbers"),
            "invoiceIds": obj.get("invoiceIds"),
            "invoiceNumbers": obj.get("invoiceNumbers"),
            "orderId": obj.get("orderId"),
            "orderLineItems": [CreateOrderResponseOrderLineItems.from_dict(_item) for _item in obj["orderLineItems"]] if obj.get("orderLineItems") is not None else None,
            "orderNumber": obj.get("orderNumber"),
            "paidAmount": obj.get("paidAmount"),
            "paymentId": obj.get("paymentId"),
            "paymentNumber": obj.get("paymentNumber"),
            "ramps": [CreateOrderResponseRamps.from_dict(_item) for _item in obj["ramps"]] if obj.get("ramps") is not None else None,
            "refunds": [CreateOrderResponseRefunds.from_dict(_item) for _item in obj["refunds"]] if obj.get("refunds") is not None else None,
            "status": obj.get("status"),
            "subscriptionIds": obj.get("subscriptionIds"),
            "subscriptionNumbers": obj.get("subscriptionNumbers"),
            "subscriptions": [CreateOrderResponseSubscriptions.from_dict(_item) for _item in obj["subscriptions"]] if obj.get("subscriptions") is not None else None,
            "writeOff": [CreateOrderResponseWriteOff.from_dict(_item) for _item in obj["writeOff"]] if obj.get("writeOff") is not None else None
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
