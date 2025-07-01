#!/usr/bin/python
# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Any


class ApiItem(BaseModel):
    tags: List = Field(..., description="API名称", default_factory=[])
    description: str = Field(..., description="API描述")
    summary: str = Field(..., description="API摘要")
    url: str = Field(..., description="API URL")
    method: str = Field(..., description="API请求方法")
    params: Any = Field(..., description="API请求参数")
    content_type: str = Field(..., description="API请求头")
    request_body: Any = Field(..., description="API请求体")


class ApiProject(BaseModel):
    project_name: str = Field(..., description="项目名称")
    base_url: str = Field(..., description="项目基础URL")
    apis: List[ApiItem] = Field(..., description="API列表")


class APIInfo(BaseModel):
    api_name: str = Field(..., description="接口名称")
    api_url: str = Field(..., description="API URL")
    api_method: str = Field(..., description="API请求方法")
    api_params: Any = Field(..., description="GET请求参数")
    api_content_type: str = Field(..., description="API请求头")
    api_request_body: Any = Field(..., description="POST方法请求体")
    api_description: str = Field(..., description="API描述")
