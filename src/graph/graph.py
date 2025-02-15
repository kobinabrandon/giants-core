from argparse import ArgumentParser
from langgraph.prebuilt import tools_condition 
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver


from src.retrieval import get_context
from src.graph.state import ChatState
from src.setup.config import groq_config
from src.generation.appendix import record_responses 
from src.graph.nodes import tools, make_retrieval_node, generate, make_generator_node


class Graph:
    def __init__(
        self, 
        question: str,
        with_memory: bool, 
        name_of_tool_node: str = "tools",
        name_of_entry_point: str = "make_retrieval_node"
    ) -> None:

        self.question: str = question
        self.context: str = get_context(question=question)

        self.with_memory: bool = with_memory
        self.name_of_tool_node: str = name_of_tool_node
        self.name_of_entry_point: str = name_of_entry_point 
        self.name_of_retrieval_node: str = "make_retrieval_node"
        self.name_of_generator_node: str = "make_generator_node" if not self.with_memory else "generate"

        self.nodes: list[object] = [make_retrieval_node, make_generator_node] if not with_memory else [make_retrieval_node, generate] 
        self.builder: StateGraph = StateGraph(state_schema=ChatState).add_sequence(nodes=self.nodes) 
       
    def build(self) -> str: 

        if not self.with_memory:
            self.builder = self.builder.add_edge(start_key=START, end_key=self.name_of_retrieval_node)
            compiled_graph = self.builder.compile()

            response = compiled_graph.invoke(
                input={"question": self.question}
            )

        else:
            initial_state: ChatState = {
                "question": self.question,
                "context": self.context,
                "answer": "",
                "messages": [""] 
            } 
            
            memory = MemorySaver()

            config = {
                "configurable": {"thread_id": "abc123"}
            }

            self.builder = self.add_nodes_to_graph()
            self.builder = self.set_entry_point()
            self.builder = self.add_edges_to_graph()

            compiled_graph = self.builder.compile(checkpointer=memory)
            response = compiled_graph.invoke(input=initial_state, config=config)

        answer: str = response["answer"]

        record_responses(
            model_name=groq_config.preferred_model,
            question=self.question,
            context=self.context,
            response=answer
        )
            
        return answer 

    def add_nodes_to_graph(self) -> StateGraph:
        self.builder = self.builder.add_node(tools)
        return self.builder 


    def set_entry_point(self) -> StateGraph:
        self.builder = self.builder.set_entry_point(key=self.name_of_entry_point)
        return self.builder 

    def add_edges_to_graph(self):
        
        self.builder = self.builder.add_conditional_edges(
            self.name_of_entry_point,
            tools_condition,
            {"tools": self.name_of_tool_node, END: END}
        )
        
        self.builder = self.builder.add_edge(start_key=self.name_of_tool_node, end_key=self.name_of_generator_node)
        self.builder = self.builder.add_edge(start_key=self.name_of_generator_node, end_key=END)
        return self.builder


if __name__ == "__main__":
    parser = ArgumentParser()
    _ = parser.add_argument("--memory", action="store_true")
    args = parser.parse_args()
    question="What reasons could the West have had for wanting Nkrumah out of the way?"

    if not args.memory: 

        graph_object = Graph(with_memory=False, question=question) 
        answer = graph_object.build()
        print(answer)
       
    else:
        graph_object = Graph(with_memory=True, question=question)
        compiled_graph = graph_object.build()

        breakpoint()
        for input in ["Hello", "Who were the coup plotters?", "What were their motivations?"]:
            state.question = input
            for step in compiled_graph.stream(
                input= {
                    "messages": [
                        {
                            "role": "user",
                            "question": input,
                            "context": graph_object.context 
                        }                    
                    ]
                },
                stream_mode="values",
                config=config
            ):

                step["messages"][-1].pretty_print()

        breakpoint()



