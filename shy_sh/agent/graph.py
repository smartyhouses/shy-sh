from langgraph.graph import StateGraph, START
from shy_sh.agent.nodes.chatbot import chatbot
from shy_sh.agent.nodes.tools_handler import tools_handler
from shy_sh.agent.edges.final_response import final_response_edge
from shy_sh.agent.edges.tool_calls import tool_calls_edge
from shy_sh.models import State

graph_builder = StateGraph(State)


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tools_handler)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tool_calls_edge)
graph_builder.add_conditional_edges("tools", final_response_edge)

graph = graph_builder.compile()
