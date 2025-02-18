from langgraph.prebuilt import tools_condition 
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.checkpoint.memory import MemorySaver


from src.generation.appendix import record_responses 
from src.graph.nodes import tools, generate, query_or_response_node


def build_graph(name_of_retrieval_node: str = "make_retrieval_node", name_of_entry_point: str = "query_or_response_node") -> CompiledStateGraph: 

    builder: StateGraph = StateGraph(MessagesState)
    builder.set_entry_point(key=name_of_entry_point)

    for node in [query_or_response_node, tools, generate]:
        builder = builder.add_node(node)

    builder = add_edges(builder=builder)

    memory = MemorySaver()
    compiled_graph = builder.compile(checkpointer=memory)
    return compiled_graph 


def add_edges(builder: StateGraph, name_of_tool_node: str = "tools", name_of_generator_node: str = "generate", name_of_entry_point: str = "query_or_response_node") -> StateGraph:


    builder = builder.add_edge(start_key=START, end_key=name_of_entry_point)

    builder = builder.add_conditional_edges(
        name_of_entry_point, 
        tools_condition,
        {END: END, "tools": name_of_tool_node}
    )
                    
    builder = builder.add_edge(start_key=name_of_tool_node, end_key=name_of_generator_node)
    builder = builder.add_edge(start_key=name_of_generator_node, end_key=END)
    return builder


def stream(input: str, compiled_graph: CompiledStateGraph, config: dict[str, str]):

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
        # if msg.type != "tool":
        msg.pretty_print()


if __name__ == "__main__":
    compiled_graph = build_graph()

    config = {
        "configurable": {"thread_id": "abc123"}
    }

    for input in ["Hello", "Who were the coup plotters against Nkrumah?", "What were their motivations?"]:
        stream(input=input, compiled_graph=compiled_graph, config=config)

