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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from zuora_sdk.models.expanded_contact import ExpandedContact
from typing import Optional, Set
from typing_extensions import Self

class ExpandedCreditMemo(BaseModel):
    """
    ExpandedCreditMemo
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

    applied_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="appliedAmount")
    balance: Optional[Union[StrictFloat, StrictInt]] = None
    bill_to_contact_id: Optional[StrictStr] = Field(default=None, alias="billToContactId")
    bill_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, alias="billToContactSnapshotId")
    cancelled_by_id: Optional[StrictStr] = Field(default=None, alias="cancelledById")
    cancelled_on: Optional[StrictStr] = Field(default=None, alias="cancelledOn")
    comments: Optional[StrictStr] = None
    currency: Optional[StrictStr] = None
    discount_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="discountAmount")
    e_invoice_status: Optional[StrictStr] = Field(default=None, alias="eInvoiceStatus")
    e_invoice_file_id: Optional[StrictStr] = Field(default=None, alias="eInvoiceFileId")
    e_invoice_error_code: Optional[StrictStr] = Field(default=None, alias="eInvoiceErrorCode")
    e_invoice_error_message: Optional[StrictStr] = Field(default=None, alias="eInvoiceErrorMessage")
    exchange_rate_date: Optional[date] = Field(default=None, alias="exchangeRateDate")
    exclude_from_auto_apply_rules: Optional[StrictBool] = Field(default=None, alias="excludeFromAutoApplyRules")
    auto_apply_upon_posting: Optional[StrictBool] = Field(default=None, alias="autoApplyUponPosting")
    invoice_group_number: Optional[StrictStr] = Field(default=None, alias="invoiceGroupNumber")
    memo_date: Optional[date] = Field(default=None, alias="memoDate")
    memo_number: Optional[StrictStr] = Field(default=None, alias="memoNumber")
    posted_by_id: Optional[StrictStr] = Field(default=None, alias="postedById")
    posted_on: Optional[StrictStr] = Field(default=None, alias="postedOn")
    reason_code: Optional[StrictStr] = Field(default=None, alias="reasonCode")
    refund_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="refundAmount")
    reversed: Optional[StrictBool] = None
    revenue_impacting: Optional[StrictStr] = Field(default=None, alias="revenueImpacting")
    sequence_set_id: Optional[StrictStr] = Field(default=None, alias="sequenceSetId")
    ship_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, alias="shipToContactSnapshotId")
    sold_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, alias="soldToContactSnapshotId")
    source: Optional[StrictStr] = None
    source_type: Optional[StrictStr] = Field(default=None, alias="sourceType")
    status: Optional[StrictStr] = None
    target_date: Optional[date] = Field(default=None, alias="targetDate")
    tax_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="taxAmount")
    tax_auto_calculation: Optional[StrictBool] = Field(default=None, alias="taxAutoCalculation")
    tax_message: Optional[StrictStr] = Field(default=None, alias="taxMessage")
    tax_status: Optional[StrictStr] = Field(default=None, alias="taxStatus")
    total_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalAmount")
    total_amount_without_tax: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalAmountWithoutTax")
    total_tax_exempt_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, alias="totalTaxExemptAmount")
    transferred_to_accounting: Optional[StrictStr] = Field(default=None, alias="transferredToAccounting")
    invoice_id: Optional[StrictStr] = Field(default=None, alias="invoiceId")
    account_id: Optional[StrictStr] = Field(default=None, alias="accountId")
    id: Optional[StrictStr] = None
    created_by_id: Optional[StrictStr] = Field(default=None, alias="createdById")
    source_id: Optional[StrictStr] = Field(default=None, alias="sourceId")
    created_date: Optional[StrictStr] = Field(default=None, alias="createdDate")
    updated_by_id: Optional[StrictStr] = Field(default=None, alias="updatedById")
    updated_date: Optional[StrictStr] = Field(default=None, alias="updatedDate")
    debit_memo_id: Optional[StrictStr] = Field(default=None, alias="debitMemoId")
    account: Optional[ExpandedAccount] = None
    bill_to_contact: Optional[ExpandedContact] = Field(default=None, alias="billToContact")
    credit_memo_items: Optional[List[ExpandedCreditMemoItem]] = Field(default=None, alias="creditMemoItems")
    credit_memo_applications: Optional[List[ExpandedCreditMemoApplication]] = Field(default=None, alias="creditMemoApplications")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["appliedAmount", "balance", "billToContactId", "billToContactSnapshotId", "cancelledById", "cancelledOn", "comments", "currency", "discountAmount", "eInvoiceStatus", "eInvoiceFileId", "eInvoiceErrorCode", "eInvoiceErrorMessage", "exchangeRateDate", "excludeFromAutoApplyRules", "autoApplyUponPosting", "invoiceGroupNumber", "memoDate", "memoNumber", "postedById", "postedOn", "reasonCode", "refundAmount", "reversed", "revenueImpacting", "sequenceSetId", "shipToContactSnapshotId", "soldToContactSnapshotId", "source", "sourceType", "status", "targetDate", "taxAmount", "taxAutoCalculation", "taxMessage", "taxStatus", "totalAmount", "totalAmountWithoutTax", "totalTaxExemptAmount", "transferredToAccounting", "invoiceId", "accountId", "id", "createdById", "sourceId", "createdDate", "updatedById", "updatedDate", "debitMemoId", "account", "billToContact", "creditMemoItems", "creditMemoApplications"]

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
        """Create an instance of ExpandedCreditMemo from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of account
        if self.account:
            _dict['account'] = self.account.to_dict()
        # override the default output from pydantic by calling `to_dict()` of bill_to_contact
        if self.bill_to_contact:
            _dict['billToContact'] = self.bill_to_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in credit_memo_items (list)
        _items = []
        if self.credit_memo_items:
            for _item_credit_memo_items in self.credit_memo_items:
                if _item_credit_memo_items:
                    _items.append(_item_credit_memo_items.to_dict())
            _dict['creditMemoItems'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in credit_memo_applications (list)
        _items = []
        if self.credit_memo_applications:
            for _item_credit_memo_applications in self.credit_memo_applications:
                if _item_credit_memo_applications:
                    _items.append(_item_credit_memo_applications.to_dict())
            _dict['creditMemoApplications'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ExpandedCreditMemo from a dict"""
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
            "appliedAmount": obj.get("appliedAmount"),
            "balance": obj.get("balance"),
            "billToContactId": obj.get("billToContactId"),
            "billToContactSnapshotId": obj.get("billToContactSnapshotId"),
            "cancelledById": obj.get("cancelledById"),
            "cancelledOn": obj.get("cancelledOn"),
            "comments": obj.get("comments"),
            "currency": obj.get("currency"),
            "discountAmount": obj.get("discountAmount"),
            "eInvoiceStatus": obj.get("eInvoiceStatus"),
            "eInvoiceFileId": obj.get("eInvoiceFileId"),
            "eInvoiceErrorCode": obj.get("eInvoiceErrorCode"),
            "eInvoiceErrorMessage": obj.get("eInvoiceErrorMessage"),
            "exchangeRateDate": obj.get("exchangeRateDate"),
            "excludeFromAutoApplyRules": obj.get("excludeFromAutoApplyRules"),
            "autoApplyUponPosting": obj.get("autoApplyUponPosting"),
            "invoiceGroupNumber": obj.get("invoiceGroupNumber"),
            "memoDate": obj.get("memoDate"),
            "memoNumber": obj.get("memoNumber"),
            "postedById": obj.get("postedById"),
            "postedOn": obj.get("postedOn"),
            "reasonCode": obj.get("reasonCode"),
            "refundAmount": obj.get("refundAmount"),
            "reversed": obj.get("reversed"),
            "revenueImpacting": obj.get("revenueImpacting"),
            "sequenceSetId": obj.get("sequenceSetId"),
            "shipToContactSnapshotId": obj.get("shipToContactSnapshotId"),
            "soldToContactSnapshotId": obj.get("soldToContactSnapshotId"),
            "source": obj.get("source"),
            "sourceType": obj.get("sourceType"),
            "status": obj.get("status"),
            "targetDate": obj.get("targetDate"),
            "taxAmount": obj.get("taxAmount"),
            "taxAutoCalculation": obj.get("taxAutoCalculation"),
            "taxMessage": obj.get("taxMessage"),
            "taxStatus": obj.get("taxStatus"),
            "totalAmount": obj.get("totalAmount"),
            "totalAmountWithoutTax": obj.get("totalAmountWithoutTax"),
            "totalTaxExemptAmount": obj.get("totalTaxExemptAmount"),
            "transferredToAccounting": obj.get("transferredToAccounting"),
            "invoiceId": obj.get("invoiceId"),
            "accountId": obj.get("accountId"),
            "id": obj.get("id"),
            "createdById": obj.get("createdById"),
            "sourceId": obj.get("sourceId"),
            "createdDate": obj.get("createdDate"),
            "updatedById": obj.get("updatedById"),
            "updatedDate": obj.get("updatedDate"),
            "debitMemoId": obj.get("debitMemoId"),
            "account": ExpandedAccount.from_dict(obj["account"]) if obj.get("account") is not None else None,
            "billToContact": ExpandedContact.from_dict(obj["billToContact"]) if obj.get("billToContact") is not None else None,
            "creditMemoItems": [ExpandedCreditMemoItem.from_dict(_item) for _item in obj["creditMemoItems"]] if obj.get("creditMemoItems") is not None else None,
            "creditMemoApplications": [ExpandedCreditMemoApplication.from_dict(_item) for _item in obj["creditMemoApplications"]] if obj.get("creditMemoApplications") is not None else None
        }
        return _obj
from zuora_sdk.models.expanded_account import ExpandedAccount
from zuora_sdk.models.expanded_credit_memo_application import ExpandedCreditMemoApplication
from zuora_sdk.models.expanded_credit_memo_item import ExpandedCreditMemoItem
# TODO: Rewrite to not use raise_errors
ExpandedCreditMemo.model_rebuild(raise_errors=False)


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
