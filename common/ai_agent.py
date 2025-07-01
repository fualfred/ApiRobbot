#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import TypedDict, Annotated, List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from common.get_llms import LLM
from common.models import APIInfo
from common.chroma_utils import ChromaUtils
from common.logger import logger
from common.utils import is_json_with_single_quotes, request_api
import json
from langgraph.types import interrupt

parser = PydanticOutputParser(pydantic_object=APIInfo)

chroma_util = ChromaUtils()


class AgentState(TypedDict):
    user_input: Annotated[str, "用户输入的消息"]
    messages: Annotated[List, "对话历史消息"]
    extract_api_info: Annotated[str, "从文档提取的api信息，需要呈现给用户"]
    next_node: Annotated[str, "下一个节点"]
    extract_user_input: Annotated[str, "从用户输入中提取的json信息"]


def wait_user_input(state: AgentState) -> AgentState:
    logger.info("==========interrupt============")
    user_data = interrupt("请输入参数")
    logger.info(f'用户输入 {user_data}')
    is_json = is_json_with_single_quotes(user_data)
    state['messages'].append(HumanMessage(content=user_data))
    if not is_json:
        logger.info(f"下一个节点是:__end__")
        state['messages'].append(AIMessage(content="请重新输入查找接口"))
        state['next_node'] = '__end__'
    else:
        state['user_input'] = user_data
        state['extract_user_input'] = user_data
        logger.info(f"下一个节点是:http_node")
        state['next_node'] = 'http_node'

    return state


def router_after_wait_user_input(state: AgentState) -> str:
    if state['next_node'] == '__end__':
        logger.info(f"下一个节点是:end")
        return '__end__'
    else:
        state['next_node'] = 'http_node'
        return 'http_node'


def retriever_node(state: AgentState) -> AgentState:
    _prompt = """
        您是世界级API文档解析专家，根据用户输入，从各种格式的API文档中提取结构化信息
        请根据以下API文档
        {context}
        
        用户输入
        {user_input}
        
        如果到提取API接口结构化信息，并按照以下格式返回
        {format_instructions}
        
        ###示例####
        {{
            "api_name": "api-queryService",  
            "api_url": "http://localhost:8080//api/queryService/"
            "api_description": "查询周边服务
            :param request:
            :param user_data: 必填
            :return:",
            "api_method":"POST"
            "api_params":"",
            "api_content_type":"application/json",
            "request_body":{{
                            "types": "",
                             "location": "",
                            "pagesize": 20,
                            "pagenum": 0
                          }}
        }}
        找不到相关的接口，则返回{{"message":"未找到相关的接口"}}
    """
    prompt = PromptTemplate(input_variables=["context", "user_input"], template=_prompt,
                            partial_variables={"format_instructions": parser.get_format_instructions()})
    llm = LLM().get_llm()
    state['messages'].append(HumanMessage(content=state["user_input"]))
    response = {"message": "未找到相关的接口"}
    try:
        # print(state['messages'])

        chain = {"context": chroma_util.retriever(),
                 "user_input": RunnablePassthrough()} | prompt | llm | parser
        response = chain.invoke(state["user_input"])
        state["extract_api_info"] = response
        state['messages'].append(AIMessage(content=APIInfo.model_dump_json(response)))
        logger.info(f"提取API接口结构化信息: {state['extract_api_info']}")
        state['next_node'] = 'wait_user_input'
    except Exception as e:
        logger.error(f"提取找不到相关的接口:{response} 异常是{str(e)}")
        state['messages'].append(AIMessage(content=json.dumps(response, ensure_ascii=False)))
        state['next_node'] = '__end__'
    # print(response)
    return state


def router_after_retriever_node(state: AgentState) -> str:
    if state['next_node'] == '__end__':
        logger.info("下一个节点是:__end__")
        return '__end__'
    else:
        logger.info("下一个节点是:wait_user_input")
        return 'wait_user_input'


def http_node(state: AgentState) -> AgentState:
    api_info = state["extract_api_info"]
    user_input = state["extract_user_input"]
    response = request_api(url=api_info.api_url, method=api_info.api_method, request_body=user_input)
    logger.info(f'http_node: {response}')
    state['messages'].append(AIMessage(content=f"API请求结果: {response}"))
    return state


def filter_message_node(state: AgentState) -> AgentState:
    messages = state['messages']
    if len(messages) > 10:
        logger.info(f"过滤掉最早的消息:只取最近10条消息")
        state['messages'] = messages[-10:]
    return state


if __name__ == '__main__':
    pass
    # _state = AgentState(user_input='查询周边', extract_api_info="", messages=[])
    # message = retriever_node(_state)
    # logger.info(_state)
