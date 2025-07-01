#!/usr/bin/python
# -*- coding: utf-8 -*-
from langgraph.graph import StateGraph, START, END
from common.ai_agent import retriever_node, http_node, AgentState, wait_user_input, filter_message_node, \
    router_after_retriever_node, router_after_wait_user_input
from langgraph.checkpoint.memory import MemorySaver
from pprint import pprint
from common.logger import logger
from langgraph.types import Command

workflow = StateGraph(AgentState)

workflow.add_node('retriever_node', retriever_node)
workflow.add_node('http_node', http_node)
workflow.add_node('filter_message_node', filter_message_node)
workflow.add_node('wait_user_input', wait_user_input)

workflow.add_edge(START, 'retriever_node')
workflow.add_conditional_edges('retriever_node', router_after_retriever_node,
                               {'wait_user_input': 'wait_user_input', '__end__': '__end__'})
workflow.add_conditional_edges('wait_user_input', router_after_wait_user_input,
                               {"http_node": "http_node", '__end__': '__end__'})
workflow.add_edge('http_node', 'filter_message_node')
workflow.add_edge('filter_message_node', END)
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

graph_png = app.get_graph().draw_mermaid_png()
with open('graph.png', 'wb') as f:
    f.write(graph_png)

messages = []
extract_api_info = ''
next_node = ''
config = {"configurable": {"thread_id": '1'}}
while True:
    user_input = input("请输入：")
    # events = app.stream(
    #     {'user_input': user_input, "messages": messages, "extract_api_info": extract_api_info, "next_node": next_node},
    #     config=config, stream_mode="values")
    # for event in events:
    #     pprint(event)
    #
    # user_data = input("请输入参数:")
    #
    # for event in app.stream(Command(resume=user_data),
    #                         config=config, stream_mode="values"):
    #     pprint(event)

    app.invoke(
        {'user_input': user_input, "messages": messages, "extract_api_info": extract_api_info, "next_node": next_node},
        config=config)
    user_data = input("请输入参数:")
    response = app.invoke(
        Command(resume=user_data),
        config=config
    )
    logger.info(f"结果：{response['messages'][-1].content}")
