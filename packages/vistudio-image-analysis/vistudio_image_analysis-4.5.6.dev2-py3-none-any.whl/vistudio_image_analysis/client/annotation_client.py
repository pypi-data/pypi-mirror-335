# !/user/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2023/11/25 13:41
# @Author : yangtingyu01
# @Email: yangtingyu01@baidu.com
# @File : annotation_client.py
# @Software: PyCharm
"""
from typing import Optional
from multidict import MultiDict
from baidubce.http import http_methods
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.bce_client_configuration import BceClientConfiguration
from bceinternalsdk.client.bce_internal_client import BceInternalClient
from bceinternalsdk.client.paging import PagingRequest
from baidubce.http import http_content_types
import json


class AnnotationClient(BceInternalClient):
    """
    A client class for interacting with the Annotation service. Initializes with default configuration.

    This client provides an interface to send requests to the BceService.

    Args:
            config (Optional[BceClientConfiguration]): The client configuration to use.
            ak (Optional[str]): Access key for authentication.
            sk (Optional[str]): Secret key for authentication.
            endpoint (Optional[str]): The service endpoint URL.
            context (Optional[dict]): Additional context information to be passed to the client.
    Example:
        client = AnnotationClient(
            endpoint="https://annotation-service.example.com",
            context={"OrgID": "org_id", "UserID": "user_id"}
            config=BceClientConfiguration(),
            ak="your-access-key",
            sk="your-secret-key")
    """

    def list_annotation_set(self, workspace_id: str, project_name: str,
                            categories: Optional[str] = "",
                            filters: Optional[str] = "",
                            page_request: Optional[PagingRequest] = PagingRequest()):
        """
                List annotation set based on specified criteria.

                Args:
                    workspace_id (str): 工作区id
                    project_name (str): project localName
                    categories (str): 按分类筛选  example: categories=Image/OCR&categories=Image/AnomalyDetection
                    filters (str):Filter the search keyword, search by localName, displayName and
                    description is supported.
                    page_request (PagingRequest): Object containing paging request details.

                Returns:
                    dict: The response from the server.
                """
        object_name = MultiDict()
        object_name.add("pageNo", str(page_request.get_page_no()))
        object_name.add("pageSize", str(page_request.get_page_size()))
        object_name.add("order", page_request.order)
        object_name.add("orderBy", page_request.orderby)
        object_name.add("filter", filters)
        if categories:
            for i in categories:
                object_name.add("category", i)

        return self._send_request(http_method=http_methods.GET,
                                  path=bytes("/v1/workspaces/" + workspace_id +
                                             "/projects/" + project_name + "/annotationsets",
                                             encoding="utf-8"),
                                  params=object_name)

    def get_annotation_set(self, workspace_id: str, project_name: str, local_name: str):
        """
        get the specific annotation_set by local name

        Args:
            workspace_id(str): 工作区id
            project_name(str): project local name
            local_name(str): annotation_set名称
        Returns:
            dict: The response from the server
        """
        return self._send_request(http_method=http_methods.GET,
                                  path=bytes("/v1/workspaces/" + workspace_id + "/projects/"
                                             + project_name + "/annotationsets/" + local_name, encoding="utf-8"))

    def create_annotation_label(self,
                                workspace_id: str,
                                project_name: str,
                                annotation_set_name: str,
                                local_name: str,
                                display_name: str,
                                color: str = "",
                                parent_id: str = None):
        """
        create annotation label
        :param workspace_id:  工作区id
        :param project_name: project local name
        :param annotation_set_name: annotation_set_name
        :param parent_id: parent_id
        :param local_name: local_name
        :param display_name: display_name
        :param color: color
        :return:
        """

        body = {
            "workspaceID": workspace_id,
            "projectName": project_name,
            "localName": local_name,
            "displayName": display_name,
            "annotationSetName": annotation_set_name,
            "parentID": parent_id,
            "color": color
        }
        return self._send_request(
            http_method=http_methods.POST,
            path=bytes(
                "/v1/workspaces/"
                + workspace_id
                + "/projects/"
                + project_name
                + "/annotationsets/"
                + annotation_set_name
                + "/annotationlabels",
                encoding="utf-8",
            ),
            headers={b"Content-Type": http_content_types.JSON},
            body=json.dumps(body))

    def delete_annotation_label(self,
                                workspace_id: str,
                                project_name: str,
                                annotation_set_name: str,
                                local_name: str,
                                parent_id: str = None):
        """
        delete_annotation_label
        :param workspace_id:  工作区id
        :param project_name: project local name
        :param annotation_set_name: annotation_set_name
        :param local_name: local_name
        :param parent_id: parent_id
        :return:
        """
        params = {"parentID": parent_id}
        return self._send_request(
            http_method=http_methods.DELETE,
            path=bytes(
                "/v1/workspaces/"
                + workspace_id
                + "/projects/"
                + project_name
                + "/annotationsets/"
                + annotation_set_name
                + "/annotationlabels/"
                + local_name,
                encoding="utf-8",
            ),
            params=params
        )

    def get_prompt_template(
            self, workspace_id: str,
            project_name: str,
            annotation_set_name: str,
            local_name: str
    ):
        """
        get prompt template

        Args:
            workspace_id(str): 工作区id
            project_name(str): project local name
            annotation_set_name(str): 标注集名称
            local_name(str): 提示词模板的local name
        Returns:
            dict: The response from the server
        """
        return self._send_request(http_method=http_methods.GET,
                                  path=bytes("/v1/workspaces/" + workspace_id +
                                             "/projects/" + project_name +
                                             "/annotationsets/" + annotation_set_name +
                                             "/prompttemplates/" + local_name, encoding="utf-8"))

    def list_prompt_template(
            self, workspace_id: str,
            project_name: str,
            annotation_set_name: str,
            filters: Optional[str] = "",
            paging_request: Optional[PagingRequest] = PagingRequest()):
        """
        list prompt templates

        Args:
            workspace_id(str): 工作区id
            project_name(str): project local name
            annotation_set_name(str): 标注集名称
            filters(str): 过滤条件
            paging_request(PagingRequest): 分页请求
        Returns:
            dict: The response from the server
        """
        object_name = MultiDict()
        object_name.add("pageNo", str(paging_request.get_page_no()))
        object_name.add("pageSize", str(paging_request.get_page_size()))
        object_name.add("order", paging_request.order)
        object_name.add("orderBy", paging_request.orderby)
        object_name.add("filter", filters)

        return self._send_request(http_method=http_methods.GET,
                                  path=bytes("/v1/workspaces/" + workspace_id +
                                             "/projects/" + project_name +
                                             "/annotationsets/" + annotation_set_name +
                                             "/prompttemplates", encoding="utf-8"),
                                  params=object_name)

