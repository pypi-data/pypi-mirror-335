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
from typing_extensions import Annotated
from zuora_sdk.models.billing_document_status import BillingDocumentStatus
from zuora_sdk.models.e_invoice_status import EInvoiceStatus
from zuora_sdk.models.memo_source_type import MemoSourceType
from zuora_sdk.models.tax_status import TaxStatus
from zuora_sdk.models.transferred_to_accounting_status import TransferredToAccountingStatus
from typing import Optional, Set
from typing_extensions import Self

class DebitMemo(BaseModel):
    """
    DebitMemo
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

    integration_id__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationId__NS")
    integration_status__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Status of the debit memo's synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationStatus__NS")
    sync_date__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Date when the debit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="SyncDate__NS")
    account_id: Optional[StrictStr] = Field(default=None, description="The ID of the customer account associated with the debit memo.", alias="accountId")
    account_number: Optional[StrictStr] = Field(default=None, description="The number of the customer account associated with the debit memo.", alias="accountNumber")
    amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The total amount of the debit memo.")
    auto_pay: Optional[StrictBool] = Field(default=None, description="Whether debit memos are automatically picked up for processing in the corresponding payment run.   By default, debit memos are automatically picked up for processing in the corresponding payment run.       ", alias="autoPay")
    balance: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The balance of the debit memo.")
    be_applied_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The applied amount of the debit memo.", alias="beAppliedAmount")
    bill_to_contact_id: Optional[StrictStr] = Field(default=None, description="The ID of the bill-to contact associated with the debit memo.  The value of this field is `null` if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.", alias="billToContactId")
    cancelled_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the Zuora user who cancelled the debit memo.", alias="cancelledById")
    cancelled_on: Optional[StrictStr] = Field(default=None, description="The date and time when the debit memo was cancelled, in `yyyy-mm-dd hh:mm:ss` format.", alias="cancelledOn")
    comment: Optional[StrictStr] = Field(default=None, description="Comments about the debit memo.")
    created_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the Zuora user who created the debit memo.", alias="createdById")
    created_date: Optional[StrictStr] = Field(default=None, description="The date and time when the debit memo was created, in `yyyy-mm-dd hh:mm:ss` format. For example, 2017-03-01 15:31:10.", alias="createdDate")
    debit_memo_date: Optional[date] = Field(default=None, description="The date when the debit memo takes effect, in `yyyy-mm-dd` format. For example, 2017-05-20.", alias="debitMemoDate")
    due_date: Optional[date] = Field(default=None, description="The date by which the payment for the debit memo is due, in `yyyy-mm-dd` format.", alias="dueDate")
    id: Optional[StrictStr] = Field(default=None, description="The unique ID of the debit memo.")
    invoice_group_number: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The number of invoice group associated with the debit memo.  **Note**: This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature enabled. ", alias="invoiceGroupNumber")
    latest_pdf_file_id: Optional[StrictStr] = Field(default=None, description="The ID of the latest PDF file generated for the debit memo.", alias="latestPDFFileId")
    number: Optional[StrictStr] = Field(default=None, description="The unique identification number of the debit memo.")
    payment_term: Optional[StrictStr] = Field(default=None, description="The name of the payment term associated with the debit memo.  The value of this field is `null` if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.", alias="paymentTerm")
    posted_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the Zuora user who posted the debit memo.", alias="postedById")
    posted_on: Optional[StrictStr] = Field(default=None, description="The date and time when the debit memo was posted, in `yyyy-mm-dd hh:mm:ss` format.", alias="postedOn")
    reason_code: Optional[StrictStr] = Field(default=None, description="A code identifying the reason for the transaction. The value must be an existing reason code or empty.", alias="reasonCode")
    referred_credit_memo_id: Optional[StrictStr] = Field(default=None, description="The ID of the credit memo from which the debit memo was created.", alias="referredCreditMemoId")
    referred_invoice_id: Optional[StrictStr] = Field(default=None, description="The ID of a referred invoice.", alias="referredInvoiceId")
    sequence_set_id: Optional[StrictStr] = Field(default=None, description="The ID of the sequence set associated with the debit memo.  The value of this field is `null` if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.", alias="sequenceSetId")
    sold_to_contact_id: Optional[StrictStr] = Field(default=None, description="The ID of the sold-to contact associated with the debit memo.  The value of this field is `null` if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.", alias="soldToContactId")
    sold_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, description="The ID of the sold-to contact snapshot associated with the debit memo.  The value of this field is `null` if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled.", alias="soldToContactSnapshotId")
    source_type: Optional[StrictStr] = Field(default=None, alias="sourceType")
    status: Optional[StrictStr] = None
    target_date: Optional[date] = Field(default=None, description="The target date for the debit memo, in `yyyy-mm-dd` format. For example, 2017-07-20.", alias="targetDate")
    tax_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The amount of taxation.", alias="taxAmount")
    tax_message: Optional[StrictStr] = Field(default=None, description="The message about the status of tax calculation related to the debit memo. If tax calculation fails in one debit memo, this field displays the reason for the failure.", alias="taxMessage")
    tax_status: Optional[StrictStr] = Field(default=None, alias="taxStatus")
    total_tax_exempt_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The calculated tax amount excluded due to the exemption.", alias="totalTaxExemptAmount")
    transferred_to_accounting: Optional[StrictStr] = Field(default=None, alias="transferredToAccounting")
    updated_by_id: Optional[StrictStr] = Field(default=None, description="The ID of the Zuora user who last updated the debit memo.", alias="updatedById")
    updated_date: Optional[StrictStr] = Field(default=None, description="The date and time when the debit memo was last updated, in `yyyy-mm-dd hh:mm:ss` format. For example, 2017-03-02 15:31:10.", alias="updatedDate")
    e_invoice_status: Optional[StrictStr] = Field(default=None, alias="eInvoiceStatus")
    e_invoice_error_code: Optional[StrictStr] = Field(default=None, description="eInvoiceErrorCode. ", alias="eInvoiceErrorCode")
    e_invoice_error_message: Optional[StrictStr] = Field(default=None, description="eInvoiceErrorMessage. ", alias="eInvoiceErrorMessage")
    e_invoice_file_id: Optional[StrictStr] = Field(default=None, description="eInvoiceFileId. ", alias="eInvoiceFileId")
    bill_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, description="billToContactSnapshotId. ", alias="billToContactSnapshotId")
    organization_label: Optional[StrictStr] = Field(default=None, description="organization label. ", alias="organizationLabel")
    currency: Optional[StrictStr] = Field(default=None, description="Currency code.")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["IntegrationId__NS", "IntegrationStatus__NS", "SyncDate__NS", "accountId", "accountNumber", "amount", "autoPay", "balance", "beAppliedAmount", "billToContactId", "cancelledById", "cancelledOn", "comment", "createdById", "createdDate", "debitMemoDate", "dueDate", "id", "invoiceGroupNumber", "latestPDFFileId", "number", "paymentTerm", "postedById", "postedOn", "reasonCode", "referredCreditMemoId", "referredInvoiceId", "sequenceSetId", "soldToContactId", "soldToContactSnapshotId", "sourceType", "status", "targetDate", "taxAmount", "taxMessage", "taxStatus", "totalTaxExemptAmount", "transferredToAccounting", "updatedById", "updatedDate", "eInvoiceStatus", "eInvoiceErrorCode", "eInvoiceErrorMessage", "eInvoiceFileId", "billToContactSnapshotId", "organizationLabel", "currency"]

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
        """Create an instance of DebitMemo from a JSON string"""
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
        """Create an instance of DebitMemo from a dict"""
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
            "IntegrationId__NS": obj.get("IntegrationId__NS"),
            "IntegrationStatus__NS": obj.get("IntegrationStatus__NS"),
            "SyncDate__NS": obj.get("SyncDate__NS"),
            "accountId": obj.get("accountId"),
            "accountNumber": obj.get("accountNumber"),
            "amount": obj.get("amount"),
            "autoPay": obj.get("autoPay"),
            "balance": obj.get("balance"),
            "beAppliedAmount": obj.get("beAppliedAmount"),
            "billToContactId": obj.get("billToContactId"),
            "cancelledById": obj.get("cancelledById"),
            "cancelledOn": obj.get("cancelledOn"),
            "comment": obj.get("comment"),
            "createdById": obj.get("createdById"),
            "createdDate": obj.get("createdDate"),
            "debitMemoDate": obj.get("debitMemoDate"),
            "dueDate": obj.get("dueDate"),
            "id": obj.get("id"),
            "invoiceGroupNumber": obj.get("invoiceGroupNumber"),
            "latestPDFFileId": obj.get("latestPDFFileId"),
            "number": obj.get("number"),
            "paymentTerm": obj.get("paymentTerm"),
            "postedById": obj.get("postedById"),
            "postedOn": obj.get("postedOn"),
            "reasonCode": obj.get("reasonCode"),
            "referredCreditMemoId": obj.get("referredCreditMemoId"),
            "referredInvoiceId": obj.get("referredInvoiceId"),
            "sequenceSetId": obj.get("sequenceSetId"),
            "soldToContactId": obj.get("soldToContactId"),
            "soldToContactSnapshotId": obj.get("soldToContactSnapshotId"),
            "sourceType": obj.get("sourceType"),
            "status": obj.get("status"),
            "targetDate": obj.get("targetDate"),
            "taxAmount": obj.get("taxAmount"),
            "taxMessage": obj.get("taxMessage"),
            "taxStatus": obj.get("taxStatus"),
            "totalTaxExemptAmount": obj.get("totalTaxExemptAmount"),
            "transferredToAccounting": obj.get("transferredToAccounting"),
            "updatedById": obj.get("updatedById"),
            "updatedDate": obj.get("updatedDate"),
            "eInvoiceStatus": obj.get("eInvoiceStatus"),
            "eInvoiceErrorCode": obj.get("eInvoiceErrorCode"),
            "eInvoiceErrorMessage": obj.get("eInvoiceErrorMessage"),
            "eInvoiceFileId": obj.get("eInvoiceFileId"),
            "billToContactSnapshotId": obj.get("billToContactSnapshotId"),
            "organizationLabel": obj.get("organizationLabel"),
            "currency": obj.get("currency")
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
