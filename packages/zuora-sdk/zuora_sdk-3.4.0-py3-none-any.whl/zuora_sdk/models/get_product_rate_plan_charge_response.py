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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing_extensions import Annotated
from zuora_sdk.models.apply_discount_to import ApplyDiscountTo
from zuora_sdk.models.bill_cycle_type import BillCycleType
from zuora_sdk.models.billing_period_alignment_product_rate_plan_charge_rest import BillingPeriodAlignmentProductRatePlanChargeRest
from zuora_sdk.models.billing_period_product_rate_plan_charge_rest import BillingPeriodProductRatePlanChargeRest
from zuora_sdk.models.billing_timing_product_rate_plan_charge_rest import BillingTimingProductRatePlanChargeRest
from zuora_sdk.models.charge_function import ChargeFunction
from zuora_sdk.models.charge_model_configuration import ChargeModelConfiguration
from zuora_sdk.models.charge_model_product_rate_plan_charge_rest import ChargeModelProductRatePlanChargeRest
from zuora_sdk.models.charge_type import ChargeType
from zuora_sdk.models.commitment_type import CommitmentType
from zuora_sdk.models.delivery_schedule_product_rate_plan_charge import DeliveryScheduleProductRatePlanCharge
from zuora_sdk.models.discount_level import DiscountLevel
from zuora_sdk.models.end_date_condition_product_rate_plan_charge_rest import EndDateConditionProductRatePlanChargeRest
from zuora_sdk.models.list_price_base import ListPriceBase
from zuora_sdk.models.overage_calculation_option import OverageCalculationOption
from zuora_sdk.models.overage_unused_units_credit_option import OverageUnusedUnitsCreditOption
from zuora_sdk.models.prepaid_operation_type import PrepaidOperationType
from zuora_sdk.models.price_change_option import PriceChangeOption
from zuora_sdk.models.price_increase_option import PriceIncreaseOption
from zuora_sdk.models.product_rate_plan_charge_object_ns_fields_include_children_ns import ProductRatePlanChargeObjectNSFieldsIncludeChildrenNS
from zuora_sdk.models.product_rate_plan_charge_object_ns_fields_item_type_ns import ProductRatePlanChargeObjectNSFieldsItemTypeNS
from zuora_sdk.models.product_rate_plan_charge_object_ns_fields_rev_rec_end_ns import ProductRatePlanChargeObjectNSFieldsRevRecEndNS
from zuora_sdk.models.product_rate_plan_charge_object_ns_fields_rev_rec_start_ns import ProductRatePlanChargeObjectNSFieldsRevRecStartNS
from zuora_sdk.models.rating_group import RatingGroup
from zuora_sdk.models.rating_groups_operator_type import RatingGroupsOperatorType
from zuora_sdk.models.rev_rec_trigger_condition_product_rate_plan_charge_rest import RevRecTriggerConditionProductRatePlanChargeRest
from zuora_sdk.models.revenue_recognition_rule_name import RevenueRecognitionRuleName
from zuora_sdk.models.rollover_apply import RolloverApply
from zuora_sdk.models.smoothing_model import SmoothingModel
from zuora_sdk.models.tax_mode import TaxMode
from zuora_sdk.models.trigger_event_product_rate_plan_charge_rest import TriggerEventProductRatePlanChargeRest
from zuora_sdk.models.up_to_periods_type_product_rate_plan_charge_rest import UpToPeriodsTypeProductRatePlanChargeRest
from zuora_sdk.models.usage_record_rating_option import UsageRecordRatingOption
from zuora_sdk.models.validity_period_type import ValidityPeriodType
from zuora_sdk.models.weekly_bill_cycle_day import WeeklyBillCycleDay
from typing import Optional, Set
from typing_extensions import Self

