import logging
import os
from abc import ABC, abstractmethod
import openai

class LLMStrategy(ABC):
    @abstractmethod
    def process(self, md_file):
        pass

class SaveLocally(LLMStrategy):
    def process(self, md_file):
        logging.info(f"File saved locally: {md_file}")

class InsertIntoLLM(LLMStrategy):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")  # Read from environment
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")  # Default model if not set

        if not self.api_key:
            raise ValueError("Missing OpenAI API key. Please set it in the environment.")

        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except openai.OpenAIError as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError("Invalid OpenAI API key.")

    def process(self, md_file):
        try:
            with open(md_file, "r", encoding="utf-8") as file:
                content = file.read()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Process this Markdown content."},
                    {"role": "user", "content": content}
                ]
            )

            llm_response = response.choices[0].message.content
            logging.info(f"LLM Response for {md_file}: {llm_response}")

        except FileNotFoundError:
            logging.error(f"Markdown file not found: {md_file}")
        except openai.OpenAIError as e:
            logging.error(f"OpenAI API error while processing {md_file}: {e}")
        except Exception as e:
            logging.exception(f"Unexpected error processing {md_file}: {e}")
