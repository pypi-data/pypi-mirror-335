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
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class OrderDeltaMrr(BaseModel):
    """
    Order Delta Mrr. This is a metric that reflects the change to the TCV on rate plan charge object as the result of the order. 
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

    charge_number: Optional[StrictStr] = Field(default=None, description="The charge number for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. ", alias="chargeNumber")
    currency: Optional[StrictStr] = Field(default=None, description="ISO 3-letter currency code (uppercase). For example, USD. ")
    end_date: Optional[date] = Field(default=None, description="The end date for the order delta metric. ", alias="endDate")
    gross_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The gross amount for the metric. The is the amount excluding applied discount. ", alias="grossAmount")
    net_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The net amount for the metric. The is the amount with discounts applied ", alias="netAmount")
    order_action_id: Optional[StrictStr] = Field(default=None, description="The Id for the related Order Action. This field can be null if the metric is generated for an Order Line Item. ", alias="orderActionId")
    order_action_sequence: Optional[StrictStr] = Field(default=None, description="The sequence for the related Order Action. This field can be null if the metric is generated for an Order Line Item. ", alias="orderActionSequence")
    order_action_type: Optional[StrictStr] = Field(default=None, description="The type for the related Order Action. This field can be null if the metric is generated for an Order Line Item. ", alias="orderActionType")
    order_line_item_number: Optional[StrictStr] = Field(default=None, description="A sequential number auto-assigned for each of order line items in a order, used as an index, for example, \"1\". ", alias="orderLineItemNumber")
    product_rate_plan_charge_id: Optional[StrictStr] = Field(default=None, description="The Id for the associated Product Rate Plan Charge. This field can be null if the Order Line Item is not associated with a Product Rate Plan Charge.", alias="productRatePlanChargeId")
    rate_plan_charge_id: Optional[StrictStr] = Field(default=None, description="The id for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. ", alias="ratePlanChargeId")
    start_date: Optional[date] = Field(default=None, description="The start date for the order delta metric. ", alias="startDate")
    subscription_number: Optional[StrictStr] = Field(default=None, description="The number of the subscription. This field can be null if the metric is generated for an Order Line Item. ", alias="subscriptionNumber")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["chargeNumber", "currency", "endDate", "grossAmount", "netAmount", "orderActionId", "orderActionSequence", "orderActionType", "orderLineItemNumber", "productRatePlanChargeId", "ratePlanChargeId", "startDate", "subscriptionNumber"]

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
        """Create an instance of OrderDeltaMrr from a JSON string"""
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
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of OrderDeltaMrr from a dict"""
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
            "chargeNumber": obj.get("chargeNumber"),
            "currency": obj.get("currency"),
            "endDate": obj.get("endDate"),
            "grossAmount": obj.get("grossAmount"),
            "netAmount": obj.get("netAmount"),
            "orderActionId": obj.get("orderActionId"),
            "orderActionSequence": obj.get("orderActionSequence"),
            "orderActionType": obj.get("orderActionType"),
            "orderLineItemNumber": obj.get("orderLineItemNumber"),
            "productRatePlanChargeId": obj.get("productRatePlanChargeId"),
            "ratePlanChargeId": obj.get("ratePlanChargeId"),
            "startDate": obj.get("startDate"),
            "subscriptionNumber": obj.get("subscriptionNumber")
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
