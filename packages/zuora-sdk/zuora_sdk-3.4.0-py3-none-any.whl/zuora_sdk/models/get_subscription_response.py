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
from zuora_sdk.models.account_basic_info import AccountBasicInfo
from zuora_sdk.models.contact import Contact
from zuora_sdk.models.externally_managed_by import ExternallyManagedBy
from zuora_sdk.models.failed_reason import FailedReason
from zuora_sdk.models.subscription_rate_plan import SubscriptionRatePlan
from zuora_sdk.models.subscription_status import SubscriptionStatus
from zuora_sdk.models.subscription_status_history import SubscriptionStatusHistory
from zuora_sdk.models.term_period_type import TermPeriodType
from typing import Optional, Set
from typing_extensions import Self

class GetSubscriptionResponse(BaseModel):
    """
    GetSubscriptionResponse
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

    process_id: Optional[StrictStr] = Field(default=None, description="The Id of the process that handle the operation. ", alias="processId")
    request_id: Optional[StrictStr] = Field(default=None, description="Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution. ", alias="requestId")
    reasons: Optional[List[FailedReason]] = None
    success: Optional[StrictBool] = Field(default=None, description="Indicates whether the call succeeded. ")
    cpq_bundle_json_id__qt: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The Bundle product structures from Zuora Quotes if you utilize Bundling in Salesforce. Do not change the value in this field. ", alias="CpqBundleJsonId__QT")
    opportunity_close_date__qt: Optional[date] = Field(default=None, description="The closing date of the Opportunity. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. ", alias="OpportunityCloseDate__QT")
    opportunity_name__qt: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The unique identifier of the Opportunity. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. ", alias="OpportunityName__QT")
    quote_business_type__qt: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The specific identifier for the type of business transaction the Quote represents such as New, Upsell, Downsell, Renewal or Churn. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. ", alias="QuoteBusinessType__QT")
    quote_number__qt: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The unique identifier of the Quote. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. ", alias="QuoteNumber__QT")
    quote_type__qt: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The Quote type that represents the subscription lifecycle stage such as New, Amendment, Renew or Cancel. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. ", alias="QuoteType__QT")
    integration_id__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationId__NS")
    integration_status__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Status of the subscription's synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationStatus__NS")
    project__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The NetSuite project that the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="Project__NS")
    sales_order__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The NetSuite sales order than the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="SalesOrder__NS")
    sync_date__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Date when the subscription was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="SyncDate__NS")
    id: Optional[StrictStr] = Field(default=None, description="Subscription ID. ")
    subscription_number: Optional[StrictStr] = Field(default=None, description="Subscription number.", alias="subscriptionNumber")
    account_id: Optional[StrictStr] = Field(default=None, description="The ID of the account associated with this subscription.", alias="accountId")
    account_name: Optional[StrictStr] = Field(default=None, description="The name of the account associated with this subscription.", alias="accountName")
    account_number: Optional[StrictStr] = Field(default=None, description="The number of the account associated with this subscription.", alias="accountNumber")
    auto_renew: Optional[StrictBool] = Field(default=None, description="If `true`, the subscription automatically renews at the end of the term. Default is `false`. ", alias="autoRenew")
    bill_to_contact: Optional[Contact] = Field(default=None, alias="billToContact")
    cancel_reason: Optional[StrictStr] = Field(default=None, description="The reason for a subscription cancellation copied from the `changeReason` field of a Cancel Subscription order action.   This field contains valid value only if a subscription is cancelled through the Orders UI or API. Otherwise, the value for this field will always be `null`. ", alias="cancelReason")
    contract_effective_date: Optional[date] = Field(default=None, description="Effective contract date for this subscription, as yyyy-mm-dd. ", alias="contractEffectiveDate")
    contracted_mrr: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Monthly recurring revenue of the subscription. ", alias="contractedMrr")
    current_term: Optional[StrictInt] = Field(default=None, description="The length of the period for the current subscription term. ", alias="currentTerm")
    current_term_period_type: Optional[TermPeriodType] = Field(default=None, alias="currentTermPeriodType")
    customer_acceptance_date: Optional[date] = Field(default=None, description="The date on which the services or products within a subscription have been accepted by the customer, as yyyy-mm-dd. ", alias="customerAcceptanceDate")
    currency: Optional[StrictStr] = Field(default=None, description="The currency of the subscription. ")
    create_time: Optional[StrictStr] = Field(default=None, description="The date when the subscription was created, as yyyy-mm-dd HH:MM:SS. ", alias="createTime")
    update_time: Optional[StrictStr] = Field(default=None, description="The date when the subscription was last updated, as yyyy-mm-dd HH:MM:SS. ", alias="updateTime")
    externally_managed_by: Optional[ExternallyManagedBy] = Field(default=None, alias="externallyManagedBy")
    initial_term: Optional[StrictInt] = Field(default=None, description="The length of the period for the first subscription term. ", alias="initialTerm")
    initial_term_period_type: Optional[TermPeriodType] = Field(default=None, alias="initialTermPeriodType")
    invoice_group_number: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The number of invoice group associated with the subscription.  **Note**: This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature enabled. ", alias="invoiceGroupNumber")
    invoice_owner_account_id: Optional[StrictStr] = Field(default=None, alias="invoiceOwnerAccountId")
    invoice_owner_account_name: Optional[StrictStr] = Field(default=None, alias="invoiceOwnerAccountName")
    invoice_owner_account_number: Optional[StrictStr] = Field(default=None, alias="invoiceOwnerAccountNumber")
    invoice_schedule_id: Optional[StrictStr] = Field(default=None, description="The ID of the invoice schedule associated with the subscription.  If multiple invoice schedules are created for different terms of a subscription, this field stores the latest invoice schedule.  **Note**: This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\" target=\"_blank\">Billing Schedule</a> feature in the **Early Adopter** phase enabled. ", alias="invoiceScheduleId")
    invoice_separately: Optional[StrictStr] = Field(default=None, description="Separates a single subscription from other subscriptions and creates an invoice for the subscription.   If the value is `true`, the subscription is billed separately from other subscriptions. If the value is `false`, the subscription is included with other subscriptions in the account invoice. ", alias="invoiceSeparately")
    invoice_template_id: Optional[StrictStr] = Field(default=None, description="The ID of the invoice template associated with the subscription.  **Note**:    - If you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature disabled, this field is unavailable in the request body and the value of this field is `null` in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Template from Account** for this field during subscription creation, the value of this field is automatically set to `null` in the response body. ", alias="invoiceTemplateId")
    invoice_template_name: Optional[StrictStr] = Field(default=None, description="The name of the invoice template associated with the subscription.  **Note**:    - If you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature disabled, the value of this field is `null` in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify the `invoiceTemplateId` field in the request or you select **Default Template from Account** for the `invoiceTemplateId` field during subscription creation, the value of the `invoiceTemplateName` field is automatically set to `null` in the response body.    ", alias="invoiceTemplateName")
    is_latest_version: Optional[StrictBool] = Field(default=None, description="If `true`, the current subscription object is the latest version.", alias="isLatestVersion")
    last_booking_date: Optional[date] = Field(default=None, description="The last booking date of the subscription object. This field is writable only when the subscription is newly created as a first version subscription. You can override the date value when creating a subscription through the Subscribe and Amend API or the subscription creation UI (non-Orders). Otherwise, the default value `today` is set per the user's timezone. The value of this field is as follows: * For a new subscription created by the [Subscribe and Amend APIs](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Orders_Harmonization/Orders_Migration_Guidance#Subscribe_and_Amend_APIs_to_Migrate), this field has the value of the subscription creation date. * For a subscription changed by an amendment, this field has the value of the amendment booking date. * For a subscription created or changed by an order, this field has the value of the order date. ", alias="lastBookingDate")
    notes: Optional[StrictStr] = Field(default=None, description="A string of up to 65,535 characters. ")
    order_number: Optional[StrictStr] = Field(default=None, description="The order number of the order in which the changes on the subscription are made.   **Note:** This field is only available if you have the [Order Metrics](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AA_Overview_of_Orders#Order_Metrics) feature enabled. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/). We will investigate your use cases and data before enabling this feature for you. ", alias="orderNumber")
    payment_term: Optional[StrictStr] = Field(default=None, description="The name of the payment term associated with the subscription. For example, `Net 30`. The payment term determines the due dates of invoices.  **Note**:    - If you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature disabled, this field is unavailable in the request body and the value of this field is `null` in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Term from Account** for this field during subscription creation, the value of this field is automatically set to `null` in the response body. ", alias="paymentTerm")
    rate_plans: Optional[List[SubscriptionRatePlan]] = Field(default=None, description="Container for rate plans. ", alias="ratePlans")
    renewal_setting: Optional[StrictStr] = Field(default=None, description="Specifies whether a termed subscription will remain `TERMED` or change to `EVERGREEN` when it is renewed.   Values are:  * `RENEW_WITH_SPECIFIC_TERM` (default) * `RENEW_TO_EVERGREEN` ", alias="renewalSetting")
    renewal_term: Optional[StrictInt] = Field(default=None, description="The length of the period for the subscription renewal term. ", alias="renewalTerm")
    renewal_term_period_type: Optional[TermPeriodType] = Field(default=None, alias="renewalTermPeriodType")
    revision: Optional[StrictStr] = Field(default=None, description="An auto-generated decimal value uniquely tagged with a subscription. The value always contains one decimal place, for example, the revision of a new subscription is 1.0. If a further version of the subscription is created, the revision value will be increased by 1. Also, the revision value is always incremental regardless of deletion of subscription versions. ")
    sequence_set_id: Optional[StrictStr] = Field(default=None, description="The ID of the sequence set associated with the subscription.  **Note**:    - If you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature disabled, this field is unavailable in the request body and the value of this field is `null` in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Set from Account** for this field during subscription creation, the value of this field is automatically set to `null` in the response body. ", alias="sequenceSetId")
    sequence_set_name: Optional[StrictStr] = Field(default=None, description="The name of the sequence set associated with the subscription.  **Note**:    - If you have the <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\" target=\"_blank\">Flexible Billing Attributes</a> feature disabled, the value of this field is `null` in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify the `sequenceSetId` field in the request or you select **Default Template from Account** for the `sequenceSetId` field during subscription creation, the value of the `sequenceSetName` field is automatically set to `null` in the response body. ", alias="sequenceSetName")
    service_activation_date: Optional[date] = Field(default=None, description="The date on which the services or products within a subscription have been activated and access has been provided to the customer, as yyyy-mm-dd ", alias="serviceActivationDate")
    sold_to_contact: Optional[Contact] = Field(default=None, alias="soldToContact")
    ship_to_contact: Optional[Contact] = Field(default=None, alias="shipToContact")
    status: Optional[SubscriptionStatus] = None
    status_history: Optional[List[SubscriptionStatusHistory]] = Field(default=None, description="Container for status history. ", alias="statusHistory")
    subscription_start_date: Optional[date] = Field(default=None, description="Date the subscription becomes effective. ", alias="subscriptionStartDate")
    subscription_end_date: Optional[date] = Field(default=None, description="The date when the subscription term ends, where the subscription ends at midnight the day before. For example, if the `subscriptionEndDate` is 12/31/2016, the subscriptions ends at midnight (00:00:00 hours) on 12/30/2016. This date is the same as the term end date or the cancelation date, as appropriate. ", alias="subscriptionEndDate")
    term_end_date: Optional[date] = Field(default=None, description="Date the subscription term ends. If the subscription is evergreen, this is null or is the cancellation date (if one has been set). ", alias="termEndDate")
    term_start_date: Optional[date] = Field(default=None, description="Date the subscription term begins. If this is a renewal subscription, this date is different from the subscription start date. ", alias="termStartDate")
    term_type: Optional[StrictStr] = Field(default=None, description="Possible values are: `TERMED`, `EVERGREEN`. ", alias="termType")
    scheduled_cancel_date: Optional[date] = Field(default=None, alias="scheduledCancelDate")
    scheduled_suspend_date: Optional[date] = Field(default=None, alias="scheduledSuspendDate")
    scheduled_resume_date: Optional[date] = Field(default=None, alias="scheduledResumeDate")
    total_contracted_value: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Total contracted value of the subscription. ", alias="totalContractedValue")
    version: Optional[StrictInt] = Field(default=None, description="This is the subscription version automatically generated by Zuora Billing. Each order or amendment creates a new version of the subscription, which incorporates the changes made in the order or amendment.")
    contracted_net_mrr: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Monthly recurring revenue of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts. ", alias="contractedNetMrr")
    as_of_day_gross_mrr: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Monthly recurring revenue of the subscription exclusive of any discounts applicable as of specified day. ", alias="asOfDayGrossMrr")
    as_of_day_net_mrr: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Monthly recurring revenue of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts as of specified day. ", alias="asOfDayNetMrr")
    net_total_contracted_value: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Total contracted value of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts. ", alias="netTotalContractedValue")
    account_owner_details: Optional[AccountBasicInfo] = Field(default=None, alias="accountOwnerDetails")
    invoice_owner_account_details: Optional[AccountBasicInfo] = Field(default=None, alias="invoiceOwnerAccountDetails")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["processId", "requestId", "reasons", "success", "CpqBundleJsonId__QT", "OpportunityCloseDate__QT", "OpportunityName__QT", "QuoteBusinessType__QT", "QuoteNumber__QT", "QuoteType__QT", "IntegrationId__NS", "IntegrationStatus__NS", "Project__NS", "SalesOrder__NS", "SyncDate__NS", "id", "subscriptionNumber", "accountId", "accountName", "accountNumber", "autoRenew", "billToContact", "cancelReason", "contractEffectiveDate", "contractedMrr", "currentTerm", "currentTermPeriodType", "customerAcceptanceDate", "currency", "createTime", "updateTime", "externallyManagedBy", "initialTerm", "initialTermPeriodType", "invoiceGroupNumber", "invoiceOwnerAccountId", "invoiceOwnerAccountName", "invoiceOwnerAccountNumber", "invoiceScheduleId", "invoiceSeparately", "invoiceTemplateId", "invoiceTemplateName", "isLatestVersion", "lastBookingDate", "notes", "orderNumber", "paymentTerm", "ratePlans", "renewalSetting", "renewalTerm", "renewalTermPeriodType", "revision", "sequenceSetId", "sequenceSetName", "serviceActivationDate", "soldToContact", "shipToContact", "status", "statusHistory", "subscriptionStartDate", "subscriptionEndDate", "termEndDate", "termStartDate", "termType", "scheduledCancelDate", "scheduledSuspendDate", "scheduledResumeDate", "totalContractedValue", "version", "contractedNetMrr", "asOfDayGrossMrr", "asOfDayNetMrr", "netTotalContractedValue", "accountOwnerDetails", "invoiceOwnerAccountDetails"]

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
        """Create an instance of GetSubscriptionResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in reasons (list)
        _items = []
        if self.reasons:
            for _item_reasons in self.reasons:
                if _item_reasons:
                    _items.append(_item_reasons.to_dict())
            _dict['reasons'] = _items
        # override the default output from pydantic by calling `to_dict()` of bill_to_contact
        if self.bill_to_contact:
            _dict['billToContact'] = self.bill_to_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in rate_plans (list)
        _items = []
        if self.rate_plans:
            for _item_rate_plans in self.rate_plans:
                if _item_rate_plans:
                    _items.append(_item_rate_plans.to_dict())
            _dict['ratePlans'] = _items
        # override the default output from pydantic by calling `to_dict()` of sold_to_contact
        if self.sold_to_contact:
            _dict['soldToContact'] = self.sold_to_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of ship_to_contact
        if self.ship_to_contact:
            _dict['shipToContact'] = self.ship_to_contact.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in status_history (list)
        _items = []
        if self.status_history:
            for _item_status_history in self.status_history:
                if _item_status_history:
                    _items.append(_item_status_history.to_dict())
            _dict['statusHistory'] = _items
        # override the default output from pydantic by calling `to_dict()` of account_owner_details
        if self.account_owner_details:
            _dict['accountOwnerDetails'] = self.account_owner_details.to_dict()
        # override the default output from pydantic by calling `to_dict()` of invoice_owner_account_details
        if self.invoice_owner_account_details:
            _dict['invoiceOwnerAccountDetails'] = self.invoice_owner_account_details.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of GetSubscriptionResponse from a dict"""
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
            "processId": obj.get("processId"),
            "requestId": obj.get("requestId"),
            "reasons": [FailedReason.from_dict(_item) for _item in obj["reasons"]] if obj.get("reasons") is not None else None,
            "success": obj.get("success"),
            "CpqBundleJsonId__QT": obj.get("CpqBundleJsonId__QT"),
            "OpportunityCloseDate__QT": obj.get("OpportunityCloseDate__QT"),
            "OpportunityName__QT": obj.get("OpportunityName__QT"),
            "QuoteBusinessType__QT": obj.get("QuoteBusinessType__QT"),
            "QuoteNumber__QT": obj.get("QuoteNumber__QT"),
            "QuoteType__QT": obj.get("QuoteType__QT"),
            "IntegrationId__NS": obj.get("IntegrationId__NS"),
            "IntegrationStatus__NS": obj.get("IntegrationStatus__NS"),
            "Project__NS": obj.get("Project__NS"),
            "SalesOrder__NS": obj.get("SalesOrder__NS"),
            "SyncDate__NS": obj.get("SyncDate__NS"),
            "id": obj.get("id"),
            "subscriptionNumber": obj.get("subscriptionNumber"),
            "accountId": obj.get("accountId"),
            "accountName": obj.get("accountName"),
            "accountNumber": obj.get("accountNumber"),
            "autoRenew": obj.get("autoRenew"),
            "billToContact": Contact.from_dict(obj["billToContact"]) if obj.get("billToContact") is not None else None,
            "cancelReason": obj.get("cancelReason"),
            "contractEffectiveDate": obj.get("contractEffectiveDate"),
            "contractedMrr": obj.get("contractedMrr"),
            "currentTerm": obj.get("currentTerm"),
            "currentTermPeriodType": obj.get("currentTermPeriodType"),
            "customerAcceptanceDate": obj.get("customerAcceptanceDate"),
            "currency": obj.get("currency"),
            "createTime": obj.get("createTime"),
            "updateTime": obj.get("updateTime"),
            "externallyManagedBy": obj.get("externallyManagedBy"),
            "initialTerm": obj.get("initialTerm"),
            "initialTermPeriodType": obj.get("initialTermPeriodType"),
            "invoiceGroupNumber": obj.get("invoiceGroupNumber"),
            "invoiceOwnerAccountId": obj.get("invoiceOwnerAccountId"),
            "invoiceOwnerAccountName": obj.get("invoiceOwnerAccountName"),
            "invoiceOwnerAccountNumber": obj.get("invoiceOwnerAccountNumber"),
            "invoiceScheduleId": obj.get("invoiceScheduleId"),
            "invoiceSeparately": obj.get("invoiceSeparately"),
            "invoiceTemplateId": obj.get("invoiceTemplateId"),
            "invoiceTemplateName": obj.get("invoiceTemplateName"),
            "isLatestVersion": obj.get("isLatestVersion"),
            "lastBookingDate": obj.get("lastBookingDate"),
            "notes": obj.get("notes"),
            "orderNumber": obj.get("orderNumber"),
            "paymentTerm": obj.get("paymentTerm"),
            "ratePlans": [SubscriptionRatePlan.from_dict(_item) for _item in obj["ratePlans"]] if obj.get("ratePlans") is not None else None,
            "renewalSetting": obj.get("renewalSetting"),
            "renewalTerm": obj.get("renewalTerm"),
            "renewalTermPeriodType": obj.get("renewalTermPeriodType"),
            "revision": obj.get("revision"),
            "sequenceSetId": obj.get("sequenceSetId"),
            "sequenceSetName": obj.get("sequenceSetName"),
            "serviceActivationDate": obj.get("serviceActivationDate"),
            "soldToContact": Contact.from_dict(obj["soldToContact"]) if obj.get("soldToContact") is not None else None,
            "shipToContact": Contact.from_dict(obj["shipToContact"]) if obj.get("shipToContact") is not None else None,
            "status": obj.get("status"),
            "statusHistory": [SubscriptionStatusHistory.from_dict(_item) for _item in obj["statusHistory"]] if obj.get("statusHistory") is not None else None,
            "subscriptionStartDate": obj.get("subscriptionStartDate"),
            "subscriptionEndDate": obj.get("subscriptionEndDate"),
            "termEndDate": obj.get("termEndDate"),
            "termStartDate": obj.get("termStartDate"),
            "termType": obj.get("termType"),
            "scheduledCancelDate": obj.get("scheduledCancelDate"),
            "scheduledSuspendDate": obj.get("scheduledSuspendDate"),
            "scheduledResumeDate": obj.get("scheduledResumeDate"),
            "totalContractedValue": obj.get("totalContractedValue"),
            "version": obj.get("version"),
            "contractedNetMrr": obj.get("contractedNetMrr"),
            "asOfDayGrossMrr": obj.get("asOfDayGrossMrr"),
            "asOfDayNetMrr": obj.get("asOfDayNetMrr"),
            "netTotalContractedValue": obj.get("netTotalContractedValue"),
            "accountOwnerDetails": AccountBasicInfo.from_dict(obj["accountOwnerDetails"]) if obj.get("accountOwnerDetails") is not None else None,
            "invoiceOwnerAccountDetails": AccountBasicInfo.from_dict(obj["invoiceOwnerAccountDetails"]) if obj.get("invoiceOwnerAccountDetails") is not None else None
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
