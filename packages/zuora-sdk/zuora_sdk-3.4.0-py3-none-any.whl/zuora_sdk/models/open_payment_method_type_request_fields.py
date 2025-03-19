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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class OpenPaymentMethodTypeRequestFields(BaseModel):
    """
    OpenPaymentMethodTypeRequestFields
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

    checksum: Optional[StrictBool] = Field(default=None, description="The checksum value of a payment method is used to identify if this payment method is the same as another one, or if this payment method is altered to another new payment method.  Set this flag to `true` for the following scenarios:   - The field should be part of checksum calculation.   - The field is a critical differentiator for this type.       For example, if you select the credit card number and expiration date as the checksum fields for the CreditCard payment method type, when you modified the expiration date, Zuora considers this payment method as a different payment method compared to the original one.  This field cannot be `null` or empty.  This field cannot be updated after the creation of the custom payment method type. ")
    default_value: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The default value of the field. `null` is supported.  If a required field is added after the custom payment method type is published, `defaultValue` is required.  This field cannot be updated after the creation of the custom payment method type. ", alias="defaultValue")
    description: Optional[Annotated[str, Field(strict=True, max_length=70)]] = Field(default=None, description="An explanation of this field. It can be an empty string. ")
    editable: Optional[StrictBool] = Field(default=None, description="Specify `true` if this field can be updated through PUT API or UI.  This field cannot be `null` or empty.  Note: If `editable` is set to `false`, you can specify the value of this field in the UI and POST API when creating a payment method. However, after you created the payment method, you cannot edit this field through PUT API or UI. ")
    index: Optional[StrictInt] = Field(default=None, description="The order of the field in this type, starting from 1. It must be unique.  This field cannot be `null` or empty.  This field cannot be updated after the creation of the custom payment method type. ")
    label: Optional[Annotated[str, Field(strict=True, max_length=30)]] = Field(default=None, description="The label that is used to refer to this field in the Zuora UI.  An alphanumeric string, excluding JSON preserved characters e.g.  * \\ ’ ”  This field cannot be `null` or empty or any reserved field name. ")
    max_length: Optional[StrictInt] = Field(default=None, description="A maximum length limitation of the field value. The specified value must be in the range of [1,8000]. `maxLength` must be greater than or equal to `minLength`.  After the custom payment method type is created, you can only increase the value of `maxLength`. Decreasing the value is not supported. ", alias="maxLength")
    min_length: Optional[StrictInt] = Field(default=None, description="A minimal length limitation of the field value.      0 <= `minLength` <= `maxLength`  The value of this metadata does not determine whether the field is a required field. It only defines the minimal length of the field value.  After the custom payment method type is created, you can only decrease the value of `minLength`. Increasing the value is not supported. ", alias="minLength")
    name: Optional[Annotated[str, Field(strict=True, max_length=30)]] = Field(default=None, description="The API name of this field. It must be uinique.  An alphanumeric string starting with a capital letter, excluding JSON preserved characters e.g.  * \\ ’ ”  Though this field must be defined with a string starting with a capital letter, use this string with the first letter in lowercase when you specify it in other API operations. For example, `AmazonPayToken` is the defined value for `name`. In the request of the \"Create a payment method\" API operation, use `amazonPayToken`.  This field cannot be `null` or empty or any reserved field name.  This field cannot be updated after the creation of the custom payment method type. ")
    representer: Optional[StrictBool] = Field(default=None, description="This flag determines whether this field will be used for identifying this payment method in the Zuora UI. The field will be shown in the Payment Method field in the UI.  This field cannot be `null` or empty.  Notes:   - In one custom payment method type, set `representer` to `true` for at least one field .   - In one custom payment method type, you can set `representer` to `true` for multiple fields. ")
    required: Optional[StrictBool] = Field(default=None, description="Specify whether this field is required.  This field cannot be `null` or empty.  This field cannot be updated after the creation of the custom payment method type. ")
    type: Optional[StrictStr] = None
    visible: Optional[StrictBool] = Field(default=None, description="Specify `true` if this field can be retrieved through GET API or UI for displaying payment method details.  This field cannot be `null` or empty.  Notes:    - If `visible` is set to `false`, you can still specify the value of this field in the UI and POST API when creating the payment method.   - If `visible` is set to `false` and `editable` is set to `true`, this field is not accessible through GET API or UI for displaying details, but you can still see it and edit the value in the UI and PUT API when updating this payment method. ")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["checksum", "defaultValue", "description", "editable", "index", "label", "maxLength", "minLength", "name", "representer", "required", "type", "visible"]

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
        """Create an instance of OpenPaymentMethodTypeRequestFields from a JSON string"""
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
        """Create an instance of OpenPaymentMethodTypeRequestFields from a dict"""
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
            "checksum": obj.get("checksum"),
            "defaultValue": obj.get("defaultValue"),
            "description": obj.get("description"),
            "editable": obj.get("editable"),
            "index": obj.get("index"),
            "label": obj.get("label"),
            "maxLength": obj.get("maxLength"),
            "minLength": obj.get("minLength"),
            "name": obj.get("name"),
            "representer": obj.get("representer"),
            "required": obj.get("required"),
            "type": obj.get("type"),
            "visible": obj.get("visible")
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
