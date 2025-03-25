# from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever 

from src.data_preparation.sourcing import Author
from src.retrieval.vector_store import get_base_retriever


class History:
    def __init__(self, author: Author, question: str, answer: str) -> None:
        self.answer: str = answer 
        self.author: Author = author 
        self.question: str = question
        self.contextualised_question: str = self.request_recontextualised_question()
        self.chat_history: list[BaseMessage] = self.make_chat_history()

    def make_chat_history(self) -> list[BaseMessage]:

        history: list[BaseMessage] = []
        history.extend(
            [
                HumanMessage(content=self.question),
                AIMessage(content=self.answer)
            ]
        )

        return history

    @staticmethod
    def request_recontextualised_question() -> str:

        return """
        Given the provided chat history and the most recent question from the user, which might reference context
        in the chat history, create a standalone question which can be understood without the chat history. Do not
        answer the question, just create it and return it.
        """

    def get_prompt_template(self) -> ChatPromptTemplate:

        return ChatPromptTemplate.from_messages(
            [
                ("system", self.contextualised_question),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )

    def get_history_aware_retriever(self, llm: BaseChatModel):
        
        base_retriever = get_base_retriever(author=self.author)
        prompt_template: ChatPromptTemplate = self.get_prompt_template()
        history_aware_retriever = create_history_aware_retriever(llm=llm, retriever=base_retriever, prompt=prompt_template)

        _ = history_aware_retriever.invoke(
            {
                "input": self.question, 
                "chat_history": self.chat_history
            }
        )


    # def make_chain(self, chat_history: list[BaseMessage], llm: BaseChatModel):
    #
    #     prompt_template: ChatPromptTemplate = self.get_prompt_template()
    #     chain = prompt_template | llm | StrOutputParser() 
    #
    #     _ = chain.invoke(
    #         {
    #             "input": self.question,
    #             "chat_history": chat_history
    #         }
    #     )
    #

