import os
import json
from pathlib import Path
from loguru import logger

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

from src.history import History
from src.setup.config import groq_config
from src.data_preparation.sourcing import Author
from src.data_preparation.utils import get_author
from src.retrieval.utils import make_base_prompt 
from src.retrieval.vector_store import get_context


class Generator:
    def __init__(
            self, 
            nickname: str, 
            question: str, 
            top_p: float | None = None,
            temperature: float | None = None,
            model_name: str = groq_config.preferred_model
    ) -> None:
        self.nickname: str = nickname
        self.question: str = question
        self.top_p: float | None = top_p 
        self.model_name: str = model_name 
        self.temperature: float | None = temperature 

    def answer(self, save: bool = True) -> None: 

        llm = self.__get_llm__() 
        assert llm != None

        author: Author|None = get_author(nickname=self.nickname)
        assert author != None
        
        context: str = get_context(author=author, question=self.question) 
        prompt: str = make_base_prompt(author=author, context=context, question=self.question)

        final_answer = ""
        for chat in llm.stream(input=prompt):
            print(chat.content, end="", flush=True)
            final_answer += chat.content

        if save:
            self.__record_answer__(author=author, context=context, response=final_answer)
        
    def __get_llm__(self, temperature: int = 0) -> BaseChatModel | None:
        if self.model_name == groq_config.preferred_model:
            return ChatGroq(temperature=temperature, model=self.model_name)
        else:
            raise NotImplementedError(f"{self.model_name} has not currently been implemented")

    def __record_answer__(self, author: Author, context: str, response: str, history: str | None = None) -> None:
        """
        Create directories where the responses for and associated data will be kept, and then store that information 
        for later review. 

        Args:
            response: the response complete response from the LLM 
        """
        RESPONSES_DIR = author.path_to_data.joinpath("reponses")
        MODEL_DIR = RESPONSES_DIR.joinpath(self.model_name) 

        for path in [RESPONSES_DIR, MODEL_DIR]:
            if not Path(path).exists():
                os.mkdir(path)

        data_to_save: list[dict[str, str | int | float | None]]  = [
            {
                "top_p": self.top_p,
                "temperature": self.temperature,
                "question": self.question, 
                "context": context,
                "response": response,
                "history": history
            }
        ]   

        attempt = 0 
        truncated_question: str = self.__shorten_question__()
        name_of_file_to_save: str = f"{truncated_question}.json" 
        file_path: Path = MODEL_DIR.joinpath(name_of_file_to_save)

        # Save the information associated with this query because it's the first of its kind 
        if not file_path.exists(): 
            data_to_save[0]["attempt"] = attempt
            with open(file_path, mode="w") as file:
                json.dump(data_to_save, file, indent=4)

        else: 
            # Retrieve the data associated with a similar question that was previously asked 
            with open(file_path, mode="rb") as file:
                saved_data: list[dict[str, str | int | float |None]]  = json.load(file)

            # Delete the old file
            os.remove(file_path)

            # Mark the current query as a new attempt to answer a similar question
            data_to_save[0]["attempt"]: int = saved_data[-1]["attempt"] + 1
            saved_data.extend(data_to_save)

            with open(file_path, mode="w") as file:
                json.dump(saved_data, file, indent=4)

        logger.success("Response logged") 

    def __shorten_question__(self) -> str:
        """
        Return the index of the first question mark or full stop that occurs in the question

        Returns:
            str: the truncated question    
        """
        question_mark_index: int = self.question.find("?")
        full_stop_index: int = self.question.find(".")

        match ("?" not in self.question), ("." not in self.question):
            case (False, False):
                return self.question
            case (False, True):
                return self.question[: full_stop_index + 1] 
            case (True, False) | (True, True):
                return self.question[: question_mark_index + 1] 


if __name__ == "__main__":
    generator = Generator(nickname="fidel", question="How did Castro get the Cuban peasants on his side?")
    generator.answer()

