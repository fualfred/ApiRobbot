#!/usr/bin/python
# -*- coding: utf-8 -*-
from langgraph.graph import StateGraph, START, END
from common.ai_agent import retriever_node, http_node, AgentState, wait_user_input, filter_message_node, \
    router_after_retriever_node, router_after_wait_user_input
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from fastapi import FastAPI, HTTPException
from fastapi_offline import FastAPIOffline
from pydantic import BaseModel
import uvicorn
from common.logger import logger
from langserve import add_routes
from langchain_core.runnables import RunnableLambda

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
agent = workflow.compile(checkpointer=checkpointer)

# config = {"configurable": {"thread_id": '1'}}

# app = FastAPI()

app = FastAPIOffline()
add_routes(
    app,
    agent,
    path="/api"
)


class InterruptRequest(BaseModel):
    thread_id: str
    user_input: str


class ResumeRequest(BaseModel):
    thread_id: str
    input_str: str


@app.post("/start")
async def start_workflow(request: InterruptRequest):
    messages = []
    extract_api_info = ''
    next_node = ''
    result = await agent.ainvoke(
        {'user_input': request.user_input, "messages": messages, "extract_api_info": extract_api_info,
         "next_node": next_node}, config={"configurable": {"thread_id": request.thread_id}})
    if "__interrupt__" in result:
        logger.info(f"interrupted by user: {request.user_input}")
        return result['messages'][-1]
    else:
        return result['messages'][-1]


@app.post("/resume")
async def resume_workflow(request: ResumeRequest):
    result = await agent.ainvoke(Command(resume=request.input_str),
                                 config={"configurable": {"thread_id": request.thread_id}})
    return result['messages'][-1]
