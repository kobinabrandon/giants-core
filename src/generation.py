import os
import json
from pathlib import Path
from loguru import logger
from openai import OpenAI
from langchain_core.documents import Document

from src.config import config 
from src.paths import set_paths
from src.retrieval import query_chroma


class PrimaryGenerator:
    def __init__(
            self, 
            question: str, 
            top_p: float | None = 0, 
            temperature: int | None = 0, 
            max_tokens: int = 2000,
            save_data: bool = True,
            model_name: str = "wayfarer-12b-gguf-hva"
    ) -> None:
        """

        Args:
            question: the question being asked of the LLM
            max_tokens: the maximum number of tokens in the generated answer 
            temperature: the level of randomness in the choice of the next letter 
            top_p: a floating point number that controls the variety of words to be considered during generation 
            save_data: whether the question and the resulting answer will be logged. 
            model_name: the name of the model being accessed via the endpoint URL 
        """
        self.question: str = question
        self.top_p: float | None = top_p
        self.max_tokens: int = max_tokens
        self.save_data: bool = save_data
        self.model_name: str = model_name
        self.context: str = self.get_context()
        self.temperature: int | None = temperature
        self.truncated_question: str = self.shorten_question()
            
    def query_llm(self) -> None:
        """Gets the context, and uses it (as well as the question) to construct a prompt."""
        
        assert self.model_name in config.endpoints_under_consideration.keys()

        logger.info(f"Question: {self.question}")
        logger.info("Creating prompt..")
        prompt: str = self.construct_prompt()
        
        endpoint_url: str = config.endpoints_under_consideration[self.model_name] 
        client = OpenAI(base_url=endpoint_url, api_key=config.hugging_face_token)

        logger.info("Prompting model...")
        chat_completion = client.chat.completions.create(
            model="tgi",
            top_p=self.top_p,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": prompt 
                }
            ]
        )
        
        logger.success("Answering query. Stand by:")

        response_characters: list[str] = [""]
        for message in chat_completion:
            letters_in_the_response: str | None = message.choices[0].delta.content
            print(letters_in_the_response, end="")

            if isinstance(letters_in_the_response, str) :
                response_characters.append(letters_in_the_response)
               
        if self.save_data:
            full_response = "" 
            for i in response_characters:
                full_response += i

            self.record_responses(response=full_response) 

    def get_context(self) -> str:
        """
        Query the VectorDB(Chroma for now) to perform a similarity search,  

        Args:
            question: the question being asked of the model. 

        Returns:
           str: the text retrieved from the vector database based on a certain similarity metric 
        """
        logger.info("Getting context:")
        query_results: list[tuple[Document, float]] = query_chroma(question=self.question)
        retrieved_results = [result[0].page_content for result in query_results]

        return "".join(
            [doc for doc in retrieved_results]
        )

    def construct_prompt(self) -> str:

        return f""" 
                You are a helpful chatbot whose job is to answer questions based on the context given to you. 
                Using the information contained in the context, give a comprehensive answer to the question, without mentioning the context with wording like "Based on the context...".
                Respond only to the question asked, but try to make the response as detailed as you can, while staying within the bounds of the context provided. 
                If the answer cannot be deduced from the context, say that you do not know. Where you make reference to specific statements from the context, quote those statements first. 
                Try to avoid repetition.
                    
                Context: 
                {self.context}

                Now here is the question you need to answer: 
                {self.question}
                """  

    def record_responses(self, response: str) -> None:
        """
        Create directories where the responses for and associated data will be kept, and then store that information 
        for later review. 

        Args:
            response: the response complete response from the LLM 
        """
        DATA_DIR = set_paths()["data"]

        RESPONSES_DIR = DATA_DIR / "responses" 
        MODEL_DIR = RESPONSES_DIR / self.model_name
        
        for path in [RESPONSES_DIR, MODEL_DIR]:
            if not Path(path).exists():
                os.mkdir(path)

        data_to_save: list[dict[str, str | int | float |None]]  = [
            {
                "top_p": self.top_p,
                "temperature": self.temperature,
                "question": self.question, 
                "context": self.context,
                "response": response
            }
        ]   

        attempt = 0 
        name_of_file_to_save: str = f"{self.truncated_question}.json" 
        file_path: Path = MODEL_DIR / name_of_file_to_save
        
        # Save the information associated with this query because it's the first of its kind 
        if not Path(file_path).exists(): 
            data_to_save[0]["attempt"] = attempt
            with open(file_path, mode="w") as file:
                json.dump(data_to_save, file, indent=4)

        else: 
            with open(file_path, mode="rb") as file:
                # Retrieve the data associated with a similar question that was previously asked 
                saved_data: list[dict[str, str | int | float |None]]  = json.load(file)
            
            # Delete the old file
            os.remove(file_path)

            # Mark the current query as a new attempt to answer a similar question
            data_to_save[0]["attempt"]: int = saved_data[-1]["attempt"] + 1
            saved_data.extend(data_to_save)

            with open(file_path, mode="w") as file:
                json.dump(saved_data, file, indent=4)


    def shorten_question(self) -> str:
        """
        Return the index of the first question mark or full stop that occurs in the question

        Returns:
            str: the truncated question    
        """
        index: list[str] = []
        for character in self.question:
            if character in ["?", "."]:
                truncated_question = self.question[: self.question.index(character) + 1] 
                index.append(truncated_question)
                break
        
        return index[0] 


if __name__ == "__main__":
    generator = PrimaryGenerator(
        question="Why was Nkrumah so insistent that Africa must unite? Provide me with quotes to support your case"
    )

    generator.query_llm()

