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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class Contact(BaseModel):
    """
    Container for response about the contact. 
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

    id: Optional[StrictStr] = Field(default=None, description="The ID of the contact. ")
    account_id: Optional[StrictStr] = Field(default=None, description="The ID of the account associated with the contact. ", alias="accountId")
    account_number: Optional[StrictStr] = Field(default=None, description="The number of the customer account associated with the contact. ", alias="accountNumber")
    address1: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The first line of the contact's address, which is often a street address or business name. ")
    address2: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The second line of the contact's address. ")
    city: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="The city of the contact's address. ")
    contact_description: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="A description for the contact. ", alias="contactDescription")
    country: Optional[Annotated[str, Field(strict=True, max_length=64)]] = Field(default=None, description="The country of the contact's address. ")
    county: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The county. May optionally be used by Zuora Tax to calculate county tax. ")
    fax: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="The contact's fax number. ")
    first_name: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The contact's first name. ", alias="firstName")
    home_phone: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="The contact's home phone number. ", alias="homePhone")
    last_name: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The contact's last name. ", alias="lastName")
    mobile_phone: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The mobile phone number of the contact. ", alias="mobilePhone")
    nickname: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="A nickname for the contact. ")
    other_phone: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="An additional phone number for the contact. ", alias="otherPhone")
    other_phone_type: Optional[StrictStr] = Field(default=None, alias="otherPhoneType")
    personal_email: Optional[Annotated[str, Field(strict=True, max_length=80)]] = Field(default=None, description="The contact's personal email address. ", alias="personalEmail")
    state: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="The state or province of the contact's address. ")
    success: Optional[StrictBool] = Field(default=None, description="Returns `true` if the request was processed successfully. ")
    tax_region: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="If using Zuora Tax, a region string as optionally defined in your tax rules. Not required. ", alias="taxRegion")
    work_email: Optional[Annotated[str, Field(strict=True, max_length=80)]] = Field(default=None, description="The contact's business email address. ", alias="workEmail")
    work_phone: Optional[Annotated[str, Field(strict=True, max_length=40)]] = Field(default=None, description="The contact's business phone number. ", alias="workPhone")
    zip_code: Optional[Annotated[str, Field(strict=True, max_length=20)]] = Field(default=None, description="The zip code for the contact's address. ", alias="zipCode")
    postal_code: Optional[Annotated[str, Field(strict=True, max_length=20)]] = Field(default=None, description="Same as zipCode, used in get subscription billto, soldto contact info. ", alias="postalCode")
    as_bill_to: Optional[StrictBool] = Field(default=None, description="Indicates the contact can as a bill to. Need Permission 'ShipToContactSupport' ", alias="asBillTo")
    as_sold_to: Optional[StrictBool] = Field(default=None, description="Indicates the contact can as a sold to. Need Permission 'ShipToContactSupport' ", alias="asSoldTo")
    as_ship_to: Optional[StrictBool] = Field(default=None, description="Indicates the contact can as a ship to. Need Permission 'ShipToContactSupport' ", alias="asShipTo")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["id", "accountId", "accountNumber", "address1", "address2", "city", "contactDescription", "country", "county", "fax", "firstName", "homePhone", "lastName", "mobilePhone", "nickname", "otherPhone", "otherPhoneType", "personalEmail", "state", "success", "taxRegion", "workEmail", "workPhone", "zipCode", "postalCode", "asBillTo", "asSoldTo", "asShipTo"]

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
        """Create an instance of Contact from a JSON string"""
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
        """Create an instance of Contact from a dict"""
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
            "id": obj.get("id"),
            "accountId": obj.get("accountId"),
            "accountNumber": obj.get("accountNumber"),
            "address1": obj.get("address1"),
            "address2": obj.get("address2"),
            "city": obj.get("city"),
            "contactDescription": obj.get("contactDescription"),
            "country": obj.get("country"),
            "county": obj.get("county"),
            "fax": obj.get("fax"),
            "firstName": obj.get("firstName"),
            "homePhone": obj.get("homePhone"),
            "lastName": obj.get("lastName"),
            "mobilePhone": obj.get("mobilePhone"),
            "nickname": obj.get("nickname"),
            "otherPhone": obj.get("otherPhone"),
            "otherPhoneType": obj.get("otherPhoneType"),
            "personalEmail": obj.get("personalEmail"),
            "state": obj.get("state"),
            "success": obj.get("success"),
            "taxRegion": obj.get("taxRegion"),
            "workEmail": obj.get("workEmail"),
            "workPhone": obj.get("workPhone"),
            "zipCode": obj.get("zipCode"),
            "postalCode": obj.get("postalCode"),
            "asBillTo": obj.get("asBillTo"),
            "asSoldTo": obj.get("asSoldTo"),
            "asShipTo": obj.get("asShipTo")
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
