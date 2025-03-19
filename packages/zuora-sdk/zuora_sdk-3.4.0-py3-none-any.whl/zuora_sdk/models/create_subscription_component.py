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
from zuora_sdk.models.charge_model_configuration_for_subscription import ChargeModelConfigurationForSubscription
from zuora_sdk.models.tier import Tier
from typing import Optional, Set
from typing_extensions import Self

class CreateSubscriptionComponent(BaseModel):
    """
    CreateSubscriptionComponent
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

    amended_by_order_on: Optional[StrictStr] = Field(default=None, description="The date when the rate plan charge is amended through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue. ", alias="amendedByOrderOn")
    apply_discount_to: Optional[StrictStr] = Field(default=None, description="Specifies the type of charges that you want a specific discount to apply to.  Values:  * `ONETIME` * `RECURRING` * `USAGE` * `ONETIMERECURRING` * `ONETIMEUSAGE` * `RECURRINGUSAGE` * `ONETIMERECURRINGUSAGE` ", alias="applyDiscountTo")
    bill_cycle_day: Optional[StrictStr] = Field(default=None, description="Sets the bill cycle day (BCD) for the charge. The BCD determines which day of the month the customer is billed.  Values: `1`-`31` ", alias="billCycleDay")
    bill_cycle_type: Optional[StrictStr] = Field(default=None, description="Specifies how to determine the billing day for the charge. When this field is set to `SpecificDayofMonth`, set the `BillCycleDay` field. When this field is set to `SpecificDayofWeek`, set the `weeklyBillCycleDay` field.  Values:  * `DefaultFromCustomer` * `SpecificDayofMonth` * `SubscriptionStartDay` * `ChargeTriggerDay` * `SpecificDayofWeek` ", alias="billCycleType")
    billing_period: Optional[StrictStr] = Field(default=None, description="Billing period for the charge. The start day of the billing period is also called the bill cycle day (BCD). Values:  * `Month` * `Quarter` * `Semi_Annual` * `Annual` * `Eighteen_Months` * `Two_Years` * `Three_Years` * `Five_Years` * `Specific_Months` * `Subscription_Term` * `Week` * `Specific_Weeks` ", alias="billingPeriod")
    billing_period_alignment: Optional[StrictStr] = Field(default=None, description="Aligns charges within the same subscription if multiple charges begin on different dates.  Values:  * `AlignToCharge` * `AlignToSubscriptionStart` * `AlignToTermStart` ", alias="billingPeriodAlignment")
    billing_timing: Optional[StrictStr] = Field(default=None, description="Billing timing for the charge for recurring charge types. Not avaliable for one time, usage, and discount charges.  Values:  * `IN_ADVANCE` (default) * `IN_ARREARS` ", alias="billingTiming")
    charge_model_configuration: Optional[ChargeModelConfigurationForSubscription] = Field(default=None, alias="chargeModelConfiguration")
    description: Optional[StrictStr] = Field(default=None, description="Description of the charge. ")
    discount_amount: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the amount of fixed-amount discount. ", alias="discountAmount")
    discount_level: Optional[StrictStr] = Field(default=None, description="Specifies if the discount applies to the product rate plan only, the entire subscription, or to any activity in the account.  Values:  * `rateplan` * `subscription` * `account` ", alias="discountLevel")
    discount_percentage: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Percentage of discount for a percentage discount.  ", alias="discountPercentage")
    end_date_condition: Optional[StrictStr] = Field(default=None, description="Defines when the charge ends after the charge trigger date. If the subscription ends before the charge end date, the charge ends when the subscription ends. But if the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge will end on the charge end date.  Values:  * `Subscription_End` * `Fixed_Period` * `Specific_End_Date` * `One_Time` ", alias="endDateCondition")
    exclude_item_billing_from_revenue_accounting: Optional[StrictBool] = Field(default=None, description="The flag to exclude rate plan charge related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled. ", alias="excludeItemBillingFromRevenueAccounting")
    exclude_item_booking_from_revenue_accounting: Optional[StrictBool] = Field(default=None, description="The flag to exclude rate plan charges from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled. ", alias="excludeItemBookingFromRevenueAccounting")
    included_units: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the number of units in the base set of units for this charge. Must be >=`0`. ", alias="includedUnits")
    is_allocation_eligible: Optional[StrictBool] = Field(default=None, description="This field is used to identify if the charge segment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at <a href=\"https://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>, and we will evaluate whether the feature is suitable for your use cases. ", alias="isAllocationEligible")
    is_unbilled: Optional[StrictBool] = Field(default=None, description="This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at <a href=\"https://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>, and we will evaluate whether the feature is suitable for your use cases. ", alias="isUnbilled")
    list_price_base: Optional[StrictStr] = Field(default=None, description="The list price base for the product rate plan charge.  Values:  * `Per_Billing_Period` * `Per_Month` * `Per_Week` * `Per_Year` * `Per_Specific_Months` ", alias="listPriceBase")
    number: Optional[StrictStr] = Field(default=None, description="Unique number that identifies the charge. Max 50 characters. System-generated if not provided. ")
    number_of_periods: Optional[StrictInt] = Field(default=None, description="Specifies the number of periods to use when calculating charges in an overage smoothing charge model. ", alias="numberOfPeriods")
    original_order_date: Optional[date] = Field(default=None, description="The date when the rate plan charge is created through an order or amendment. This field is not updatable.  This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue. ", alias="originalOrderDate")
    overage_price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Price for units over the allowed amount. ", alias="overagePrice")
    overage_unused_units_credit_option: Optional[StrictStr] = Field(default=None, description="Determines whether to credit the customer with unused units of usage.  Values:  * `NoCredit` * `CreditBySpecificRate` ", alias="overageUnusedUnitsCreditOption")
    price: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Price for units in the subscription rate plan. ")
    price_change_option: Optional[StrictStr] = Field(default=None, description="Applies an automatic price change when a termed subscription is renewed. The Billing Admin setting **Enable Automatic Price Change When Subscriptions are Renewed?** must be set to Yes to use this field. Values:  * `NoChange` (default) * `SpecificPercentageValue` * `UseLatestProductCatalogPricing` ", alias="priceChangeOption")
    price_increase_percentage: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the percentage to increase or decrease the price of a termed subscription's renewal. Required if you set the `PriceChangeOption` field to `SpecificPercentageValue`.   Value must be a decimal between `-100` and `100`. ", alias="priceIncreasePercentage")
    product_rate_plan_charge_id: StrictStr = Field(description="ID of a product rate-plan charge for this subscription. ", alias="productRatePlanChargeId")
    product_rate_plan_charge_number: Optional[StrictStr] = Field(default=None, description="Number of a product rate-plan charge for this subscription. ", alias="productRatePlanChargeNumber")
    quantity: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Number of units. Must be a decimal >=`0`.   When using `chargeOverrides` for creating subscriptions with recurring charge types, the `quantity` field must be populated when the charge model is \"Tiered Pricing\" or \"Volume Pricing\". It is not required for \"Flat Fee Pricing\" charge model. ")
    rating_group: Optional[StrictStr] = Field(default=None, description="Specifies a rating group based on which usage records are rated.  Possible values:  - `ByBillingPeriod` (default): The rating is based on all the usages in a billing period. - `ByUsageStartDate`: The rating is based on all the usages on the same usage start date.  - `ByUsageRecord`: The rating is based on each usage record. - `ByUsageUpload`: The rating is based on all the  usages in a uploaded usage file (`.xls` or `.csv`). - `ByGroupId`: The rating is based on all the usages in a custom group.  **Note:**  - The `ByBillingPeriod` value can be applied for all charge models.  - The `ByUsageStartDate`, `ByUsageRecord`, and `ByUsageUpload` values can only be applied for per unit, volume pricing, and tiered pricing charge models.  - The `ByGroupId` value is only available if you have the Active Rating feature enabled. - Use this field only for Usage charges. One-Time Charges and Recurring Charges return `NULL`. ", alias="ratingGroup")
    specific_billing_period: Optional[StrictInt] = Field(default=None, description="Specifies the number of month or week for the charges billing period. Required if you set the value of the `billingPeriod` field to `Specific_Months` or `Specific_Weeks`. ", alias="specificBillingPeriod")
    specific_end_date: Optional[date] = Field(default=None, description="Defines when the charge ends after the charge trigger date.  **note:**  * This field is only applicable when the `endDateCondition` field is set to `Specific_End_Date`.  * If the subscription ends before the specific end date, the charge ends when the subscription ends. But if the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge will end on the specific end date. ", alias="specificEndDate")
    specific_list_price_base: Optional[Annotated[int, Field(le=200, strict=True, ge=1)]] = Field(default=None, description="The number of months for the list price base of the charge. This field is required if you set the value of the `listPriceBase` field to `Per_Specific_Months`.  **Note**:    - This field is available only if you have the <a href=\"https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/I_Annual_List_Price\" target=\"_blank\">Annual List Price</a> feature enabled.   - The value of this field is `null` if you do not set the value of the `listPriceBase` field to `Per_Specific_Months`. ", alias="specificListPriceBase")
    tiers: Optional[List[Tier]] = Field(default=None, description="Container for Volume, Tiered, or Tiered with Overage charge models. Supports the following charge types:  * One-time * Recurring * Usage-based ")
    trigger_date: Optional[date] = Field(default=None, description="Specifies when to start billing the customer for the charge. Required if the `triggerEvent` field is set to `USD`. ", alias="triggerDate")
    trigger_event: Optional[StrictStr] = Field(default=None, description="Specifies when to start billing the customer for the charge.  Values:  * `UCE` * `USA` * `UCA` * `USD` ", alias="triggerEvent")
    unused_units_credit_rates: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="Specifies the rate to credit a customer for unused units of usage. This field applies only for overage charge models when the `OverageUnusedUnitsCreditOption` field is set to `CreditBySpecificRate`. ", alias="unusedUnitsCreditRates")
    up_to_periods: Optional[StrictInt] = Field(default=None, description="Specifies the length of the period during which the charge is active. If this period ends before the subscription ends, the charge ends when this period ends.  **Note:** You must use this field together with the `upToPeriodsType` field to specify the time period.  * This field is applicable only when the `endDateCondition` field is set to `Fixed_Period`.  * If the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge end date will change accordingly up to the original period end. ", alias="upToPeriods")
    up_to_periods_type: Optional[StrictStr] = Field(default=None, description=" The period type used to define when the charge ends.   Values:  * `Billing_Periods` * `Days` * `Weeks` * `Months` * `Years`  You must use this field together with the `upToPeriods` field to specify the time period.  This field is applicable only when the `endDateCondition` field is set to `Fixed_Period`.  ", alias="upToPeriodsType")
    weekly_bill_cycle_day: Optional[StrictStr] = Field(default=None, description="Specifies which day of the week is the bill cycle day (BCD) for the charge.   Values:  * `Sunday` * `Monday` * `Tuesday` * `Wednesday` * `Thursday` * `Friday` * `Saturday` ", alias="weeklyBillCycleDay")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["amendedByOrderOn", "applyDiscountTo", "billCycleDay", "billCycleType", "billingPeriod", "billingPeriodAlignment", "billingTiming", "chargeModelConfiguration", "description", "discountAmount", "discountLevel", "discountPercentage", "endDateCondition", "excludeItemBillingFromRevenueAccounting", "excludeItemBookingFromRevenueAccounting", "includedUnits", "isAllocationEligible", "isUnbilled", "listPriceBase", "number", "numberOfPeriods", "originalOrderDate", "overagePrice", "overageUnusedUnitsCreditOption", "price", "priceChangeOption", "priceIncreasePercentage", "productRatePlanChargeId", "productRatePlanChargeNumber", "quantity", "ratingGroup", "specificBillingPeriod", "specificEndDate", "specificListPriceBase", "tiers", "triggerDate", "triggerEvent", "unusedUnitsCreditRates", "upToPeriods", "upToPeriodsType", "weeklyBillCycleDay"]

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
        """Create an instance of CreateSubscriptionComponent from a JSON string"""
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
            _dict['chargeModelConfiguration'] = self.charge_model_configuration.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in tiers (list)
        _items = []
        if self.tiers:
            for _item_tiers in self.tiers:
                if _item_tiers:
                    _items.append(_item_tiers.to_dict())
            _dict['tiers'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of CreateSubscriptionComponent from a dict"""
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
            "amendedByOrderOn": obj.get("amendedByOrderOn"),
            "applyDiscountTo": obj.get("applyDiscountTo"),
            "billCycleDay": obj.get("billCycleDay"),
            "billCycleType": obj.get("billCycleType"),
            "billingPeriod": obj.get("billingPeriod"),
            "billingPeriodAlignment": obj.get("billingPeriodAlignment"),
            "billingTiming": obj.get("billingTiming"),
            "chargeModelConfiguration": ChargeModelConfigurationForSubscription.from_dict(obj["chargeModelConfiguration"]) if obj.get("chargeModelConfiguration") is not None else None,
            "description": obj.get("description"),
            "discountAmount": obj.get("discountAmount"),
            "discountLevel": obj.get("discountLevel"),
            "discountPercentage": obj.get("discountPercentage"),
            "endDateCondition": obj.get("endDateCondition"),
            "excludeItemBillingFromRevenueAccounting": obj.get("excludeItemBillingFromRevenueAccounting"),
            "excludeItemBookingFromRevenueAccounting": obj.get("excludeItemBookingFromRevenueAccounting"),
            "includedUnits": obj.get("includedUnits"),
            "isAllocationEligible": obj.get("isAllocationEligible"),
            "isUnbilled": obj.get("isUnbilled"),
            "listPriceBase": obj.get("listPriceBase"),
            "number": obj.get("number"),
            "numberOfPeriods": obj.get("numberOfPeriods"),
            "originalOrderDate": obj.get("originalOrderDate"),
            "overagePrice": obj.get("overagePrice"),
            "overageUnusedUnitsCreditOption": obj.get("overageUnusedUnitsCreditOption"),
            "price": obj.get("price"),
            "priceChangeOption": obj.get("priceChangeOption"),
            "priceIncreasePercentage": obj.get("priceIncreasePercentage"),
            "productRatePlanChargeId": obj.get("productRatePlanChargeId"),
            "productRatePlanChargeNumber": obj.get("productRatePlanChargeNumber"),
            "quantity": obj.get("quantity"),
            "ratingGroup": obj.get("ratingGroup"),
            "specificBillingPeriod": obj.get("specificBillingPeriod"),
            "specificEndDate": obj.get("specificEndDate"),
            "specificListPriceBase": obj.get("specificListPriceBase"),
            "tiers": [Tier.from_dict(_item) for _item in obj["tiers"]] if obj.get("tiers") is not None else None,
            "triggerDate": obj.get("triggerDate"),
            "triggerEvent": obj.get("triggerEvent"),
            "unusedUnitsCreditRates": obj.get("unusedUnitsCreditRates"),
            "upToPeriods": obj.get("upToPeriods"),
            "upToPeriodsType": obj.get("upToPeriodsType"),
            "weeklyBillCycleDay": obj.get("weeklyBillCycleDay")
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
