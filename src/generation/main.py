from loguru import logger
from openai import OpenAI
from collections.abc import Generator

from src.setup.config import env_config, hf_config  
from src.generation.appendix import get_prompt, get_context, record_responses 


class PrimaryGenerator:
    def __init__(
            self, 
            question: str, 
            top_p: float | None = 0, 
            temperature: int | None = 0, 
            max_tokens: int = 2000,
            save_data: bool = True,
            model_name: str = hf_config.preferred_model
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
            
    def query_llm(self, to_frontend: bool) -> Generator[str|None] | None:
        """Gets the context, and uses it (as well as the question) to construct a prompt."""
        
        assert self.model_name in hf_config.endpoints_under_consideration.keys()

        logger.info(f"Question: {self.question}")
        logger.info("Creating prompt..")
        prompt: str = get_prompt(context=self.context, question=self.question)
        
        endpoint_url: str = hf_config.endpoints_under_consideration[self.model_name] 
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

                    record_responses(response=full_response, history=history) 

                if not to_frontend:
                    print(letters_in_the_response, end="")
                else:
                    return response_characters



if __name__ == "__main__":
    generator = PrimaryGenerator(
        question="How is international finance involved in neocolonialism?"
    )

    generator.query_llm(to_frontend=False)


