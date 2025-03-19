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
from zuora_sdk.models.create_order_rate_plan_feature_override import CreateOrderRatePlanFeatureOverride
from zuora_sdk.models.preview_order_charge_update import PreviewOrderChargeUpdate
from typing import Optional, Set
from typing_extensions import Self

class PreviewOrderRatePlanUpdate(BaseModel):
    """
    Information about an order action of type `UpdateProduct`. 
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

    charge_updates: Optional[List[PreviewOrderChargeUpdate]] = Field(default=None, description="Array of the JSON objects containing the information for a charge update in the `updateProduct` type of order action.  When previewing an `updateProduct` order action, either the `chargeNumber` or `uniqueToken` field is required to specify the charge to update. ", alias="chargeUpdates")
    clearing_existing_features: Optional[StrictBool] = Field(default=None, description="Specifies whether all features in the rate plan will be cleared. ", alias="clearingExistingFeatures")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Container for custom fields of the Rate Plan object. The custom fields of  the Rate Plan object are used when rate plans are subscribed. ", alias="customFields")
    product_rate_plan_number: Optional[StrictStr] = Field(default=None, description="Number of a product rate plan for this subscription. ", alias="productRatePlanNumber")
    rate_plan_id: Optional[StrictStr] = Field(default=None, description="The id of the rate plan to be updated. It can be the latest version or any history version id. ", alias="ratePlanId")
    specific_update_date: Optional[date] = Field(default=None, description=" The date when the Update Product order action takes effect. This field is only applicable if there is already a future-dated Update Product order action on the subscription. The format of the date is yyyy-mm-dd.  See [Update a Product on Subscription with Future-dated Updates](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AC_Orders_Tutorials/C_Update_a_Product_in_a_Subscription/Update_a_Product_on_Subscription_with_Future-dated_Updates) for more information about this feature. ", alias="specificUpdateDate")
    subscription_product_features: Optional[List[CreateOrderRatePlanFeatureOverride]] = Field(default=None, description="List of features associated with the rate plan. The system compares the `subscriptionProductFeatures` and `featureId` fields in the request with the counterpart fields in a rate plan. The comparison results are as follows: * If there is no `subscriptionProductFeatures` field or the field is empty, features in the rate plan remain unchanged. But if the `clearingExistingFeatures` field is additionally set to true, all features in the rate plan are cleared. * If the `subscriptionProductFeatures` field contains the `featureId` nested fields, as well as the optional `description` and `customFields` nested fields, the features indicated by the featureId nested fields in the request overwrite all features in the rate plan. ", alias="subscriptionProductFeatures")
    subscription_rate_plan_number: Optional[StrictStr] = Field(default=None, description="Number of a rate plan for this subscription. ", alias="subscriptionRatePlanNumber")
    unique_token: Optional[StrictStr] = Field(default=None, description="A unique string to represent the rate plan in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, assign a unique token to the newly added rate plan and use that token in future order actions. ", alias="uniqueToken")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["chargeUpdates", "clearingExistingFeatures", "customFields", "productRatePlanNumber", "ratePlanId", "specificUpdateDate", "subscriptionProductFeatures", "subscriptionRatePlanNumber", "uniqueToken"]

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
        """Create an instance of PreviewOrderRatePlanUpdate from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in charge_updates (list)
        _items = []
        if self.charge_updates:
            for _item_charge_updates in self.charge_updates:
                if _item_charge_updates:
                    _items.append(_item_charge_updates.to_dict())
            _dict['chargeUpdates'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in subscription_product_features (list)
        _items = []
        if self.subscription_product_features:
            for _item_subscription_product_features in self.subscription_product_features:
                if _item_subscription_product_features:
                    _items.append(_item_subscription_product_features.to_dict())
            _dict['subscriptionProductFeatures'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PreviewOrderRatePlanUpdate from a dict"""
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
            "chargeUpdates": [PreviewOrderChargeUpdate.from_dict(_item) for _item in obj["chargeUpdates"]] if obj.get("chargeUpdates") is not None else None,
            "clearingExistingFeatures": obj.get("clearingExistingFeatures"),
            "customFields": obj.get("customFields"),
            "productRatePlanNumber": obj.get("productRatePlanNumber"),
            "ratePlanId": obj.get("ratePlanId"),
            "specificUpdateDate": obj.get("specificUpdateDate"),
            "subscriptionProductFeatures": [CreateOrderRatePlanFeatureOverride.from_dict(_item) for _item in obj["subscriptionProductFeatures"]] if obj.get("subscriptionProductFeatures") is not None else None,
            "subscriptionRatePlanNumber": obj.get("subscriptionRatePlanNumber"),
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
