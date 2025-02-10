import os
import json
from pathlib import Path
from loguru import logger
from openai import OpenAI
from collections.abc import Generator

from src.setup.paths import set_paths
from src.setup.config import env_config, llm_config  
from src.generation.appendix import get_prompt, get_context 


class PrimaryGenerator:
    def __init__(
            self, 
            question: str, 
            top_p: float | None = 0, 
            temperature: int | None = 0, 
            max_tokens: int = 2000,
            save_data: bool = True,
            model_name: str = llm_config.preferred_model
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
        self.context: str = get_context(question=self.question)

        self.top_p: float | None = top_p
        self.max_tokens: int = max_tokens
        self.save_data: bool = save_data
        self.model_name: str = model_name
        self.temperature: int | None = temperature
        self.truncated_question: str = self.shorten_question()
            
    def query_llm(self, to_frontend: bool) -> Generator[str|None] | None:
        """Gets the context, and uses it (as well as the question) to construct a prompt."""
        
        assert self.model_name in llm_config.endpoints_under_consideration.keys()

        logger.info(f"Question: {self.question}")
        logger.info("Creating prompt..")
        prompt: str = get_prompt(context=self.context, question=self.question)
        
        endpoint_url: str = llm_config.endpoints_under_consideration[self.model_name] 
        client = OpenAI(base_url=endpoint_url, api_key=env_config.hugging_face_token)

        logger.info("Prompting model...")
        chat_completion = client.chat.completions.create(
            model="tgi",
            top_p=self.top_p,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
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
            if "choices" in message: # Prevents repetition
                letters_in_the_response: str | None = chat_completion.choices[0].message.content 

                if isinstance(letters_in_the_response, str) :
                    response_characters.append(letters_in_the_response)
                
                if self.save_data:
                    full_response = "" 
                    for i in response_characters:
                        full_response += i

                    self.record_responses(response=full_response, history=history) 

                if not to_frontend:
                    print(letters_in_the_response, end="")
                else:
                    return response_characters

    def record_responses(self, response: str, history: str) -> None:
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
                "response": response,
                "history": history
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

        if ("?" not in self.question) and ("." not in self.question):
            return self.question

        else:
            for character in self.question:
                if character in ["?", "."]:
                    truncated_question = self.question[: self.question.index(character) + 1] 
                    index.append(truncated_question)
                    break

            return index[0] 
            
         
if __name__ == "__main__":
    generator = PrimaryGenerator(
        question="How is international finance involved in neocolonialism?"
    )

    generator.query_llm(to_frontend=False)

