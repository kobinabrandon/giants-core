from langgraph.prebuilt import tools_condition 
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import END, MessagesState, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from src.generation.appendix import get_context
from src.setup.config import State
from src.graph.nodes import tools, make_retrieval_node, make_generator_node, query_or_response_node


class Graph:
    def __init__(
            self, 
            with_memory: bool, 
            name_of_entry_point: str = "query_or_response_node", 
            name_of_tool_node: str = "tools", 
            name_of_generator_node: str = "make_generator_node"
    ) -> None:
    
        self.with_memory: bool = with_memory
        self.name_of_tool_node: str = name_of_tool_node
        self.name_of_entry_point: str = name_of_entry_point 
        self.name_of_generator_node: str = name_of_generator_node

        if not with_memory:
            self.builder: StateGraph = StateGraph(MessagesState) 
        else:
            self.builder: StateGraph = StateGraph(state_schema=State).add_sequence(
                nodes=[make_retrieval_node, make_generator_node]
            ) 
           
    def build(self) -> CompiledStateGraph:
        if not self.with_memory:
            _ = self.builder.add_edge(start_key=START, end_key="make_retrieval_node")
            graph = self.builder.compile()

            response = graph.invoke(
                input={"question": "Describe the events around the coup"}
            )
                
            return response["answer"]

        else:
            graph_builder = self.add_nodes_to_graph()
            graph_builder = self.set_entry_point()
            graph_builder = self.add_edges_to_graph()
            memory = MemorySaver()
            return self.builder.compile(checkpointer=memory)


    def add_nodes_to_graph(self) -> StateGraph:
        self.builder.add_node(query_or_response_node)
        self.builder.add_node(tools)
        return self.builder 


    def set_entry_point(self) -> StateGraph:
        _ = self.builder.set_entry_point(key=self.name_of_entry_point)
        return self.builder 

    def add_edges_to_graph(self):
        
        _ = self.builder.add_conditional_edges(
            self.name_of_entry_point,
            tools_condition,
            {END: END, "tools": self.name_of_tool_node}
        )
        
        _ = self.builder.add_edge(start_key=self.name_of_tool_node, end_key=self.name_of_generator_node)
        _ = self.builder.add_edge(start_key=self.name_of_generator_node, end_key=END)
        return self.builder


if __name__ == "__main__":
    config = {
        "configurable": {"thread_id": "abc123"}
    }

    graph_object = Graph(with_memory=True)
    compiled_graph = graph_object.build()

    for input in ["Hello", "Who were the coup plotters?", "What were their motivations?"]:
        for step in compiled_graph.stream(
            input= {
                "messages": [
                    {
                        "role": "user",
                        "question": input,
                        "context": get_context(question=input)
                    }                    
                ]
            },
            stream_mode="values",
            config=config
        ):

            step["messages"][-1].pretty_print()

    breakpoint()



