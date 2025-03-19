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
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from typing import Optional, Set
from typing_extensions import Self

class PaymentMethodResponseMandateInfo(BaseModel):
    """
    The mandate information for the Credit Card, Apple Pay, Google Pay, Credit Card Reference Transaction, ACH, or Bank Transfer payment method.  The following mandate fields are common to all supported payment methods: * `mandateId` * `mandateReason` * `mandateStatus`  The following mandate fields are specific to the ACH and Bank Transfer payment methods: * `mandateReceivedStatus` * `existingMandateStatus` * `mandateCreationDate` * `mandateUpdateDate`  The following mandate fields are specific to the Credit Card, Apple Pay, and Google Pay payment methods: * `mitTransactionId` * `mitProfileAgreedOn` * `mitConsentAgreementRef` * `mitConsentAgreementSrc` * `mitProfileType` * `mitProfileAction` 
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

    existing_mandate_status: Optional[StrictStr] = Field(default=None, alias="existingMandateStatus")
    mandate_creation_date: Optional[date] = Field(default=None, description="The date on which the mandate was created. ", alias="mandateCreationDate")
    mandate_id: Optional[StrictStr] = Field(default=None, description="The mandate ID. ", alias="mandateId")
    mandate_reason: Optional[StrictStr] = Field(default=None, description="The reason of the mandate from the gateway side. ", alias="mandateReason")
    mandate_received_status: Optional[StrictStr] = Field(default=None, alias="mandateReceivedStatus")
    mandate_status: Optional[StrictStr] = Field(default=None, description="The status of the mandate from the gateway side. ", alias="mandateStatus")
    mandate_update_date: Optional[date] = Field(default=None, description="The date on which the mandate was updated. ", alias="mandateUpdateDate")
    mit_consent_agreement_ref: Optional[StrictStr] = Field(default=None, description="Reference for the consent agreement that you have established with the customer.   ", alias="mitConsentAgreementRef")
    mit_consent_agreement_src: Optional[StrictStr] = Field(default=None, alias="mitConsentAgreementSrc")
    mit_profile_action: Optional[StrictStr] = Field(default=None, alias="mitProfileAction")
    mit_profile_agreed_on: Optional[date] = Field(default=None, description="The date on which the stored credential profile is agreed. The date format is `yyyy-mm-dd`. ", alias="mitProfileAgreedOn")
    mit_profile_type: Optional[StrictStr] = Field(default=None, description="Indicates the type of the stored credential profile. If you do not specify the `mitProfileAction` field, Zuora will automatically create a stored credential profile for the payment method, with the default value `Recurring` set to this field. ", alias="mitProfileType")
    mit_transaction_id: Optional[Annotated[str, Field(strict=True, max_length=128)]] = Field(default=None, description="Specifies the ID of the transaction. Only applicable if you set the `mitProfileAction` field to `Persist`. ", alias="mitTransactionId")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["existingMandateStatus", "mandateCreationDate", "mandateId", "mandateReason", "mandateReceivedStatus", "mandateStatus", "mandateUpdateDate", "mitConsentAgreementRef", "mitConsentAgreementSrc", "mitProfileAction", "mitProfileAgreedOn", "mitProfileType", "mitTransactionId"]

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
        """Create an instance of PaymentMethodResponseMandateInfo from a JSON string"""
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
        """Create an instance of PaymentMethodResponseMandateInfo from a dict"""
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
            "existingMandateStatus": obj.get("existingMandateStatus"),
            "mandateCreationDate": obj.get("mandateCreationDate"),
            "mandateId": obj.get("mandateId"),
            "mandateReason": obj.get("mandateReason"),
            "mandateReceivedStatus": obj.get("mandateReceivedStatus"),
            "mandateStatus": obj.get("mandateStatus"),
            "mandateUpdateDate": obj.get("mandateUpdateDate"),
            "mitConsentAgreementRef": obj.get("mitConsentAgreementRef"),
            "mitConsentAgreementSrc": obj.get("mitConsentAgreementSrc"),
            "mitProfileAction": obj.get("mitProfileAction"),
            "mitProfileAgreedOn": obj.get("mitProfileAgreedOn"),
            "mitProfileType": obj.get("mitProfileType"),
            "mitTransactionId": obj.get("mitTransactionId")
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
