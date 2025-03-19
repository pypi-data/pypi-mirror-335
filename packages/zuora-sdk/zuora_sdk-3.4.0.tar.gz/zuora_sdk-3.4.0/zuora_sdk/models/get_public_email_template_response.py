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
from zuora_sdk.models.get_public_email_template_response_cc_email_type import GetPublicEmailTemplateResponseCcEmailType
from typing import Optional, Set
from typing_extensions import Self

class GetPublicEmailTemplateResponse(BaseModel):
    """
    GetPublicEmailTemplateResponse
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

    active: Optional[StrictBool] = Field(default=None, description="The status of the email template.")
    bcc_email_address: Optional[StrictStr] = Field(default=None, description="Email BCC address.", alias="bccEmailAddress")
    cc_email_address: Optional[StrictStr] = Field(default=None, description="Email CC address.", alias="ccEmailAddress")
    cc_email_type: Optional[GetPublicEmailTemplateResponseCcEmailType] = Field(default=GetPublicEmailTemplateResponseCcEmailType.SPECIFICEMAILS, alias="ccEmailType")
    created_by: Optional[StrictStr] = Field(default=None, description="The ID of the user who created the email template.", alias="createdBy")
    created_on: Optional[datetime] = Field(default=None, description="The time when the email template was created. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00", alias="createdOn")
    description: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The description of the email template.")
    email_body: Optional[StrictStr] = Field(default=None, description="The email body. You can add merge fields in the email object using angle brackets.  User can also embed html tags if `isHtml` is `true`.", alias="emailBody")
    email_subject: Optional[StrictStr] = Field(default=None, description="The email subject. You can add merge fields in the email subject using angle brackets.", alias="emailSubject")
    encoding_type: Optional[StrictStr] = Field(default=None, alias="encodingType")
    event_category: Optional[Union[StrictFloat, StrictInt]] = Field(default=None, description="The event category code for a standard event. See [Standard Event Categories](https://knowledgecenter.zuora.com/Central_Platform/Notifications/A_Standard_Events/Standard_Event_Category_Code_for_Notification_Histories_API) for all event category codes.", alias="eventCategory")
    event_type_name: Optional[Annotated[str, Field(min_length=1, strict=True)]] = Field(default=None, description="The name of the custom event or custom scheduled event.", alias="eventTypeName")
    event_type_namespace: Optional[StrictStr] = Field(default=None, description="The namespace of the `eventTypeName` field for custom events and custom scheduled events.  ", alias="eventTypeNamespace")
    from_email_address: Optional[StrictStr] = Field(default=None, description="If formEmailType is SpecificEmail, this field is required.", alias="fromEmailAddress")
    from_email_type: Optional[StrictStr] = Field(default=None, alias="fromEmailType")
    from_name: Optional[Annotated[str, Field(strict=True, max_length=50)]] = Field(default=None, description="The name of email sender.", alias="fromName")
    id: Optional[StrictStr] = Field(default=None, description="The email template ID.")
    is_html: Optional[StrictBool] = Field(default=None, description="Indicates whether the style of email body is HTML.", alias="isHtml")
    name: Optional[Annotated[str, Field(strict=True, max_length=255)]] = Field(default=None, description="The name of the email template.")
    reply_to_email_address: Optional[StrictStr] = Field(default=None, description="If replyToEmailType is SpecificEmail, this field is required", alias="replyToEmailAddress")
    reply_to_email_type: Optional[StrictStr] = Field(default=None, alias="replyToEmailType")
    to_email_address: Optional[StrictStr] = Field(default=None, description="If `toEmailType` is `SpecificEmail`, this field is required.", alias="toEmailAddress")
    to_email_type: Optional[StrictStr] = Field(default=None, alias="toEmailType")
    updated_by: Optional[StrictStr] = Field(default=None, description="The ID of the user who updated the email template.", alias="updatedBy")
    updated_on: Optional[datetime] = Field(default=None, description="The time when the email template was updated. Specified in the UTC timezone in the ISO860 format (YYYY-MM-DDThh:mm:ss.sTZD). E.g. 1997-07-16T19:20:30.45+00:00", alias="updatedOn")
    additional_properties: Dict[str, Any] = {}
    __properties: ClassVar[List[str]] = ["active", "bccEmailAddress", "ccEmailAddress", "ccEmailType", "createdBy", "createdOn", "description", "emailBody", "emailSubject", "encodingType", "eventCategory", "eventTypeName", "eventTypeNamespace", "fromEmailAddress", "fromEmailType", "fromName", "id", "isHtml", "name", "replyToEmailAddress", "replyToEmailType", "toEmailAddress", "toEmailType", "updatedBy", "updatedOn"]

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
        """Create an instance of GetPublicEmailTemplateResponse from a JSON string"""
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
        """Create an instance of GetPublicEmailTemplateResponse from a dict"""
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
            "active": obj.get("active"),
            "bccEmailAddress": obj.get("bccEmailAddress"),
            "ccEmailAddress": obj.get("ccEmailAddress"),
            "ccEmailType": obj.get("ccEmailType") if obj.get("ccEmailType") is not None else GetPublicEmailTemplateResponseCcEmailType.SPECIFICEMAILS,
            "createdBy": obj.get("createdBy"),
            "createdOn": obj.get("createdOn"),
            "description": obj.get("description"),
            "emailBody": obj.get("emailBody"),
            "emailSubject": obj.get("emailSubject"),
            "encodingType": obj.get("encodingType"),
            "eventCategory": obj.get("eventCategory"),
            "eventTypeName": obj.get("eventTypeName"),
            "eventTypeNamespace": obj.get("eventTypeNamespace"),
            "fromEmailAddress": obj.get("fromEmailAddress"),
            "fromEmailType": obj.get("fromEmailType"),
            "fromName": obj.get("fromName"),
            "id": obj.get("id"),
            "isHtml": obj.get("isHtml"),
            "name": obj.get("name"),
            "replyToEmailAddress": obj.get("replyToEmailAddress"),
            "replyToEmailType": obj.get("replyToEmailType"),
            "toEmailAddress": obj.get("toEmailAddress"),
            "toEmailType": obj.get("toEmailType"),
            "updatedBy": obj.get("updatedBy"),
            "updatedOn": obj.get("updatedOn")
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
