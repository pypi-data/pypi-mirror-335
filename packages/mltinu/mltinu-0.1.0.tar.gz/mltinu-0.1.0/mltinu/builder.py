import os
import pandas as pd
import logging
from typing import Tuple, Dict, Any
from langchain_openai import ChatOpenAI

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Use INFO in production
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

class CodeBuilder:
    """
    CodeBuilder generates a complete machine learning pipeline code based on a CSV file's structure,
    a specified target variable, and a desired machine learning model.
    """

    def __init__(self, csv_path: str, target: str, model_name: str, provider: str = "groq"):
        """
        Initialize the CodeBuilder.
        
        Args:
            csv_path (str): Path to the CSV file.
            target (str): The target column in the CSV.
            model_name (str): The machine learning model to use (e.g., "RandomForest").
            provider (str, optional): AI provider to use ("openai" or "groq"). Defaults to "groq".
        """
        self.csv_path = csv_path
        self.target = target
        self.model_name = model_name
        self.provider = provider.lower()
        
        # Retrieve API key (here hard-coded; adjust if needed).
        self.api_key = "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"
        if not self.api_key:
            logger.error("API key is required. Set the 'API_KEY' environment variable.")
            raise ValueError("API key is required for AI provider access.")
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found at path: {self.csv_path}")
            raise FileNotFoundError(f"CSV file not found at path: {self.csv_path}")
        
        # Initialize the LangChain ChatOpenAI client.
        self.llm = ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key,
            model="llama-3.3-70b-versatile",
        )

    def _get_csv_info(self) -> Tuple[str, Dict[str, Any]]:
        """
        Reads the CSV file and extracts the first few rows and column data types.
        
        Returns:
            Tuple[str, Dict[str, Any]]: The CSV head as a string and a dictionary of column data types.
        """
        try:
            df = pd.read_csv(self.csv_path)
        except Exception as e:
            logger.exception("Failed to read CSV file.")
            raise e

        head_str = df.head().to_string()
        dtypes = df.dtypes.apply(lambda x: x.name).to_dict()
        logger.debug("CSV info extracted successfully.")
        return head_str, dtypes

    def _get_prompt(self, head_str: str, dtypes: Dict[str, Any]) -> str:
        """
        Constructs the prompt for the AI model.
        
        Args:
            head_str (str): A string representation of the CSV head.
            dtypes (Dict[str, Any]): A dictionary of column data types.
        
        Returns:
            str: The prompt that instructs the AI to generate the ML code.
        """
        prompt = (
    "You are TINU, an expert machine learning engineer. Generate complete, working Jupyter Notebook code that meets the following requirements:\n\n"
    "1. Load a CSV file with the following structure:\n"
    f"{head_str}\n\n"
    "2. Use the following column details:\n"
    f"{dtypes}\n\n"
    f"3. The target variable is '{self.target}'.\n"
    "4. Perform robust and comprehensive data preprocessing, including handling missing values if any.\n"
    f"5. Train a machine learning model: {self.model_name}.\n"
    "6. Evaluate the model and print all relevant evaluation metrics (accuracy, classification report, confusion matrix, etc.).\n"
    "7. Do not define any functions; implement the code directly in the notebook cells for immediate execution."
)

        logger.debug("Prompt generated successfully.")
        logger.debug("Prompt:\n%s", prompt)
        return prompt

    def generate_code(self) -> str:
        """
        Generates the ML code by invoking the AI provider.
        
        Returns:
            str: The generated Python code.
        """
        head_str, dtypes = self._get_csv_info()
        prompt = self._get_prompt(head_str, dtypes)
        try:
            response = self.llm.invoke(
                [
                    {"role": "system", "content": "You are a professional coder."},
                    {"role": "user", "content": prompt},
                ]
            )
            logger.debug("Raw LLM response: %s", response)
            code = response.content if hasattr(response, "content") else str(response)
            code = code.strip()
            logger.info("Code generated successfully.")
            return code
        except Exception as e:
            logger.exception("Error generating code with AI provider.")
            raise e

if __name__ == "__main__":
    builder = CodeBuilder(csv_path="data.csv", target="target", model_name="RandomForest", provider="groq")
    generated_code = builder.generate_code()
    print(generated_code)
