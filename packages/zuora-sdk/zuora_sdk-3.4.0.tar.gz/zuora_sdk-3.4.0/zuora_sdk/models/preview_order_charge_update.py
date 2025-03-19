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
from zuora_sdk.models.billing_update import BillingUpdate
from zuora_sdk.models.preview_order_pricing_update import PreviewOrderPricingUpdate
from zuora_sdk.models.trigger_params import TriggerParams
from typing import Optional, Set
from typing_extensions import Self

class PreviewOrderChargeUpdate(BaseModel):
    """
    PreviewOrderChargeUpdate
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

    billing: Optional[BillingUpdate] = None
    charge_number: Optional[StrictStr] = Field(default=None, description="The number of the charge to be updated. The value of this field is inherited from the `subscriptions` > `orderActions` > `addProduct` > `chargeOverrides` > `chargeNumber` field. ", alias="chargeNumber")
    product_rate_plan_charge_number: Optional[StrictStr] = Field(default=None, description="Number of a product rate-plan charge for this subscription.", alias="productRatePlanChargeNumber")
    product_rate_plan_charge_id: Optional[StrictStr] = Field(default=None, description="ID of a product rate-plan charge for this subscription. ", alias="productRatePlanChargeId")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Container for custom fields of a Rate Plan Charge object. ", alias="customFields")
    description: Optional[StrictStr] = None
    estimated_start_date: Optional[date] = Field(default=None, description="Estimated start date of the charge. This field is only available when the charge is changed through the related order actions. **Note:** This field is available when the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/\" target=\"_blank\">Pending Charge Flexibility</a> feature is enabled. ", alias="estimatedStartDate")
    effective_date: Optional[TriggerParams] = Field(default=None, alias="effectiveDate")
    prepaid_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  The number of units included in a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). Must be a positive number (>0).       ", alias="prepaidQuantity")
    pricing: Optional[PreviewOrderPricingUpdate] = Field(default=None, description="Pricing information about the charge. ")
    unique_token: Optional[StrictStr] = Field(default=None, description="A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan charge. For example, if you want to add and update a product in the same order, assign a unique token to the newly added rate plan charge and use that token in future order actions. ", alias="uniqueToken")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["billing", "chargeNumber", "productRatePlanChargeNumber", "productRatePlanChargeId", "customFields", "description", "estimatedStartDate", "effectiveDate", "prepaidQuantity", "pricing", "uniqueToken"]

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
        """Create an instance of PreviewOrderChargeUpdate from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of billing
        if self.billing:
            _dict['billing'] = self.billing.to_dict()
        # override the default output from pydantic by calling `to_dict()` of effective_date
        if self.effective_date:
            _dict['effectiveDate'] = self.effective_date.to_dict()
        # override the default output from pydantic by calling `to_dict()` of pricing
        if self.pricing:
            _dict['pricing'] = self.pricing.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PreviewOrderChargeUpdate from a dict"""
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
            "billing": BillingUpdate.from_dict(obj["billing"]) if obj.get("billing") is not None else None,
            "chargeNumber": obj.get("chargeNumber"),
            "productRatePlanChargeNumber": obj.get("productRatePlanChargeNumber"),
            "productRatePlanChargeId": obj.get("productRatePlanChargeId"),
            "customFields": obj.get("customFields"),
            "description": obj.get("description"),
            "estimatedStartDate": obj.get("estimatedStartDate"),
            "effectiveDate": TriggerParams.from_dict(obj["effectiveDate"]) if obj.get("effectiveDate") is not None else None,
            "prepaidQuantity": obj.get("prepaidQuantity"),
            "pricing": PreviewOrderPricingUpdate.from_dict(obj["pricing"]) if obj.get("pricing") is not None else None,
            "uniqueToken": obj.get("uniqueToken")
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
