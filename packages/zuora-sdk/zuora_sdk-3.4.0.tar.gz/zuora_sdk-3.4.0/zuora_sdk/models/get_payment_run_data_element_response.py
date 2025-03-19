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

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from zuora_sdk.models.get_payment_run_data_transaction_element_response import GetPaymentRunDataTransactionElementResponse
from typing import Optional, Set
from typing_extensions import Self

class GetPaymentRunDataElementResponse(BaseModel):
    """
    GetPaymentRunDataElementResponse
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

    account_id: Optional[StrictStr] = Field(default=None, description="The customer account ID specified in the `data` field when creating the payment run. ", alias="accountId")
    account_number: Optional[StrictStr] = Field(default=None, description="The customer account number specified in the `data` field when creating the payment run. ", alias="accountNumber")
    amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ")
    amount_collected: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount that is collected. ", alias="amountCollected")
    amount_to_collect: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount to be collected. ", alias="amountToCollect")
    comment: Optional[StrictStr] = Field(default=None, description="The comment specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ")
    currency: Optional[StrictStr] = Field(default=None, description="This field is only available if support for standalone payments is enabled.  The currency of the standalone payment. The currency of the standalone payment can be different from the payment currency defined in the customer account settings. ")
    document_id: Optional[StrictStr] = Field(default=None, description="The billing document ID specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ", alias="documentId")
    document_number: Optional[StrictStr] = Field(default=None, description="The billing document number specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ", alias="documentNumber")
    document_type: Optional[StrictStr] = Field(default=None, description="The billing document type specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ", alias="documentType")
    error_code: Optional[StrictStr] = Field(default=None, description="The error code of the response. ", alias="errorCode")
    error_message: Optional[StrictStr] = Field(default=None, description="The detailed information of the error response. ", alias="errorMessage")
    payment_gateway_id: Optional[StrictStr] = Field(default=None, description="The payment gateway ID specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ", alias="paymentGatewayId")
    payment_method_id: Optional[StrictStr] = Field(default=None, description="The payment method ID specified in the `data` field when creating the payment run. `null` is returned if it was not specified. ", alias="paymentMethodId")
    result: Optional[StrictStr] = Field(default=None, description="Indicates whether the data is processed successfully or not. ")
    standalone: Optional[StrictBool] = Field(default=None, description="This field is only available if the support for standalone payment is enabled.  The value `true` indicates this is a standalone payment that is created and processed in Zuora through Zuora gateway integration but will be settled outside of Zuora. No settlement data will be created. The standalone payment cannot be applied, unapplied, or transferred. ")
    transactions: Optional[List[GetPaymentRunDataTransactionElementResponse]] = Field(default=None, description="Container for transactions that apply to the current request. Each element contains an array of the settlement/payment applied to the record. ")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["accountId", "accountNumber", "amount", "amountCollected", "amountToCollect", "comment", "currency", "documentId", "documentNumber", "documentType", "errorCode", "errorMessage", "paymentGatewayId", "paymentMethodId", "result", "standalone", "transactions"]

    @field_validator('document_type')
    def document_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Invoice', 'DebitMemo']):
            raise ValueError("must be one of enum values ('Invoice', 'DebitMemo')")
        return value

    @field_validator('result')
    def result_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Processed', 'Error']):
            raise ValueError("must be one of enum values ('Processed', 'Error')")
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
        """Create an instance of GetPaymentRunDataElementResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in transactions (list)
        _items = []
        if self.transactions:
            for _item_transactions in self.transactions:
                if _item_transactions:
                    _items.append(_item_transactions.to_dict())
            _dict['transactions'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of GetPaymentRunDataElementResponse from a dict"""
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
            "amount": obj.get("amount"),
            "amountCollected": obj.get("amountCollected"),
            "amountToCollect": obj.get("amountToCollect"),
            "comment": obj.get("comment"),
            "currency": obj.get("currency"),
            "documentId": obj.get("documentId"),
            "documentNumber": obj.get("documentNumber"),
            "documentType": obj.get("documentType"),
            "errorCode": obj.get("errorCode"),
            "errorMessage": obj.get("errorMessage"),
            "paymentGatewayId": obj.get("paymentGatewayId"),
            "paymentMethodId": obj.get("paymentMethodId"),
            "result": obj.get("result"),
            "standalone": obj.get("standalone"),
            "transactions": [GetPaymentRunDataTransactionElementResponse.from_dict(_item) for _item in obj["transactions"]] if obj.get("transactions") is not None else None
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
