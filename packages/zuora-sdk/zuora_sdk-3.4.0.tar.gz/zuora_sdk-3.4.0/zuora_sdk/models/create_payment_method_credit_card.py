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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from zuora_sdk.models.create_payment_method_cardholder_info import CreatePaymentMethodCardholderInfo
from typing import Optional, Set
from typing_extensions import Self

class CreatePaymentMethodCreditCard(BaseModel):
    """
    CreatePaymentMethodCreditCard
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

    card_holder_info: Optional[CreatePaymentMethodCardholderInfo] = Field(default=None, alias="cardHolderInfo")
    card_number: Optional[StrictStr] = Field(default=None, description="Credit card number. This field is required if `type` is set to `CreditCard`. However, for creating tokenized credit card payment methods,  this field is optional if the `tokens` and `cardMaskNumber` fields are specified. ", alias="cardNumber")
    card_mask_number: Optional[StrictStr] = Field(default=None, description="The masked card number associated with the credit card payment. This field is only required if the credit card payment method is created using tokens.  ", alias="cardMaskNumber")
    card_type: Optional[StrictStr] = Field(default=None, description="The type of the credit card. This field is required if `type` is set to `CreditCard`.  Possible values include `Visa`, `MasterCard`, `AmericanExpress`, `Discover`, `JCB`, and `Diners`. For more information about credit card types supported by different payment gateways, see [Supported Payment Gateways](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways). ", alias="cardType")
    check_duplicated: Optional[StrictBool] = Field(default=None, description="Indicates whether the duplication check is performed when you create a new credit card payment method. The default value is `false`.  With this field set to `true`, Zuora will check all active payment methods associated with the same billing account to ensure that no duplicate credit card payment methods are created. An error is returned if a duplicate payment method is found.          The following fields are used for the duplication check:   - `cardHolderName`   - `expirationMonth`   - `expirationYear`   - `creditCardMaskNumber`. It is the masked credit card number generated by Zuora. For example:     ```     ************1234     ``` ", alias="checkDuplicated")
    expiration_month: Optional[StrictInt] = Field(default=None, description="One or two digit expiration month (1-12) of the credit card. This field is required if `type` is set to `CreditCard`. However, for creating tokenized credit card payment methods,  this field is optional if the `tokens` and `cardMaskNumber` fields are specified. ", alias="expirationMonth")
    expiration_year: Optional[StrictInt] = Field(default=None, description="Four-digit expiration year of the credit card. This field is required if `type` is set to `CreditCard`. However, for creating tokenized credit card payment methods,  this field is optional if the `tokens` and `cardMaskNumber` fields are specified. ", alias="expirationYear")
    mit_consent_agreement_ref: Optional[Annotated[str, Field(strict=True, max_length=128)]] = Field(default=None, description="Specifies your reference for the stored credential consent agreement that you have established with the customer. Only applicable if you set the `mitProfileAction` field. ", alias="mitConsentAgreementRef")
    mit_consent_agreement_src: Optional[StrictStr] = Field(default=None, alias="mitConsentAgreementSrc")
    mit_network_transaction_id: Optional[Annotated[str, Field(strict=True, max_length=128)]] = Field(default=None, description="Specifies the ID of a network transaction. Only applicable if you set the `mitProfileAction` field to `Persist`. ", alias="mitNetworkTransactionId")
    mit_profile_action: Optional[StrictStr] = Field(default=None, alias="mitProfileAction")
    mit_profile_agreed_on: Optional[date] = Field(default=None, description="The date on which the profile is agreed. The date format is `yyyy-mm-dd`. ", alias="mitProfileAgreedOn")
    mit_profile_type: Optional[StrictStr] = Field(default=None, alias="mitProfileType")
    security_code: Optional[StrictStr] = Field(default=None, description="CVV or CVV2 security code of the credit card.  To ensure PCI compliance, this value is not stored and cannot be queried. ", alias="securityCode")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["cardHolderInfo", "cardNumber", "cardMaskNumber", "cardType", "checkDuplicated", "expirationMonth", "expirationYear", "mitConsentAgreementRef", "mitConsentAgreementSrc", "mitNetworkTransactionId", "mitProfileAction", "mitProfileAgreedOn", "mitProfileType", "securityCode"]

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
        """Create an instance of CreatePaymentMethodCreditCard from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of card_holder_info
        if self.card_holder_info:
            _dict['cardHolderInfo'] = self.card_holder_info.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CreatePaymentMethodCreditCard from a dict"""
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
            "cardHolderInfo": CreatePaymentMethodCardholderInfo.from_dict(obj["cardHolderInfo"]) if obj.get("cardHolderInfo") is not None else None,
            "cardNumber": obj.get("cardNumber"),
            "cardMaskNumber": obj.get("cardMaskNumber"),
            "cardType": obj.get("cardType"),
            "checkDuplicated": obj.get("checkDuplicated"),
            "expirationMonth": obj.get("expirationMonth"),
            "expirationYear": obj.get("expirationYear"),
            "mitConsentAgreementRef": obj.get("mitConsentAgreementRef"),
            "mitConsentAgreementSrc": obj.get("mitConsentAgreementSrc"),
            "mitNetworkTransactionId": obj.get("mitNetworkTransactionId"),
            "mitProfileAction": obj.get("mitProfileAction"),
            "mitProfileAgreedOn": obj.get("mitProfileAgreedOn"),
            "mitProfileType": obj.get("mitProfileType"),
            "securityCode": obj.get("securityCode")
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
