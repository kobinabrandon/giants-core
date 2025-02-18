from argparse import ArgumentParser
from os import walk
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage
from langgraph import graph
from langgraph.graph.message import Messages
from langgraph.prebuilt import tools_condition 
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.tool_node import asyncio


from src.retrieval import get_context
from src.graph.state import ChatState
from src.setup.config import groq_config
from src.generation.appendix import record_responses 
from src.graph.nodes import tools, make_retrieval_node, generate, make_generator_node, query_or_response_node


class Graph:
    def __init__(
        self, 
        question: str,
        name_of_tool_node: str = "tools",
        name_of_entry_point: str = "query_or_response_node"
    ) -> None:

        self.question: str = question
        self.context: str = get_context(question=question, raw=False)
        self.name_of_tool_node: str = name_of_tool_node
        self.name_of_entry_point: str = name_of_entry_point 

        self.name_of_retrieval_node: str = "make_retrieval_node" 
        self.name_of_generator_node: str = "generate"

        self.builder: StateGraph = StateGraph(MessagesState)
      
    def build(self) -> CompiledStateGraph: 

        self.builder.set_entry_point(key=self.name_of_entry_point)
        self.builder = self.add_nodes()
        self.builder = self.add_edges()

        memory = MemorySaver()
        compiled_graph = self.builder.compile(checkpointer=memory)
        return compiled_graph 
        
    def add_nodes(self) -> StateGraph:
        self.builder = self.builder.add_node(query_or_response_node)
        self.builder = self.builder.add_node(tools)
        self.builder = self.builder.add_node(generate)
        return self.builder

    def add_edges(self)-> StateGraph:

        self.builder = self.builder.add_conditional_edges(
            "query_or_response_node", 
            tools_condition,
            {"tools": self.name_of_tool_node, END: END}
        )
                        
        self.builder = self.builder.add_edge(start_key=self.name_of_tool_node, end_key=self.name_of_generator_node)
        self.builder = self.builder.add_edge(start_key=self.name_of_generator_node, end_key=END)
        return self.builder


def final(input: str, config: dict[str, str]):

    for step in compiled_graph.stream(
        input= {
            "messages": [
                {
                    "role": "user",
                    "content": input,
                }                    
            ]
        },
        stream_mode="values",
        config=config
    ):
        msg = step["messages"][-1]
        msg.pretty_print()


if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--memory", action="store_true")
    args = parser.parse_args()
    question="What reasons could the West have had for wanting Nkrumah out of the way?"

    if args.memory: 
        graph_object = Graph(question=question)
        compiled_graph = graph_object.build()

        config = {
            "configurable": {"thread_id": "abc123"}
        }

        for input in ["Hello", "Who were the coup plotters?", "What were their motivations?"]:
            final(config=config, input=input)
