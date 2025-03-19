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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing_extensions import Annotated
from zuora_sdk.models.billing_document_item_processing_type import BillingDocumentItemProcessingType
from zuora_sdk.models.billing_document_item_source_type import BillingDocumentItemSourceType
from zuora_sdk.models.charge_type import ChargeType
from zuora_sdk.models.rev_rec_trigger import RevRecTrigger
from zuora_sdk.models.tax_mode import TaxMode
from zuora_sdk.models.taxation_items_data import TaxationItemsData
from typing import Optional, Set
from typing_extensions import Self

class InvoiceItem(BaseModel):
    """
    InvoiceItem
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
    integration_status__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Status of the invoice item's synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationStatus__NS")
    sync_date__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Date when the invoice item was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="SyncDate__NS")
    accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code associated with the invoice item.", alias="accountingCode")
    adjustment_liability_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for adjustment liability.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="adjustmentLiabilityAccountingCode")
    adjustment_revenue_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for adjustment revenue.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="adjustmentRevenueAccountingCode")
    applied_to_item_id: Optional[StrictStr] = Field(default=None, description="The unique ID of the invoice item that the discount charge is applied to.", alias="appliedToItemId")
    available_to_credit_amount: Optional[Decimal] = Field(default=None, description="The amount of the invoice item that is available to credit.", alias="availableToCreditAmount")
    balance: Optional[StrictStr] = Field(default=None, description="The balance of the invoice item.")
    booking_reference: Optional[StrictStr] = Field(default=None, description="The booking reference of the invoice item.", alias="bookingReference")
    charge_amount: Optional[StrictStr] = Field(default=None, description="The amount of the charge.   This amount does not include taxes regardless if the charge's tax mode is inclusive or exclusive. ", alias="chargeAmount")
    charge_date: Optional[StrictStr] = Field(default=None, description="The date when the invoice item is charged, in `yyyy-mm-dd hh:mm:ss` format.", alias="chargeDate")
    charge_description: Optional[StrictStr] = Field(default=None, description="The description of the charge.", alias="chargeDescription")
    charge_id: Optional[StrictStr] = Field(default=None, description="The unique ID of the charge.", alias="chargeId")
    charge_name: Optional[StrictStr] = Field(default=None, description="The name of the charge.", alias="chargeName")
    charge_type: Optional[StrictStr] = Field(default=None, alias="chargeType")
    contract_asset_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for contract asset.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="contractAssetAccountingCode")
    contract_liability_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for contract liability.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="contractLiabilityAccountingCode")
    contract_recognized_revenue_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for contract recognized revenue.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="contractRecognizedRevenueAccountingCode")
    deferred_revenue_accounting_code: Optional[StrictStr] = Field(default=None, description="The deferred revenue accounting code associated with the invoice item. **Note:** This field is only available if you have Zuora Finance enabled.", alias="deferredRevenueAccountingCode")
    description: Optional[StrictStr] = Field(default=None, description="The description of the invoice item.")
    exclude_item_billing_from_revenue_accounting: Optional[StrictBool] = Field(default=None, description="The flag to exclude the invoice item from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="excludeItemBillingFromRevenueAccounting")
    id: Optional[StrictStr] = Field(default=None, description="Item ID.")
    invoice_schedule_id: Optional[StrictStr] = Field(default=None, description="The ID of the invoice schedule item by which Invoice Schedule Item the invoice item is generated by when the Invoice Schedule Item is executed. **Note**: This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\" target=\"_blank\">Billing Schedule</a> feature in the **Early Adopter** phase enabled.", alias="invoiceScheduleId")
    invoice_schedule_item_id: Optional[StrictStr] = Field(default=None, description="The ID of the invoice schedule item associated with the invoice item. **Note**: This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\" target=\"_blank\">Billing Schedule</a> feature in the **Early Adopter** phase enabled.", alias="invoiceScheduleItemId")
    item_type: Optional[StrictStr] = Field(default=None, description="The type of the invoice item.", alias="itemType")
    processing_type: Optional[StrictStr] = Field(default=None, alias="processingType")
    product_name: Optional[StrictStr] = Field(default=None, description="Name of the product associated with this item.", alias="productName")
    product_rate_plan_charge_id: Optional[StrictStr] = Field(default=None, description="The ID of the product rate plan charge that the invoice item is created from.", alias="productRatePlanChargeId")
    purchase_order_number: Optional[StrictStr] = Field(default=None, description="The purchase order number associated with the invoice item.", alias="purchaseOrderNumber")
    quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The quantity of this item, in the configured unit of measure for the charge.")
    recognized_revenue_accounting_code: Optional[StrictStr] = Field(default=None, description="The recognized revenue accounting code associated with the invoice item. **Note:** This field is only available if you have Zuora Finance enabled.", alias="recognizedRevenueAccountingCode")
    rev_rec_code: Optional[StrictStr] = Field(default=None, description="The revenue recognition code.", alias="revRecCode")
    rev_rec_trigger_condition: Optional[StrictStr] = Field(default=None, alias="revRecTriggerCondition")
    revenue_recognition_rule_name: Optional[StrictStr] = Field(default=None, description="The revenue recognition rule of the invoice item. **Note:** This field is only available if you have Zuora Finance enabled.", alias="revenueRecognitionRuleName")
    service_end_date: Optional[date] = Field(default=None, description="The end date of the service period for this item, i.e., the last day of the service period, as _yyyy-mm-dd_.", alias="serviceEndDate")
    service_start_date: Optional[date] = Field(default=None, description="The start date of the service period for this item, as _yyyy-mm-dd_. For a one-time fee item, the date of the charge.", alias="serviceStartDate")
    ship_to_contact_id: Optional[StrictStr] = Field(default=None, description="The ID of the ship-to contact associated with the invoice item.", alias="shipToContactId")
    sku: Optional[StrictStr] = Field(default=None, description="The SKU of the invoice item.")
    sold_to_contact_id: Optional[StrictStr] = Field(default=None, description="The ID of the sold-to contact associated with the invoice item. **Note**: If you have the Flexible Billing Attributes feature disabled, the value of this field is `null`.", alias="soldToContactId")
    sold_to_contact_snapshot_id: Optional[StrictStr] = Field(default=None, description="The ID of the sold-to contact snapshot associated with the invoice item. **Note**: If you have the Flexible Billing Attributes feature disabled, the value of this field is `null`.", alias="soldToContactSnapshotId")
    source_item_type: Optional[StrictStr] = Field(default=None, alias="sourceItemType")
    subscription_id: Optional[StrictStr] = Field(default=None, description="The ID of the subscription for this item.", alias="subscriptionId")
    subscription_name: Optional[StrictStr] = Field(default=None, description="The name of the subscription for this item.", alias="subscriptionName")
    tax_amount: Optional[StrictStr] = Field(default=None, description="Tax applied to the charge.", alias="taxAmount")
    tax_code: Optional[StrictStr] = Field(default=None, description="The tax code of the invoice item. **Note** Only when taxation feature is enabled, this field can be presented.", alias="taxCode")
    tax_mode: Optional[StrictStr] = Field(default=None, alias="taxMode")
    taxation_items: Optional[TaxationItemsData] = Field(default=None, alias="taxationItems")
    unbilled_receivables_accounting_code: Optional[StrictStr] = Field(default=None, description="The accounting code for unbilled receivables.         **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="unbilledReceivablesAccountingCode")
    unit_of_measure: Optional[StrictStr] = Field(default=None, description="Unit used to measure consumption.", alias="unitOfMeasure")
    unit_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The per-unit price of the invoice item.", alias="unitPrice")
    number_of_deliveries: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The number of delivery for charge.  **Note**: This field is available only if you have the Delivery Pricing feature enabled. ", alias="numberOfDeliveries")
    reflect_discount_in_net_amount: Optional[StrictBool] = Field(default=None, description="The flag to reflect Discount in Apply To Charge Net Amount. ", alias="reflectDiscountInNetAmount")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["IntegrationId__NS", "IntegrationStatus__NS", "SyncDate__NS", "accountingCode", "adjustmentLiabilityAccountingCode", "adjustmentRevenueAccountingCode", "appliedToItemId", "availableToCreditAmount", "balance", "bookingReference", "chargeAmount", "chargeDate", "chargeDescription", "chargeId", "chargeName", "chargeType", "contractAssetAccountingCode", "contractLiabilityAccountingCode", "contractRecognizedRevenueAccountingCode", "deferredRevenueAccountingCode", "description", "excludeItemBillingFromRevenueAccounting", "id", "invoiceScheduleId", "invoiceScheduleItemId", "itemType", "processingType", "productName", "productRatePlanChargeId", "purchaseOrderNumber", "quantity", "recognizedRevenueAccountingCode", "revRecCode", "revRecTriggerCondition", "revenueRecognitionRuleName", "serviceEndDate", "serviceStartDate", "shipToContactId", "sku", "soldToContactId", "soldToContactSnapshotId", "sourceItemType", "subscriptionId", "subscriptionName", "taxAmount", "taxCode", "taxMode", "taxationItems", "unbilledReceivablesAccountingCode", "unitOfMeasure", "unitPrice", "numberOfDeliveries", "reflectDiscountInNetAmount"]

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
        """Create an instance of InvoiceItem from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of taxation_items
        if self.taxation_items:
            _dict['taxationItems'] = self.taxation_items.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of InvoiceItem from a dict"""
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
            "accountingCode": obj.get("accountingCode"),
            "adjustmentLiabilityAccountingCode": obj.get("adjustmentLiabilityAccountingCode"),
            "adjustmentRevenueAccountingCode": obj.get("adjustmentRevenueAccountingCode"),
            "appliedToItemId": obj.get("appliedToItemId"),
            "availableToCreditAmount": obj.get("availableToCreditAmount"),
            "balance": obj.get("balance"),
            "bookingReference": obj.get("bookingReference"),
            "chargeAmount": obj.get("chargeAmount"),
            "chargeDate": obj.get("chargeDate"),
            "chargeDescription": obj.get("chargeDescription"),
            "chargeId": obj.get("chargeId"),
            "chargeName": obj.get("chargeName"),
            "chargeType": obj.get("chargeType"),
            "contractAssetAccountingCode": obj.get("contractAssetAccountingCode"),
            "contractLiabilityAccountingCode": obj.get("contractLiabilityAccountingCode"),
            "contractRecognizedRevenueAccountingCode": obj.get("contractRecognizedRevenueAccountingCode"),
            "deferredRevenueAccountingCode": obj.get("deferredRevenueAccountingCode"),
            "description": obj.get("description"),
            "excludeItemBillingFromRevenueAccounting": obj.get("excludeItemBillingFromRevenueAccounting"),
            "id": obj.get("id"),
            "invoiceScheduleId": obj.get("invoiceScheduleId"),
            "invoiceScheduleItemId": obj.get("invoiceScheduleItemId"),
            "itemType": obj.get("itemType"),
            "processingType": obj.get("processingType"),
            "productName": obj.get("productName"),
            "productRatePlanChargeId": obj.get("productRatePlanChargeId"),
            "purchaseOrderNumber": obj.get("purchaseOrderNumber"),
            "quantity": obj.get("quantity"),
            "recognizedRevenueAccountingCode": obj.get("recognizedRevenueAccountingCode"),
            "revRecCode": obj.get("revRecCode"),
            "revRecTriggerCondition": obj.get("revRecTriggerCondition"),
            "revenueRecognitionRuleName": obj.get("revenueRecognitionRuleName"),
            "serviceEndDate": obj.get("serviceEndDate"),
            "serviceStartDate": obj.get("serviceStartDate"),
            "shipToContactId": obj.get("shipToContactId"),
            "sku": obj.get("sku"),
            "soldToContactId": obj.get("soldToContactId"),
            "soldToContactSnapshotId": obj.get("soldToContactSnapshotId"),
            "sourceItemType": obj.get("sourceItemType"),
            "subscriptionId": obj.get("subscriptionId"),
            "subscriptionName": obj.get("subscriptionName"),
            "taxAmount": obj.get("taxAmount"),
            "taxCode": obj.get("taxCode"),
            "taxMode": obj.get("taxMode"),
            "taxationItems": TaxationItemsData.from_dict(obj["taxationItems"]) if obj.get("taxationItems") is not None else None,
            "unbilledReceivablesAccountingCode": obj.get("unbilledReceivablesAccountingCode"),
            "unitOfMeasure": obj.get("unitOfMeasure"),
            "unitPrice": obj.get("unitPrice"),
            "numberOfDeliveries": obj.get("numberOfDeliveries"),
            "reflectDiscountInNetAmount": obj.get("reflectDiscountInNetAmount")
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
