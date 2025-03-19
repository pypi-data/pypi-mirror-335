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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, ClassVar, Dict, List, Optional
from zuora_sdk.models.setting_component_key_value import SettingComponentKeyValue
from typing import Optional, Set
from typing_extensions import Self

class SettingSourceComponent(BaseModel):
    """
    Provides details about the different components that need to be compared and deployed.
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

    custom_fields: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="customFields")
    custom_objects: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="customObjects")
    data_access_control: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="dataAccessControl")
    notifications: Optional[List[SettingComponentKeyValue]] = None
    product_catalog: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="productCatalog")
    settings: Optional[List[SettingComponentKeyValue]] = None
    workflows: Optional[List[SettingComponentKeyValue]] = None
    user_roles: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="userRoles")
    taxation: Optional[List[SettingComponentKeyValue]] = None
    billing_documents: Optional[List[SettingComponentKeyValue]] = Field(default=None, alias="billingDocuments")
    reporting: Optional[List[SettingComponentKeyValue]] = None
    revenue: Optional[List[SettingComponentKeyValue]] = None
    mediation: Optional[List[SettingComponentKeyValue]] = None
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["customFields", "customObjects", "dataAccessControl", "notifications", "productCatalog", "settings", "workflows", "userRoles", "taxation", "billingDocuments", "reporting", "revenue", "mediation"]

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
        """Create an instance of SettingSourceComponent from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in custom_fields (list)
        _items = []
        if self.custom_fields:
            for _item_custom_fields in self.custom_fields:
                if _item_custom_fields:
                    _items.append(_item_custom_fields.to_dict())
            _dict['customFields'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in custom_objects (list)
        _items = []
        if self.custom_objects:
            for _item_custom_objects in self.custom_objects:
                if _item_custom_objects:
                    _items.append(_item_custom_objects.to_dict())
            _dict['customObjects'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in data_access_control (list)
        _items = []
        if self.data_access_control:
            for _item_data_access_control in self.data_access_control:
                if _item_data_access_control:
                    _items.append(_item_data_access_control.to_dict())
            _dict['dataAccessControl'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in notifications (list)
        _items = []
        if self.notifications:
            for _item_notifications in self.notifications:
                if _item_notifications:
                    _items.append(_item_notifications.to_dict())
            _dict['notifications'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in product_catalog (list)
        _items = []
        if self.product_catalog:
            for _item_product_catalog in self.product_catalog:
                if _item_product_catalog:
                    _items.append(_item_product_catalog.to_dict())
            _dict['productCatalog'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in settings (list)
        _items = []
        if self.settings:
            for _item_settings in self.settings:
                if _item_settings:
                    _items.append(_item_settings.to_dict())
            _dict['settings'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in workflows (list)
        _items = []
        if self.workflows:
            for _item_workflows in self.workflows:
                if _item_workflows:
                    _items.append(_item_workflows.to_dict())
            _dict['workflows'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in user_roles (list)
        _items = []
        if self.user_roles:
            for _item_user_roles in self.user_roles:
                if _item_user_roles:
                    _items.append(_item_user_roles.to_dict())
            _dict['userRoles'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in taxation (list)
        _items = []
        if self.taxation:
            for _item_taxation in self.taxation:
                if _item_taxation:
                    _items.append(_item_taxation.to_dict())
            _dict['taxation'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in billing_documents (list)
        _items = []
        if self.billing_documents:
            for _item_billing_documents in self.billing_documents:
                if _item_billing_documents:
                    _items.append(_item_billing_documents.to_dict())
            _dict['billingDocuments'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in reporting (list)
        _items = []
        if self.reporting:
            for _item_reporting in self.reporting:
                if _item_reporting:
                    _items.append(_item_reporting.to_dict())
            _dict['reporting'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in revenue (list)
        _items = []
        if self.revenue:
            for _item_revenue in self.revenue:
                if _item_revenue:
                    _items.append(_item_revenue.to_dict())
            _dict['revenue'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in mediation (list)
        _items = []
        if self.mediation:
            for _item_mediation in self.mediation:
                if _item_mediation:
                    _items.append(_item_mediation.to_dict())
            _dict['mediation'] = _items
        # puts key-value pairs in additional_properties in the top level
        if self.additional_properties is not None:
            for _key, _value in self.additional_properties.items():
                _dict[_key] = _value

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SettingSourceComponent from a dict"""
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
            "customFields": [SettingComponentKeyValue.from_dict(_item) for _item in obj["customFields"]] if obj.get("customFields") is not None else None,
            "customObjects": [SettingComponentKeyValue.from_dict(_item) for _item in obj["customObjects"]] if obj.get("customObjects") is not None else None,
            "dataAccessControl": [SettingComponentKeyValue.from_dict(_item) for _item in obj["dataAccessControl"]] if obj.get("dataAccessControl") is not None else None,
            "notifications": [SettingComponentKeyValue.from_dict(_item) for _item in obj["notifications"]] if obj.get("notifications") is not None else None,
            "productCatalog": [SettingComponentKeyValue.from_dict(_item) for _item in obj["productCatalog"]] if obj.get("productCatalog") is not None else None,
            "settings": [SettingComponentKeyValue.from_dict(_item) for _item in obj["settings"]] if obj.get("settings") is not None else None,
            "workflows": [SettingComponentKeyValue.from_dict(_item) for _item in obj["workflows"]] if obj.get("workflows") is not None else None,
            "userRoles": [SettingComponentKeyValue.from_dict(_item) for _item in obj["userRoles"]] if obj.get("userRoles") is not None else None,
            "taxation": [SettingComponentKeyValue.from_dict(_item) for _item in obj["taxation"]] if obj.get("taxation") is not None else None,
            "billingDocuments": [SettingComponentKeyValue.from_dict(_item) for _item in obj["billingDocuments"]] if obj.get("billingDocuments") is not None else None,
            "reporting": [SettingComponentKeyValue.from_dict(_item) for _item in obj["reporting"]] if obj.get("reporting") is not None else None,
            "revenue": [SettingComponentKeyValue.from_dict(_item) for _item in obj["revenue"]] if obj.get("revenue") is not None else None,
            "mediation": [SettingComponentKeyValue.from_dict(_item) for _item in obj["mediation"]] if obj.get("mediation") is not None else None
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
