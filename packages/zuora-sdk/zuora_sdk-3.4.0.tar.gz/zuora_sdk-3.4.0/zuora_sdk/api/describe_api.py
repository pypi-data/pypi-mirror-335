# coding: utf-8

"""
    Zuora API Reference

    REST API reference for the Zuora Billing, Payments, and Central Platform! Check out the [REST API Overview](https://www.zuora.com/developer/api-references/api/overview/).

    The version of the OpenAPI document: 2024-05-20
    Contact: docs@zuora.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated

from zuora_sdk.api_client import ApiClient, RequestSerialized
from zuora_sdk.api_response import ApiResponse
from zuora_sdk.rest import RESTResponseType


class DescribeApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def get_describe(
        self,
        object: Annotated[StrictStr, Field(description="API name of an object in your Zuora tenant. For example, `InvoiceItem`. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects. ")],
        accept_encoding: Annotated[Optional[StrictStr], Field(description="Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it. ")] = None,
        content_encoding: Annotated[Optional[StrictStr], Field(description="Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload. ")] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken). ")] = None,
        zuora_track_id: Annotated[Optional[Annotated[str, Field(strict=True, max_length=64)]], Field(description="A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`). ")] = None,
        zuora_entity_ids: Annotated[Optional[StrictStr], Field(description="An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header. ")] = None,
        show_currency_conversion_information: Annotated[Optional[StrictStr], Field(description="Set the value to `yes` to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass `yes` to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text=Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. Set this parameter value to `no` to not include the additional currency conversion information in the result. ")] = None,
        zuora_version: Annotated[Optional[StrictStr], Field(description="The minor version of the Zuora REST API.  ")] = None,
        zuora_org_ids: Annotated[Optional[StrictStr], Field(description="Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs. ")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> str:
        """Describe an object

        Provides a reference listing of each object that is available in your Zuora tenant.  The information returned by this call is useful if you are using [CRUD: Create Export](https://www.zuora.com/developer/api-references/api/operation/Object_PostExport) or the [AQuA API](https://knowledgecenter.zuora.com/DC_Developers/T_Aggregate_Query_API) to create a data source export. See [Export ZOQL](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) for more information.  ### Response The response contains an XML document that lists the fields of the specified object. Each of the object's fields is represented by a `<field>` element in the XML document.      Each `<field>` element contains the following elements:  | Element      | Description                                                                                                                                                                                                                                                                                  | |--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | `<name>`     | API name of the field.                                                                                                                                                                                                                                                                       | | `<label>`    | Name of the field in the Zuora user interface.                                                                                                                                                                                                                                               | | `<type>`     | Data type of the field. The possible data types are: `boolean`, `date`, `datetime`, `decimal`, `integer`, `picklist`, `text`, `timestamp`, and `ZOQL`. If the data type is `picklist`, the `<field>` element contains an `<options>` element that lists the possible values of the field.    | | `<contexts>` | Specifies the availability of the field. If the `<contexts>` element lists the `export` context, the field is available for use in data source exports.                                                                                                                                                |  The `<field>` element contains other elements that provide legacy information about the field. This information is not directly related to the REST API.  Response sample: ```xml <?xml version=\"1.0\" encoding=\"UTF-8\"?> <object>   <name>ProductRatePlanCharge</name>   <label>Product Rate Plan Charge</label>   <fields>     ...     <field>       <name>TaxMode</name>       <label>Tax Mode</label>       <type>picklist</type>       <options>         <option>TaxExclusive</option>         <option>TaxInclusive</option>       </options>       <contexts>         <context>export</context>       </contexts>       ...     </field>     ...   </fields> </object> ```  It is strongly recommended that your integration checks `<contexts>` elements in the response. If your integration does not check `<contexts>` elements, your integration may process fields that are not available for use in data source exports. See [Changes to the Describe API](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL/Changes_to_the_Describe_API) for more information. 

        :param object: API name of an object in your Zuora tenant. For example, `InvoiceItem`. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects.  (required)
        :type object: str
        :param accept_encoding: Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it. 
        :type accept_encoding: str
        :param content_encoding: Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload. 
        :type content_encoding: str
        :param authorization: The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken). 
        :type authorization: str
        :param zuora_track_id: A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`). 
        :type zuora_track_id: str
        :param zuora_entity_ids: An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header. 
        :type zuora_entity_ids: str
        :param show_currency_conversion_information: Set the value to `yes` to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass `yes` to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text=Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. Set this parameter value to `no` to not include the additional currency conversion information in the result. 
        :type show_currency_conversion_information: str
        :param zuora_version: The minor version of the Zuora REST API.  
        :type zuora_version: str
        :param zuora_org_ids: Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs. 
        :type zuora_org_ids: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_describe_serialize(
            object=object,
            accept_encoding=accept_encoding,
            content_encoding=content_encoding,
            authorization=authorization,
            zuora_track_id=zuora_track_id,
            zuora_entity_ids=zuora_entity_ids,
            show_currency_conversion_information=show_currency_conversion_information,
            zuora_version=zuora_version,
            zuora_org_ids=zuora_org_ids,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "str",
            '400': "CommonResponse",
            '401': "ProxyUnauthorizedResponse",
            '403': "CommonErrorResponse",
            '404': "str",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def get_describe_with_http_info(
        self,
        object: Annotated[StrictStr, Field(description="API name of an object in your Zuora tenant. For example, `InvoiceItem`. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects. ")],
        accept_encoding: Annotated[Optional[StrictStr], Field(description="Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it. ")] = None,
        content_encoding: Annotated[Optional[StrictStr], Field(description="Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload. ")] = None,
        authorization: Annotated[Optional[StrictStr], Field(description="The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken). ")] = None,
        zuora_track_id: Annotated[Optional[Annotated[str, Field(strict=True, max_length=64)]], Field(description="A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`). ")] = None,
        zuora_entity_ids: Annotated[Optional[StrictStr], Field(description="An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header. ")] = None,
        show_currency_conversion_information: Annotated[Optional[StrictStr], Field(description="Set the value to `yes` to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass `yes` to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text=Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. Set this parameter value to `no` to not include the additional currency conversion information in the result. ")] = None,
        zuora_version: Annotated[Optional[StrictStr], Field(description="The minor version of the Zuora REST API.  ")] = None,
        zuora_org_ids: Annotated[Optional[StrictStr], Field(description="Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs. ")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[str]:
        """Describe an object

        Provides a reference listing of each object that is available in your Zuora tenant.  The information returned by this call is useful if you are using [CRUD: Create Export](https://www.zuora.com/developer/api-references/api/operation/Object_PostExport) or the [AQuA API](https://knowledgecenter.zuora.com/DC_Developers/T_Aggregate_Query_API) to create a data source export. See [Export ZOQL](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) for more information.  ### Response The response contains an XML document that lists the fields of the specified object. Each of the object's fields is represented by a `<field>` element in the XML document.      Each `<field>` element contains the following elements:  | Element      | Description                                                                                                                                                                                                                                                                                  | |--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | `<name>`     | API name of the field.                                                                                                                                                                                                                                                                       | | `<label>`    | Name of the field in the Zuora user interface.                                                                                                                                                                                                                                               | | `<type>`     | Data type of the field. The possible data types are: `boolean`, `date`, `datetime`, `decimal`, `integer`, `picklist`, `text`, `timestamp`, and `ZOQL`. If the data type is `picklist`, the `<field>` element contains an `<options>` element that lists the possible values of the field.    | | `<contexts>` | Specifies the availability of the field. If the `<contexts>` element lists the `export` context, the field is available for use in data source exports.                                                                                                                                                |  The `<field>` element contains other elements that provide legacy information about the field. This information is not directly related to the REST API.  Response sample: ```xml <?xml version=\"1.0\" encoding=\"UTF-8\"?> <object>   <name>ProductRatePlanCharge</name>   <label>Product Rate Plan Charge</label>   <fields>     ...     <field>       <name>TaxMode</name>       <label>Tax Mode</label>       <type>picklist</type>       <options>         <option>TaxExclusive</option>         <option>TaxInclusive</option>       </options>       <contexts>         <context>export</context>       </contexts>       ...     </field>     ...   </fields> </object> ```  It is strongly recommended that your integration checks `<contexts>` elements in the response. If your integration does not check `<contexts>` elements, your integration may process fields that are not available for use in data source exports. See [Changes to the Describe API](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL/Changes_to_the_Describe_API) for more information. 

        :param object: API name of an object in your Zuora tenant. For example, `InvoiceItem`. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects.  (required)
        :type object: str
        :param accept_encoding: Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it. 
        :type accept_encoding: str
        :param content_encoding: Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload. 
        :type content_encoding: str
        :param authorization: The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken). 
        :type authorization: str
        :param zuora_track_id: A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`). 
        :type zuora_track_id: str
        :param zuora_entity_ids: An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header. 
        :type zuora_entity_ids: str
        :param show_currency_conversion_information: Set the value to `yes` to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass `yes` to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text=Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. Set this parameter value to `no` to not include the additional currency conversion information in the result. 
        :type show_currency_conversion_information: str
        :param zuora_version: The minor version of the Zuora REST API.  
        :type zuora_version: str
        :param zuora_org_ids: Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs. 
        :type zuora_org_ids: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._get_describe_serialize(
            object=object,
            accept_encoding=accept_encoding,
            content_encoding=content_encoding,
            authorization=authorization,
            zuora_track_id=zuora_track_id,
            zuora_entity_ids=zuora_entity_ids,
            show_currency_conversion_information=show_currency_conversion_information,
            zuora_version=zuora_version,
            zuora_org_ids=zuora_org_ids,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "str",
            '400': "CommonResponse",
            '401': "ProxyUnauthorizedResponse",
            '403': "CommonErrorResponse",
            '404': "str",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )

    def _get_describe_serialize(
        self,
        object,
        accept_encoding,
        content_encoding,
        authorization,
        zuora_track_id,
        zuora_entity_ids,
        show_currency_conversion_information,
        zuora_version,
        zuora_org_ids,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if object is not None:
            _path_params['object'] = object
        # process the query parameters
        if show_currency_conversion_information is not None:
            
            _query_params.append(('showCurrencyConversionInformation', show_currency_conversion_information))
            
        # process the header parameters
        if accept_encoding is not None:
            _header_params['Accept-Encoding'] = accept_encoding
        if content_encoding is not None:
            _header_params['Content-Encoding'] = content_encoding
        if authorization is not None:
            _header_params['Authorization'] = authorization
        if zuora_track_id is not None:
            _header_params['Zuora-Track-Id'] = zuora_track_id
        if zuora_entity_ids is not None:
            _header_params['Zuora-Entity-Ids'] = zuora_entity_ids
        if zuora_version is not None:
            _header_params['Zuora-Version'] = zuora_version
        if zuora_org_ids is not None:
            _header_params['Zuora-Org-Ids'] = zuora_org_ids
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'text/xml; charset=utf-8', 
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'bearerAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/v1/describe/{object}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