class GetProductRatePlanChargeResponse(BaseModel):
    """
    GetProductRatePlanChargeResponse
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

    id: Optional[StrictStr] = Field(default=None, description="Object identifier.", alias="Id")
    product_rate_plan_id: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The ID of the product rate plan associated with this product rate plan charge. ", alias="ProductRatePlanId")
    accounting_code: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The accounting code for the charge. Accounting codes group transactions that contain similar accounting attributes. ", alias="AccountingCode")
    apply_discount_to: Optional[ApplyDiscountTo] = Field(default=None, alias="ApplyDiscountTo")
    bill_cycle_day: Optional[StrictInt] = Field(default=None, description="Sets the bill cycle day (BCD) for the charge. The BCD determines which day of the month customer is billed. The BCD value in the account can override the BCD in this object. StackedDiscount **Character limit**: 2  **Values**: a valid BCD integer, 1 - 31 ", alias="BillCycleDay")
    bill_cycle_type: Optional[BillCycleType] = Field(default=None, alias="BillCycleType")
    billing_period: Optional[BillingPeriodProductRatePlanChargeRest] = Field(default=None, alias="BillingPeriod")
    billing_period_alignment: Optional[BillingPeriodAlignmentProductRatePlanChargeRest] = Field(default=None, alias="BillingPeriodAlignment")
    billing_timing: Optional[BillingTimingProductRatePlanChargeRest] = Field(default=None, alias="BillingTiming")
    charge_function: Optional[ChargeFunction] = Field(default=None, alias="ChargeFunction")
    charge_model: Optional[ChargeModelProductRatePlanChargeRest] = Field(default=None, alias="ChargeModel")
    charge_model_configuration: Optional[ChargeModelConfiguration] = Field(default=None, alias="ChargeModelConfiguration")
    charge_type: Optional[ChargeType] = Field(default=None, alias="ChargeType")
    commitment_type: Optional[CommitmentType] = Field(default=None, alias="CommitmentType")
    created_by_id: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The automatically generated ID of the Zuora user who created the `ProductRatePlanCharge` object. ", alias="CreatedById")
    created_date: Optional[datetime] = Field(default=None, description="The date when the `ProductRatePlanCharge` object was created. ", alias="CreatedDate")
    default_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The default quantity of units, such as the number of authors in a hosted wiki service. This field is required if you use a per-unit pricing model.  **Character limit**: 16  **Values**: a valid quantity value.  **Note**: When `ChargeModel` is `Tiered Pricing` or `Volume Pricing`, if this field is not specified, the value will default to `0`. ", alias="DefaultQuantity")
    deferred_revenue_account: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The name of the deferred revenue account for this charge.  This feature is in **Limited Availability**. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  ", alias="DeferredRevenueAccount")
    delivery_schedule: Optional[DeliveryScheduleProductRatePlanCharge] = Field(default=None, alias="DeliverySchedule")
    description: Optional[Annotated[str, Field(strict=True, max_length=500)]] = Field(default=None, description="A description of the charge. ", alias="Description")
    discount_level: Optional[DiscountLevel] = Field(default=None, alias="DiscountLevel")
    drawdown_rate: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  The [conversion rate](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge#UOM_Conversion) between Usage UOM and Drawdown UOM for a [drawdown charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge). Must be a positive number (>0). ", alias="DrawdownRate")
    drawdown_uom: Optional[StrictStr] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. Unit of measurement for a [drawdown charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge). ", alias="DrawdownUom")
    end_date_condition: Optional[EndDateConditionProductRatePlanChargeRest] = Field(default=EndDateConditionProductRatePlanChargeRest.SUBSCRIPTIONEND, alias="EndDateCondition")
    exclude_item_billing_from_revenue_accounting: Optional[StrictBool] = Field(default=None, description="The flag to exclude the related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.  **Notes**:    - To use this field, you must set the `X-Zuora-WSDL-Version` request header to `115` or later. Otherwise, an error occurs.   - This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="ExcludeItemBillingFromRevenueAccounting")
    exclude_item_booking_from_revenue_accounting: Optional[StrictBool] = Field(default=None, description="The flag to exclude the related rate plan charges and order line items from revenue accounting.  **Notes**:    - To use this field, you must set the `X-Zuora-WSDL-Version` request header to `115` or later. Otherwise, an error occurs.   - This field is only available if you have the Billing - Revenue Integration feature enabled.  ", alias="ExcludeItemBookingFromRevenueAccounting")
    included_units: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the number of units in the base set of units.  **Character limit**: 16  **Values**: a positive decimal value ", alias="IncludedUnits")
    is_prepaid: Optional[StrictBool] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  Indicates whether this charge is a prepayment (topup) charge or a drawdown charge. Values: `true` or `false`. ", alias="IsPrepaid")
    is_rollover: Optional[StrictBool] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  To use this field, you must set the `X-Zuora-WSDL-Version` request header to 114 or higher. Otherwise, an error occurs.  The value is either \"True\" or \"False\". It determines whether the rollover fields are needed. ", alias="IsRollover")
    is_stacked_discount: Optional[StrictBool] = Field(default=None, description="**Note**: This field is only applicable to the Discount - Percentage charge model. To use this field, you must set the `X-Zuora-WSDL-Version` request header to 130 or higher. Otherwise, an error occurs. This field indicates whether the discount is to be calculated as stacked discount. Possible values are as follows: - `true`: This is a stacked discount, which should be calculated by stacking with other discounts. - `false`: This is not a stacked discount, which should be calculated in sequence with other discounts. For more information, see [Stacked discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Products/Product_Catalog/B_Charge_Models/B_Discount_Charge_Models). ", alias="IsStackedDiscount")
    is_unbilled: Optional[StrictBool] = Field(default=None, description="This field is used to dictate how to perform the accounting during revenue recognition. **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at <a href=\"https://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>, and we will evaluate whether the feature is suitable for your use cases. ", alias="IsUnbilled")
    revenue_recognition_timing: Optional[Annotated[str, Field(strict=True, max_length=200)]] = Field(default=None, description="This field is used to dictate the type of revenue recognition timing. ", alias="RevenueRecognitionTiming")
    revenue_amortization_method: Optional[Annotated[str, Field(strict=True, max_length=200)]] = Field(default=None, description="This field is used to dictate the type of revenue amortization method. ", alias="RevenueAmortizationMethod")
    legacy_revenue_reporting: Optional[StrictBool] = Field(default=None, alias="LegacyRevenueReporting")
    list_price_base: Optional[ListPriceBase] = Field(default=None, alias="ListPriceBase")
    min_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the minimum number of units for this charge. Use this field and the `MaxQuantity` field to create a range of units allowed in a product rate plan charge.  **Character limit**: 16  **Values**: a positive decimal value ", alias="MinQuantity")
    max_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the maximum number of units for this charge. Use this field and the `MinQuantity` field to create a range of units allowed in a product rate plan charge.  **Character limit**: 16  **Values**: a positive decimal value ", alias="MaxQuantity")
    name: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The name of the product rate plan charge. ", alias="Name")
    number_of_period: Optional[StrictInt] = Field(default=None, description="Specifies the number of periods to use when calculating charges in an overage smoothing charge model. The valid value is a positive whole number. ", alias="NumberOfPeriod")
    overage_calculation_option: Optional[OverageCalculationOption] = Field(default=None, alias="OverageCalculationOption")
    overage_unused_units_credit_option: Optional[OverageUnusedUnitsCreditOption] = Field(default=None, alias="OverageUnusedUnitsCreditOption")
    prepaid_operation_type: Optional[PrepaidOperationType] = Field(default=None, alias="PrepaidOperationType")
    prepaid_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. The number of units included in a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). Must be a positive number (>0). ", alias="prepaidQuantity")
    prepaid_total_quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. The total amount of units that end customers can use during a validity period when they subscribe to a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). ", alias="prepaidTotalQuantity")
    prepaid_uom: Optional[StrictStr] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. Unit of measurement for a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). ", alias="prepaidUom")
    prepay_periods: Optional[StrictInt] = Field(default=None, description="The number of periods to which prepayment is set. **Note:** This field is only available if you already have the prepayment feature enabled.  The prepayment feature is deprecated and available only for backward compatibility. Zuora does not support enabling this feature anymore. ", alias="prepayPeriods")
    price_change_option: Optional[PriceChangeOption] = Field(default=PriceChangeOption.NOCHANGE, alias="PriceChangeOption")
    price_increase_percentage: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the percentage to increase or decrease the price of a termed subscription's renewal. Use this field if you set the value to `SpecificPercentageValue`.  **Character limit**: 16  **Values**: a decimal value between -100 and 100 ", alias="PriceIncreasePercentage")
    price_increase_option: Optional[PriceIncreaseOption] = Field(default=None, alias="PriceIncreaseOption")
    rating_group: Optional[RatingGroup] = Field(default=None, alias="RatingGroup")
    recognized_revenue_account: Optional[Annotated[str, Field(strict=True, max_length=100)]] = Field(default=None, description="The name of the recognized revenue account for this charge.   - Required when the Allow Blank Accounting Code setting is No.   - Optional when the Allow Blank Accounting Code setting is Yes.  This feature is in **Limited Availability**. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  ", alias="RecognizedRevenueAccount")
    rev_rec_code: Optional[Annotated[str, Field(strict=True, max_length=70)]] = Field(default=None, description="Associates this product rate plan charge with a specific revenue recognition code. ", alias="RevRecCode")
    rev_rec_trigger_condition: Optional[RevRecTriggerConditionProductRatePlanChargeRest] = Field(default=None, alias="RevRecTriggerCondition")
    revenue_recognition_rule_name: Optional[RevenueRecognitionRuleName] = Field(default=None, alias="RevenueRecognitionRuleName")
    rollover_apply: Optional[RolloverApply] = Field(default=None, alias="RolloverApply")
    rollover_periods: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="**Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. To use this field, you must set the `X-Zuora-WSDL-Version` request header to 114 or higher. Otherwise, an error occurs. This field defines the number of rollover periods, it is restricted to 3. ", alias="RolloverPeriods")
    smoothing_model: Optional[SmoothingModel] = Field(default=None, alias="SmoothingModel")
    specific_billing_period: Optional[StrictInt] = Field(default=None, description="Customizes the number of months or weeks for the charges billing period. This field is required if you set the value of the BillingPeriod field to `Specific Months` or `Specific Weeks`. The valid value is a positive integer. ", alias="SpecificBillingPeriod")
    specific_list_price_base: Optional[Dict[str, Any]] = Field(default=None, description="The number of months for the list price base of the charge. The value of this field is `null` if you do not set the value of the `ListPriceBase` field to `Per Specific Months`.  **Notes**:    - This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/I_Annual_List_Price\" target=\"_blank\">Annual List Price</a> feature enabled.   - To use this field, you must set the `X-Zuora-WSDL-Version` request header to `129` or later. Otherwise, an error occurs.   - The value of this field is `null` if you do not set the value of the `ListPriceBase` field to `Per Specific Months`. ", alias="SpecificListPriceBase")
    tax_code: Optional[Annotated[str, Field(strict=True, max_length=64)]] = Field(default=None, description="Specifies the tax code for taxation rules. Required when the Taxable field is set to `True`.  **Note**: This value affects the tax calculation of rate plan charges that come from the `ProductRatePlanCharge`. ", alias="TaxCode")
    tax_mode: Optional[TaxMode] = Field(default=None, alias="TaxMode")
    taxable: Optional[StrictBool] = Field(default=None, description="Determines whether the charge is taxable. When set to `True`, the TaxMode and TaxCode fields are required when creating or updating th ProductRatePlanCharge object.  **Character limit**: 5  **Values**: `True`, `False`  **Note**: This value affects the tax calculation of rate plan charges that come from the `ProductRatePlanCharge`. ", alias="Taxable")
    trigger_event: Optional[TriggerEventProductRatePlanChargeRest] = Field(default=None, alias="TriggerEvent")
    uom: Optional[Annotated[str, Field(strict=True, max_length=25)]] = Field(default=None, description="Specifies the units to measure usage.   **Note**: You must specify this field when creating the following charge models:   - Per Unit Pricing   - Volume Pricin   - Overage Pricing   - Tiered Pricing   - Tiered with Overage Pricing ", alias="UOM")
    up_to_periods: Optional[StrictInt] = Field(default=None, description="Specifies the length of the period during which the charge is active. If this period ends before the subscription ends, the charge ends when this period ends.  **Character limit**: 5  **Values**: a whole number between 0 and 65535, exclusive  **Notes**:   - You must use this field together with the `UpToPeriodsType` field to specify the time period. This field is applicable only when the `EndDateCondition` field is set to `FixedPeriod`.    - If the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge end date will change accordingly up to the original period end. ", alias="UpToPeriods")
    up_to_periods_type: Optional[UpToPeriodsTypeProductRatePlanChargeRest] = Field(default=UpToPeriodsTypeProductRatePlanChargeRest.BILLING_PERIODS, alias="UpToPeriodsType")
    updated_by_id: Optional[Annotated[str, Field(strict=True, max_length=32)]] = Field(default=None, description="The ID of the last user to update the object. ", alias="UpdatedById")
    updated_date: Optional[datetime] = Field(default=None, description="The date when the object was last updated. ", alias="UpdatedDate")
    usage_record_rating_option: Optional[UsageRecordRatingOption] = Field(default=None, alias="UsageRecordRatingOption")
    use_discount_specific_accounting_code: Optional[StrictBool] = Field(default=None, description="Determines whether to define a new accounting code for the new discount charge.  **Character limit**: 5  **Values**: `True`, `False` ", alias="UseDiscountSpecificAccountingCode")
    use_tenant_default_for_price_change: Optional[StrictBool] = Field(default=None, description="Applies the tenant-level percentage uplift value for an automatic price change to a termed subscription's renewal.   **Character limit**: 5  **Values**: `true`, `false` ", alias="UseTenantDefaultForPriceChange")
    validity_period_type: Optional[ValidityPeriodType] = Field(default=None, alias="ValidityPeriodType")
    weekly_bill_cycle_day: Optional[WeeklyBillCycleDay] = Field(default=None, alias="WeeklyBillCycleDay")
    rating_groups_operator_type: Optional[RatingGroupsOperatorType] = Field(default=None, alias="RatingGroupsOperatorType")
    class__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Class associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="Class__NS")
    deferred_rev_account__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Deferrred revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="DeferredRevAccount__NS")
    department__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Department associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="Department__NS")
    include_children__ns: Optional[StrictStr] = Field(default=None, alias="IncludeChildren__NS")
    integration_id__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationId__NS")
    integration_status__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Status of the product rate plan charge's synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="IntegrationStatus__NS")
    item_type__ns: Optional[StrictStr] = Field(default=None, alias="ItemType__NS")
    location__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Location associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="Location__NS")
    recognized_rev_account__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Recognized revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="RecognizedRevAccount__NS")
    rev_rec_end__ns: Optional[StrictStr] = Field(default=None, alias="RevRecEnd__NS")
    rev_rec_start__ns: Optional[StrictStr] = Field(default=None, alias="RevRecStart__NS")
    rev_rec_template_type__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="RevRecTemplateType__NS")
    subsidiary__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Subsidiary associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="Subsidiary__NS")
    sync_date__ns: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="Date when the product rate plan charge was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId=265). ", alias="SyncDate__NS")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["Id", "ProductRatePlanId", "AccountingCode", "ApplyDiscountTo", "BillCycleDay", "BillCycleType", "BillingPeriod", "BillingPeriodAlignment", "BillingTiming", "ChargeFunction", "ChargeModel", "ChargeModelConfiguration", "ChargeType", "CommitmentType", "CreatedById", "CreatedDate", "DefaultQuantity", "DeferredRevenueAccount", "DeliverySchedule", "Description", "DiscountLevel", "DrawdownRate", "DrawdownUom", "EndDateCondition", "ExcludeItemBillingFromRevenueAccounting", "ExcludeItemBookingFromRevenueAccounting", "IncludedUnits", "IsPrepaid", "IsRollover", "IsStackedDiscount", "IsUnbilled", "RevenueRecognitionTiming", "RevenueAmortizationMethod", "LegacyRevenueReporting", "ListPriceBase", "MinQuantity", "MaxQuantity", "Name", "NumberOfPeriod", "OverageCalculationOption", "OverageUnusedUnitsCreditOption", "PrepaidOperationType", "prepaidQuantity", "prepaidTotalQuantity", "prepaidUom", "prepayPeriods", "PriceChangeOption", "PriceIncreasePercentage", "PriceIncreaseOption", "RatingGroup", "RecognizedRevenueAccount", "RevRecCode", "RevRecTriggerCondition", "RevenueRecognitionRuleName", "RolloverApply", "RolloverPeriods", "SmoothingModel", "SpecificBillingPeriod", "SpecificListPriceBase", "TaxCode", "TaxMode", "Taxable", "TriggerEvent", "UOM", "UpToPeriods", "UpToPeriodsType", "UpdatedById", "UpdatedDate", "UsageRecordRatingOption", "UseDiscountSpecificAccountingCode", "UseTenantDefaultForPriceChange", "ValidityPeriodType", "WeeklyBillCycleDay", "RatingGroupsOperatorType", "Class__NS", "DeferredRevAccount__NS", "Department__NS", "IncludeChildren__NS", "IntegrationId__NS", "IntegrationStatus__NS", "ItemType__NS", "Location__NS", "RecognizedRevAccount__NS", "RevRecEnd__NS", "RevRecStart__NS", "RevRecTemplateType__NS", "Subsidiary__NS", "SyncDate__NS"]

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
        """Create an instance of GetProductRatePlanChargeResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of charge_model_configuration
        if self.charge_model_configuration:
            _dict['ChargeModelConfiguration'] = self.charge_model_configuration.to_dict()
        # override the default output from pydantic by calling `to_dict()` of delivery_schedule
        if self.delivery_schedule:
            _dict['DeliverySchedule'] = self.delivery_schedule.to_dict()
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of GetProductRatePlanChargeResponse from a dict"""
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
            "Id": obj.get("Id"),
            "ProductRatePlanId": obj.get("ProductRatePlanId"),
            "AccountingCode": obj.get("AccountingCode"),
            "ApplyDiscountTo": obj.get("ApplyDiscountTo"),
            "BillCycleDay": obj.get("BillCycleDay"),
            "BillCycleType": obj.get("BillCycleType"),
            "BillingPeriod": obj.get("BillingPeriod"),
            "BillingPeriodAlignment": obj.get("BillingPeriodAlignment"),
            "BillingTiming": obj.get("BillingTiming"),
            "ChargeFunction": obj.get("ChargeFunction"),
            "ChargeModel": obj.get("ChargeModel"),
            "ChargeModelConfiguration": ChargeModelConfiguration.from_dict(obj["ChargeModelConfiguration"]) if obj.get("ChargeModelConfiguration") is not None else None,
            "ChargeType": obj.get("ChargeType"),
            "CommitmentType": obj.get("CommitmentType"),
            "CreatedById": obj.get("CreatedById"),
            "CreatedDate": obj.get("CreatedDate"),
            "DefaultQuantity": obj.get("DefaultQuantity"),
            "DeferredRevenueAccount": obj.get("DeferredRevenueAccount"),
            "DeliverySchedule": DeliveryScheduleProductRatePlanCharge.from_dict(obj["DeliverySchedule"]) if obj.get("DeliverySchedule") is not None else None,
            "Description": obj.get("Description"),
            "DiscountLevel": obj.get("DiscountLevel"),
            "DrawdownRate": obj.get("DrawdownRate"),
            "DrawdownUom": obj.get("DrawdownUom"),
            "EndDateCondition": obj.get("EndDateCondition") if obj.get("EndDateCondition") is not None else EndDateConditionProductRatePlanChargeRest.SUBSCRIPTIONEND,
            "ExcludeItemBillingFromRevenueAccounting": obj.get("ExcludeItemBillingFromRevenueAccounting"),
            "ExcludeItemBookingFromRevenueAccounting": obj.get("ExcludeItemBookingFromRevenueAccounting"),
            "IncludedUnits": obj.get("IncludedUnits"),
            "IsPrepaid": obj.get("IsPrepaid"),
            "IsRollover": obj.get("IsRollover"),
            "IsStackedDiscount": obj.get("IsStackedDiscount"),
            "IsUnbilled": obj.get("IsUnbilled"),
            "RevenueRecognitionTiming": obj.get("RevenueRecognitionTiming"),
            "RevenueAmortizationMethod": obj.get("RevenueAmortizationMethod"),
            "LegacyRevenueReporting": obj.get("LegacyRevenueReporting"),
            "ListPriceBase": obj.get("ListPriceBase"),
            "MinQuantity": obj.get("MinQuantity"),
            "MaxQuantity": obj.get("MaxQuantity"),
            "Name": obj.get("Name"),
            "NumberOfPeriod": obj.get("NumberOfPeriod"),
            "OverageCalculationOption": obj.get("OverageCalculationOption"),
            "OverageUnusedUnitsCreditOption": obj.get("OverageUnusedUnitsCreditOption"),
            "PrepaidOperationType": obj.get("PrepaidOperationType"),
            "prepaidQuantity": obj.get("prepaidQuantity"),
            "prepaidTotalQuantity": obj.get("prepaidTotalQuantity"),
            "prepaidUom": obj.get("prepaidUom"),
            "prepayPeriods": obj.get("prepayPeriods"),
            "PriceChangeOption": obj.get("PriceChangeOption") if obj.get("PriceChangeOption") is not None else PriceChangeOption.NOCHANGE,
            "PriceIncreasePercentage": obj.get("PriceIncreasePercentage"),
            "PriceIncreaseOption": obj.get("PriceIncreaseOption"),
            "RatingGroup": obj.get("RatingGroup"),
            "RecognizedRevenueAccount": obj.get("RecognizedRevenueAccount"),
            "RevRecCode": obj.get("RevRecCode"),
            "RevRecTriggerCondition": obj.get("RevRecTriggerCondition"),
            "RevenueRecognitionRuleName": obj.get("RevenueRecognitionRuleName"),
            "RolloverApply": obj.get("RolloverApply"),
            "RolloverPeriods": obj.get("RolloverPeriods"),
            "SmoothingModel": obj.get("SmoothingModel"),
            "SpecificBillingPeriod": obj.get("SpecificBillingPeriod"),
            "SpecificListPriceBase": obj.get("SpecificListPriceBase"),
            "TaxCode": obj.get("TaxCode"),
            "TaxMode": obj.get("TaxMode"),
            "Taxable": obj.get("Taxable"),
            "TriggerEvent": obj.get("TriggerEvent"),
            "UOM": obj.get("UOM"),
            "UpToPeriods": obj.get("UpToPeriods"),
            "UpToPeriodsType": obj.get("UpToPeriodsType") if obj.get("UpToPeriodsType") is not None else UpToPeriodsTypeProductRatePlanChargeRest.BILLING_PERIODS,
            "UpdatedById": obj.get("UpdatedById"),
            "UpdatedDate": obj.get("UpdatedDate"),
            "UsageRecordRatingOption": obj.get("UsageRecordRatingOption"),
            "UseDiscountSpecificAccountingCode": obj.get("UseDiscountSpecificAccountingCode"),
            "UseTenantDefaultForPriceChange": obj.get("UseTenantDefaultForPriceChange"),
            "ValidityPeriodType": obj.get("ValidityPeriodType"),
            "WeeklyBillCycleDay": obj.get("WeeklyBillCycleDay"),
            "RatingGroupsOperatorType": obj.get("RatingGroupsOperatorType"),
            "Class__NS": obj.get("Class__NS"),
            "DeferredRevAccount__NS": obj.get("DeferredRevAccount__NS"),
            "Department__NS": obj.get("Department__NS"),
            "IncludeChildren__NS": obj.get("IncludeChildren__NS"),
            "IntegrationId__NS": obj.get("IntegrationId__NS"),
            "IntegrationStatus__NS": obj.get("IntegrationStatus__NS"),
            "ItemType__NS": obj.get("ItemType__NS"),
            "Location__NS": obj.get("Location__NS"),
            "RecognizedRevAccount__NS": obj.get("RecognizedRevAccount__NS"),
            "RevRecEnd__NS": obj.get("RevRecEnd__NS"),
            "RevRecStart__NS": obj.get("RevRecStart__NS"),
            "RevRecTemplateType__NS": obj.get("RevRecTemplateType__NS"),
            "Subsidiary__NS": obj.get("Subsidiary__NS"),
            "SyncDate__NS": obj.get("SyncDate__NS")
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
