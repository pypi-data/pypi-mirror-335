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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional, Union
from zuora_sdk.models.failed_reason import FailedReason
from zuora_sdk.models.payment_schedule_billing_document import PaymentScheduleBillingDocument
from zuora_sdk.models.payment_schedule_item import PaymentScheduleItem
from zuora_sdk.models.payment_schedule_payment_option_fields import PaymentSchedulePaymentOptionFields
from typing import Optional, Set
from typing_extensions import Self

class PaymentScheduleResponse(BaseModel):
    """
    PaymentScheduleResponse
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

    account_id: Optional[StrictStr] = Field(default=None, description="ID of the account that owns the payment schedule. ", alias="accountId")
    account_number: Optional[StrictStr] = Field(default=None, description="Number of the account that owns the payment schedule. ", alias="accountNumber")
    billing_document: Optional[PaymentScheduleBillingDocument] = Field(default=None, alias="billingDocument")
    cancel_date: Optional[StrictStr] = Field(default=None, description="The date when the payment schedule item was cancelled. ", alias="cancelDate")
    cancelled_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the user who cancel the payment schedule item. ", alias="cancelledById")
    cancelled_on: Optional[StrictStr] = Field(default=None, description="The date and time when the payment schedule item was cancelled. ", alias="cancelledOn")
    created_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the user who created this payment schedule. ", alias="createdById")
    created_date: Optional[StrictStr] = Field(default=None, description="The date and time the payment schedule is created. ", alias="createdDate")
    description: Optional[StrictStr] = Field(default=None, description="The description of the payment schedule. ")
    id: Optional[StrictStr] = Field(default=None, description="ID of the payment schedule. ")
    is_custom: Optional[StrictBool] = Field(default=None, description="Indicates if the payment schedule is a custom payment schedule. ", alias="isCustom")
    items: Optional[List[PaymentScheduleItem]] = Field(default=None, description="Container for payment schedule items. ")
    next_payment_date: Optional[StrictStr] = Field(default=None, description="The date the next payment will be processed. ", alias="nextPaymentDate")
    occurrences: Optional[StrictInt] = Field(default=None, description="The number of payment schedule items that are created by this payment schedule. ")
    payment_option: Optional[List[PaymentSchedulePaymentOptionFields]] = Field(default=None, description="Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.  `paymentOption` of the payment schedule takes precedence over `paymentOption` of the payment schedule item.  This field is only available if `zuora-version` is set to `337.0` or later. ", alias="paymentOption")
    payment_schedule_number: Optional[StrictStr] = Field(default=None, description="Number of the payment schedule. ", alias="paymentScheduleNumber")
    period: Optional[StrictStr] = Field(default=None, description="For recurring payment schedule only. The period of payment generation. Available values include: `Monthly`, `Weekly`, `BiWeekly`.  Return `null` for custom payment schedules. ")
    prepayment: Optional[StrictBool] = Field(default=None, description="Indicates whether the payments created by the payment schedule are used as a reserved payment. This field is available only if the prepaid cash drawdown permission is enabled. See [Prepaid Cash with Drawdown](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/JA_Advanced_Consumption_Billing/Prepaid_Cash_with_Drawdown) for more information. ")
    recent_payment_date: Optional[date] = Field(default=None, description="The date the last payment was processed. ", alias="recentPaymentDate")
    run_hour: Optional[StrictInt] = Field(default=None, description="[0,1,2,~,22,23]  At which hour in the day in the tenant’s timezone this payment will be collected.  Return `0` for custom payment schedules. ", alias="runHour")
    standalone: Optional[StrictBool] = Field(default=None, description="Indicates if the payments that the payment schedule created are standalone payments. ")
    start_date: Optional[StrictStr] = Field(default=None, description="The date when the first payment of this payment schedule is proccessed. ", alias="startDate")
    status: Optional[StrictStr] = Field(default=None, description="The status of the payment schedule.  - Active: There is still payment schedule item to process. - Canceled: After a payment schedule is canceled by the user, the schedule is marked as `Canceled`. - Completed: After all payment schedule items are processed, the schedule is marked as `Completed`. ")
    success: Optional[StrictBool] = Field(default=None, description="Indicates whether the call succeeded. ")
    total_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total amount that will be collected by the payment schedule. ", alias="totalAmount")
    total_payments_errored: Optional[StrictInt] = Field(default=None, description="The number of errored payments. ", alias="totalPaymentsErrored")
    total_payments_processed: Optional[StrictInt] = Field(default=None, description="The number of processed payments. ", alias="totalPaymentsProcessed")
    updated_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the user who last updated this payment schedule. ", alias="updatedById")
    updated_date: Optional[StrictStr] = Field(default=None, description="The date and time the payment schedule is last updated. ", alias="updatedDate")
    process_id: Optional[StrictStr] = Field(default=None, description="The Id of the process that handle the operation. ", alias="processId")
    request_id: Optional[StrictStr] = Field(default=None, description="Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution. ", alias="requestId")
    reasons: Optional[List[FailedReason]] = None
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["accountId", "accountNumber", "billingDocument", "cancelDate", "cancelledById", "cancelledOn", "createdById", "createdDate", "description", "id", "isCustom", "items", "nextPaymentDate", "occurrences", "paymentOption", "paymentScheduleNumber", "period", "prepayment", "recentPaymentDate", "runHour", "standalone", "startDate", "status", "success", "totalAmount", "totalPaymentsErrored", "totalPaymentsProcessed", "updatedById", "updatedDate", "processId", "requestId", "reasons"]

    @field_validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['Active', 'Canceled', 'Completed']):
            raise ValueError("must be one of enum values ('Active', 'Canceled', 'Completed')")
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
        """Create an instance of PaymentScheduleResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of billing_document
        if self.billing_document:
            _dict['billingDocument'] = self.billing_document.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in items (list)
        _items = []
        if self.items:
            for _item_items in self.items:
                if _item_items:
                    _items.append(_item_items.to_dict())
            _dict['items'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in payment_option (list)
        _items = []
        if self.payment_option:
            for _item_payment_option in self.payment_option:
                if _item_payment_option:
                    _items.append(_item_payment_option.to_dict())
            _dict['paymentOption'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in reasons (list)
        _items = []
        if self.reasons:
            for _item_reasons in self.reasons:
                if _item_reasons:
                    _items.append(_item_reasons.to_dict())
            _dict['reasons'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of PaymentScheduleResponse from a dict"""
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
            "billingDocument": PaymentScheduleBillingDocument.from_dict(obj["billingDocument"]) if obj.get("billingDocument") is not None else None,
            "cancelDate": obj.get("cancelDate"),
            "cancelledById": obj.get("cancelledById"),
            "cancelledOn": obj.get("cancelledOn"),
            "createdById": obj.get("createdById"),
            "createdDate": obj.get("createdDate"),
            "description": obj.get("description"),
            "id": obj.get("id"),
            "isCustom": obj.get("isCustom"),
            "items": [PaymentScheduleItem.from_dict(_item) for _item in obj["items"]] if obj.get("items") is not None else None,
            "nextPaymentDate": obj.get("nextPaymentDate"),
            "occurrences": obj.get("occurrences"),
            "paymentOption": [PaymentSchedulePaymentOptionFields.from_dict(_item) for _item in obj["paymentOption"]] if obj.get("paymentOption") is not None else None,
            "paymentScheduleNumber": obj.get("paymentScheduleNumber"),
            "period": obj.get("period"),
            "prepayment": obj.get("prepayment"),
            "recentPaymentDate": obj.get("recentPaymentDate"),
            "runHour": obj.get("runHour"),
            "standalone": obj.get("standalone"),
            "startDate": obj.get("startDate"),
            "status": obj.get("status"),
            "success": obj.get("success"),
            "totalAmount": obj.get("totalAmount"),
            "totalPaymentsErrored": obj.get("totalPaymentsErrored"),
            "totalPaymentsProcessed": obj.get("totalPaymentsProcessed"),
            "updatedById": obj.get("updatedById"),
            "updatedDate": obj.get("updatedDate"),
            "processId": obj.get("processId"),
            "requestId": obj.get("requestId"),
            "reasons": [FailedReason.from_dict(_item) for _item in obj["reasons"]] if obj.get("reasons") is not None else None
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
