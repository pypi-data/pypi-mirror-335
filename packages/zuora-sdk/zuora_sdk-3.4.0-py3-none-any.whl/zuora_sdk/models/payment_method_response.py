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

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from zuora_sdk.models.get_pm_account_holder_info import GetPMAccountHolderInfo
from zuora_sdk.models.payment_method_ach_bank_account_type import PaymentMethodACHBankAccountType
from zuora_sdk.models.payment_method_mandate_info_mandate_status import PaymentMethodMandateInfoMandateStatus
from zuora_sdk.models.payment_method_response_card_bin_info import PaymentMethodResponseCardBinInfo
from zuora_sdk.models.payment_method_response_mandate_info import PaymentMethodResponseMandateInfo
from typing import Optional, Set
from typing_extensions import Self

class PaymentMethodResponse(BaseModel):
    """
    PaymentMethodResponse
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

    iban: Optional[StrictStr] = Field(default=None, description="The International Bank Account Number used to create the SEPA payment method. The value is masked. ", alias="IBAN")
    account_number: Optional[StrictStr] = Field(default=None, description="The number of the customer's bank account and it is masked. ", alias="accountNumber")
    bank_code: Optional[StrictStr] = Field(default=None, description="The sort code or number that identifies the bank. This is also known as the sort code.          ", alias="bankCode")
    bank_transfer_type: Optional[StrictStr] = Field(default=None, description="The type of the Bank Transfer payment method. For example, `SEPA`. ", alias="bankTransferType")
    branch_code: Optional[StrictStr] = Field(default=None, description="The branch code of the bank used for Direct Debit.           ", alias="branchCode")
    business_identification_code: Optional[StrictStr] = Field(default=None, description="The BIC code used for SEPA. The value is masked.        ", alias="businessIdentificationCode")
    identity_number: Optional[StrictStr] = Field(default=None, description="The identity number of the customer. ", alias="identityNumber")
    bank_aba_code: Optional[StrictStr] = Field(default=None, description="The nine-digit routing number or ABA number used by banks. This field is only required if the `type` field is set to `ACH`. ", alias="bankABACode")
    bank_account_name: Optional[StrictStr] = Field(default=None, description="The name of the account holder, which can be either a person or a company. This field is only required if the `type` field is set to `ACH`. ", alias="bankAccountName")
    bank_account_number: Optional[StrictStr] = Field(default=None, description="The bank account number associated with the ACH payment. This field is only required if the `type` field is set to `ACH`. However, for creating tokenized ACH payment methods on  Stripe v2, this field is optional if the `tokens` and `bankAccountMaskNumber` fields are specified. ", alias="bankAccountNumber")
    bank_account_mask_number: Optional[StrictStr] = Field(default=None, description="The masked bank account number associated with the ACH payment. This field is only required if the ACH payment method is created using tokens. ", alias="bankAccountMaskNumber")
    bank_account_type: Optional[StrictStr] = Field(default=None, alias="bankAccountType")
    bank_name: Optional[StrictStr] = Field(default=None, description="The name of the bank where the ACH payment account is held. This field is only required if the `type` field is set to `ACH`.  When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify a dummy value. ", alias="bankName")
    card_number: Optional[StrictStr] = Field(default=None, description="The masked credit card number.  When `cardNumber` is `null`, the following fields will not be returned:   - `expirationMonth`   - `expirationYear`   - `accountHolderInfo` ", alias="cardNumber")
    expiration_month: Optional[StrictInt] = Field(default=None, description="One or two digits expiration month (1-12).          ", alias="expirationMonth")
    expiration_year: Optional[StrictInt] = Field(default=None, description="Four-digit expiration year. ", alias="expirationYear")
    security_code: Optional[StrictStr] = Field(default=None, description="The CVV or CVV2 security code for the credit card or debit card.             Only required if changing expirationMonth, expirationYear, or cardHolderName.             To ensure PCI compliance, this value isn''t stored and can''t be queried.                   ", alias="securityCode")
    baid: Optional[StrictStr] = Field(default=None, description="ID of a PayPal billing agreement. For example, I-1TJ3GAGG82Y9. ", alias="BAID")
    email: Optional[StrictStr] = Field(default=None, description="Email address associated with the PayPal payment method.  ")
    preapproval_key: Optional[StrictStr] = Field(default=None, description="The PayPal preapproval key. ", alias="preapprovalKey")
    google_bin: Optional[StrictStr] = Field(default=None, description="This field is only available for Google Pay payment methods. ", alias="googleBIN")
    google_card_number: Optional[StrictStr] = Field(default=None, description="This field is only available for Google Pay payment methods. ", alias="googleCardNumber")
    google_card_type: Optional[StrictStr] = Field(default=None, description="This field is only available for Google Pay payment methods.  For Google Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. ", alias="googleCardType")
    google_expiry_date: Optional[StrictStr] = Field(default=None, description="This field is only available for Google Pay payment methods. ", alias="googleExpiryDate")
    google_gateway_token: Optional[StrictStr] = Field(default=None, description="This field is only available for Google Pay payment methods. ", alias="googleGatewayToken")
    apple_bin: Optional[StrictStr] = Field(default=None, description="This field is only available for Apple Pay payment methods. ", alias="appleBIN")
    apple_card_number: Optional[StrictStr] = Field(default=None, description="This field is only available for Apple Pay payment methods. ", alias="appleCardNumber")
    apple_card_type: Optional[StrictStr] = Field(default=None, description="This field is only available for Apple Pay payment methods.  For Apple Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. ", alias="appleCardType")
    apple_expiry_date: Optional[StrictStr] = Field(default=None, description="This field is only available for Apple Pay payment methods. ", alias="appleExpiryDate")
    apple_gateway_token: Optional[StrictStr] = Field(default=None, description="This field is only available for Apple Pay payment methods. ", alias="appleGatewayToken")
    account_holder_info: Optional[GetPMAccountHolderInfo] = Field(default=None, alias="accountHolderInfo")
    bank_identification_number: Optional[StrictStr] = Field(default=None, description="The first six or eight digits of the payment method's number, such as the credit card number or account number. Banks use this number to identify a payment method. ", alias="bankIdentificationNumber")
    card_bin_info: Optional[PaymentMethodResponseCardBinInfo] = Field(default=None, alias="cardBinInfo")
    created_by: Optional[StrictStr] = Field(default=None, description="ID of the user who created this payment method.", alias="createdBy")
    created_on: Optional[datetime] = Field(default=None, description="The date and time when the payment method was created, in `yyyy-mm-dd hh:mm:ss` format. ", alias="createdOn")
    credit_card_mask_number: Optional[StrictStr] = Field(default=None, description="The masked credit card number, such as: ``` *********1112 ``` ", alias="creditCardMaskNumber")
    credit_card_type: Optional[StrictStr] = Field(default=None, description="The type of the credit card or debit card.  Possible values include `Visa`, `MasterCard`, `AmericanExpress`, `Discover`, `JCB`, and `Diners`. For more information about credit card types supported by different payment gateways, see [Supported Payment Gateways](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways).  **Note:** This field is only returned for the Credit Card and Debit Card payment types. ", alias="creditCardType")
    device_session_id: Optional[StrictStr] = Field(default=None, description="The session ID of the user when the `PaymentMethod` was created or updated. ", alias="deviceSessionId")
    existing_mandate: Optional[PaymentMethodMandateInfoMandateStatus] = Field(default=None, alias="existingMandate")
    id: Optional[StrictStr] = Field(default=None, description="The payment method ID. ")
    ip_address: Optional[StrictStr] = Field(default=None, description="The IP address of the user when the payment method was created or updated. ", alias="ipAddress")
    is_default: Optional[StrictBool] = Field(default=None, description="Indicates whether this payment method is the default payment method for the account. ", alias="isDefault")
    last_failed_sale_transaction_date: Optional[datetime] = Field(default=None, description="The date of the last failed attempt to collect payment with this payment method. ", alias="lastFailedSaleTransactionDate")
    last_transaction: Optional[StrictStr] = Field(default=None, description="ID of the last transaction of this payment method.", alias="lastTransaction")
    last_transaction_time: Optional[datetime] = Field(default=None, description="The time when the last transaction of this payment method happened.", alias="lastTransactionTime")
    mandate_info: Optional[PaymentMethodResponseMandateInfo] = Field(default=None, alias="mandateInfo")
    max_consecutive_payment_failures: Optional[StrictInt] = Field(default=None, description="The number of allowable consecutive failures Zuora attempts with the payment method before stopping. ", alias="maxConsecutivePaymentFailures")
    num_consecutive_failures: Optional[StrictInt] = Field(default=None, description="The number of consecutive failed payments for this payment method. It is reset to `0` upon successful payment.  ", alias="numConsecutiveFailures")
    payment_retry_window: Optional[StrictInt] = Field(default=None, description="The retry interval setting, which prevents making a payment attempt if the last failed attempt was within the last specified number of hours. ", alias="paymentRetryWindow")
    second_token_id: Optional[StrictStr] = Field(default=None, description="A gateway unique identifier that replaces sensitive payment method data.  **Note:** This field is only returned for the Credit Card Reference Transaction payment type. ", alias="secondTokenId")
    status: Optional[StrictStr] = Field(default=None, description="The status of the payment method. ")
    token_id: Optional[StrictStr] = Field(default=None, description="A gateway unique identifier that replaces sensitive payment method data or represents a gateway's unique customer profile.  **Note:** This field is only returned for the Credit Card Reference Transaction payment type. ", alias="tokenId")
    total_number_of_error_payments: Optional[StrictInt] = Field(default=None, description="The number of error payments that used this payment method. ", alias="totalNumberOfErrorPayments")
    total_number_of_processed_payments: Optional[StrictInt] = Field(default=None, description="The number of successful payments that used this payment method. ", alias="totalNumberOfProcessedPayments")
    type: Optional[StrictStr] = Field(default=None, description="The type of the payment method. For example, `CreditCard`. ")
    updated_by: Optional[StrictStr] = Field(default=None, description="ID of the user who made the last update to this payment method.", alias="updatedBy")
    updated_on: Optional[datetime] = Field(default=None, description="The last date and time when the payment method was updated, in `yyyy-mm-dd hh:mm:ss` format. ", alias="updatedOn")
    use_default_retry_rule: Optional[StrictBool] = Field(default=None, description="Indicates whether this payment method uses the default retry rules configured in the Zuora Payments settings. ", alias="useDefaultRetryRule")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["IBAN", "accountNumber", "bankCode", "bankTransferType", "branchCode", "businessIdentificationCode", "identityNumber", "bankABACode", "bankAccountName", "bankAccountNumber", "bankAccountMaskNumber", "bankAccountType", "bankName", "cardNumber", "expirationMonth", "expirationYear", "securityCode", "BAID", "email", "preapprovalKey", "googleBIN", "googleCardNumber", "googleCardType", "googleExpiryDate", "googleGatewayToken", "appleBIN", "appleCardNumber", "appleCardType", "appleExpiryDate", "appleGatewayToken", "accountHolderInfo", "bankIdentificationNumber", "cardBinInfo", "createdBy", "createdOn", "creditCardMaskNumber", "creditCardType", "deviceSessionId", "existingMandate", "id", "ipAddress", "isDefault", "lastFailedSaleTransactionDate", "lastTransaction", "lastTransactionTime", "mandateInfo", "maxConsecutivePaymentFailures", "numConsecutiveFailures", "paymentRetryWindow", "secondTokenId", "status", "tokenId", "totalNumberOfErrorPayments", "totalNumberOfProcessedPayments", "type", "updatedBy", "updatedOn", "useDefaultRetryRule"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Active', 'Closed', 'Scrubbed']):
            raise ValueError("must be one of enum values ('Active', 'Closed', 'Scrubbed')")
        return value

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
        """Create an instance of PaymentMethodResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of account_holder_info
        if self.account_holder_info:
            _dict['accountHolderInfo'] = self.account_holder_info.to_dict()
        # override the default output from pydantic by calling `to_dict()` of card_bin_info
        if self.card_bin_info:
            _dict['cardBinInfo'] = self.card_bin_info.to_dict()
        # override the default output from pydantic by calling `to_dict()` of mandate_info
        if self.mandate_info:
            _dict['mandateInfo'] = self.mandate_info.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PaymentMethodResponse from a dict"""
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
            "IBAN": obj.get("IBAN"),
            "accountNumber": obj.get("accountNumber"),
            "bankCode": obj.get("bankCode"),
            "bankTransferType": obj.get("bankTransferType"),
            "branchCode": obj.get("branchCode"),
            "businessIdentificationCode": obj.get("businessIdentificationCode"),
            "identityNumber": obj.get("identityNumber"),
            "bankABACode": obj.get("bankABACode"),
            "bankAccountName": obj.get("bankAccountName"),
            "bankAccountNumber": obj.get("bankAccountNumber"),
            "bankAccountMaskNumber": obj.get("bankAccountMaskNumber"),
            "bankAccountType": obj.get("bankAccountType"),
            "bankName": obj.get("bankName"),
            "cardNumber": obj.get("cardNumber"),
            "expirationMonth": obj.get("expirationMonth"),
            "expirationYear": obj.get("expirationYear"),
            "securityCode": obj.get("securityCode"),
            "BAID": obj.get("BAID"),
            "email": obj.get("email"),
            "preapprovalKey": obj.get("preapprovalKey"),
            "googleBIN": obj.get("googleBIN"),
            "googleCardNumber": obj.get("googleCardNumber"),
            "googleCardType": obj.get("googleCardType"),
            "googleExpiryDate": obj.get("googleExpiryDate"),
            "googleGatewayToken": obj.get("googleGatewayToken"),
            "appleBIN": obj.get("appleBIN"),
            "appleCardNumber": obj.get("appleCardNumber"),
            "appleCardType": obj.get("appleCardType"),
            "appleExpiryDate": obj.get("appleExpiryDate"),
            "appleGatewayToken": obj.get("appleGatewayToken"),
            "accountHolderInfo": GetPMAccountHolderInfo.from_dict(obj["accountHolderInfo"]) if obj.get("accountHolderInfo") is not None else None,
            "bankIdentificationNumber": obj.get("bankIdentificationNumber"),
            "cardBinInfo": PaymentMethodResponseCardBinInfo.from_dict(obj["cardBinInfo"]) if obj.get("cardBinInfo") is not None else None,
            "createdBy": obj.get("createdBy"),
            "createdOn": obj.get("createdOn"),
            "creditCardMaskNumber": obj.get("creditCardMaskNumber"),
            "creditCardType": obj.get("creditCardType"),
            "deviceSessionId": obj.get("deviceSessionId"),
            "existingMandate": obj.get("existingMandate"),
            "id": obj.get("id"),
            "ipAddress": obj.get("ipAddress"),
            "isDefault": obj.get("isDefault"),
            "lastFailedSaleTransactionDate": obj.get("lastFailedSaleTransactionDate"),
            "lastTransaction": obj.get("lastTransaction"),
            "lastTransactionTime": obj.get("lastTransactionTime"),
            "mandateInfo": PaymentMethodResponseMandateInfo.from_dict(obj["mandateInfo"]) if obj.get("mandateInfo") is not None else None,
            "maxConsecutivePaymentFailures": obj.get("maxConsecutivePaymentFailures"),
            "numConsecutiveFailures": obj.get("numConsecutiveFailures"),
            "paymentRetryWindow": obj.get("paymentRetryWindow"),
            "secondTokenId": obj.get("secondTokenId"),
            "status": obj.get("status"),
            "tokenId": obj.get("tokenId"),
            "totalNumberOfErrorPayments": obj.get("totalNumberOfErrorPayments"),
            "totalNumberOfProcessedPayments": obj.get("totalNumberOfProcessedPayments"),
            "type": obj.get("type"),
            "updatedBy": obj.get("updatedBy"),
            "updatedOn": obj.get("updatedOn"),
            "useDefaultRetryRule": obj.get("useDefaultRetryRule")
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
