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
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from zuora_sdk.models.account_summary_rate_plan import AccountSummaryRatePlan
from typing import Optional, Set
from typing_extensions import Self

class AccountSummarySubscription(BaseModel):
    """
    AccountSummarySubscription
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
    auto_renew: Optional[StrictBool] = Field(default=None, description="If `true`, auto-renew is enabled. If `false`, auto-renew is disabled. ", alias="autoRenew")
    id: Optional[StrictStr] = Field(default=None, description="Subscription ID. ")
    initial_term: Optional[StrictStr] = Field(default=None, description="Duration of the initial subscription term in whole months.  ", alias="initialTerm")
    rate_plans: Optional[List[AccountSummaryRatePlan]] = Field(default=None, description="Container for rate plans for this subscription. ", alias="ratePlans")
    renewal_term: Optional[StrictStr] = Field(default=None, description="Duration of the renewal term in whole months. ", alias="renewalTerm")
    status: Optional[StrictStr] = Field(default=None, description="Subscription status; possible values are: `Draft`, `PendingActivation`, `PendingAcceptance`, `Active`, `Cancelled`, `Expired`. ")
    subscription_number: Optional[StrictStr] = Field(default=None, description="Subscription Number. ", alias="subscriptionNumber")
    subscription_start_date: Optional[date] = Field(default=None, description="Subscription start date. ", alias="subscriptionStartDate")
    term_end_date: Optional[date] = Field(default=None, description="End date of the subscription term. If the subscription is evergreen, this is either null or equal to the cancellation date, as appropriate. ", alias="termEndDate")
    term_start_date: Optional[date] = Field(default=None, description="Start date of the subscription term. If this is a renewal subscription, this date is different than the subscription start date. ", alias="termStartDate")
    term_type: Optional[StrictStr] = Field(default=None, description="Possible values are: `TERMED`, `EVERGREEN`. ", alias="termType")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["CpqBundleJsonId__QT", "OpportunityCloseDate__QT", "OpportunityName__QT", "QuoteBusinessType__QT", "QuoteNumber__QT", "QuoteType__QT", "IntegrationId__NS", "IntegrationStatus__NS", "Project__NS", "SalesOrder__NS", "SyncDate__NS", "autoRenew", "id", "initialTerm", "ratePlans", "renewalTerm", "status", "subscriptionNumber", "subscriptionStartDate", "termEndDate", "termStartDate", "termType"]

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
        """Create an instance of AccountSummarySubscription from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in rate_plans (list)
        _items = []
        if self.rate_plans:
            for _item_rate_plans in self.rate_plans:
                if _item_rate_plans:
                    _items.append(_item_rate_plans.to_dict())
            _dict['ratePlans'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AccountSummarySubscription from a dict"""
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
            "autoRenew": obj.get("autoRenew"),
            "id": obj.get("id"),
            "initialTerm": obj.get("initialTerm"),
            "ratePlans": [AccountSummaryRatePlan.from_dict(_item) for _item in obj["ratePlans"]] if obj.get("ratePlans") is not None else None,
            "renewalTerm": obj.get("renewalTerm"),
            "status": obj.get("status"),
            "subscriptionNumber": obj.get("subscriptionNumber"),
            "subscriptionStartDate": obj.get("subscriptionStartDate"),
            "termEndDate": obj.get("termEndDate"),
            "termStartDate": obj.get("termStartDate"),
            "termType": obj.get("termType")
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
