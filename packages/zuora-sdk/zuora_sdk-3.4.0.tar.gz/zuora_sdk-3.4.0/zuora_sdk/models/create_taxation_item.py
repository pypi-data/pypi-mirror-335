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
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class CreateTaxationItem(BaseModel):
    """
    CreateTaxationItem
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

    exempt_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The calculated tax amount excluded due to the exemption.", alias="exemptAmount")
    jurisdiction: Optional[StrictStr] = Field(default=None, description="The jurisdiction that applies the tax or VAT. This value is typically a state, province, county, or city.")
    location_code: Optional[StrictStr] = Field(default=None, description="The identifier for the location based on the value of the `taxCode` field.", alias="locationCode")
    name: StrictStr = Field(description="The name of taxation.")
    tax_amount: Union[StrictFloat, StrictInt] = Field(description="The amount of the taxation item in the invoice item.", alias="taxAmount")
    tax_code: StrictStr = Field(description="The tax code identifies which tax rules and tax rates to apply to a specific invoice item.", alias="taxCode")
    tax_code_description: Optional[StrictStr] = Field(default=None, description="The description of the tax code.", alias="taxCodeDescription")
    tax_date: date = Field(description="The date that the tax is applied to the invoice item, in `yyyy-mm-dd` format.", alias="taxDate")
    tax_mode: StrictStr = Field(alias="taxMode")
    tax_rate: Decimal = Field(description="The tax rate applied to the invoice item.", alias="taxRate")
    tax_rate_description: Optional[StrictStr] = Field(default=None, description="The description of the tax rate.", alias="taxRateDescription")
    tax_rate_type: StrictStr = Field(alias="taxRateType")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["exemptAmount", "jurisdiction", "locationCode", "name", "taxAmount", "taxCode", "taxCodeDescription", "taxDate", "taxMode", "taxRate", "taxRateDescription", "taxRateType"]

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
        """Create an instance of CreateTaxationItem from a JSON string"""
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
        """Create an instance of CreateTaxationItem from a dict"""
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
            "exemptAmount": obj.get("exemptAmount"),
            "jurisdiction": obj.get("jurisdiction"),
            "locationCode": obj.get("locationCode"),
            "name": obj.get("name"),
            "taxAmount": obj.get("taxAmount"),
            "taxCode": obj.get("taxCode"),
            "taxCodeDescription": obj.get("taxCodeDescription"),
            "taxDate": obj.get("taxDate"),
            "taxMode": obj.get("taxMode"),
            "taxRate": obj.get("taxRate"),
            "taxRateDescription": obj.get("taxRateDescription"),
            "taxRateType": obj.get("taxRateType")
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
