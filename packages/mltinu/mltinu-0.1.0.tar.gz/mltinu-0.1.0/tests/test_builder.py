import os
import unittest
from unittest.mock import patch
import pandas as pd

# Import the CodeBuilder from your package
from mltinu.builder import CodeBuilder

class TestCodeBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary CSV file for testing.
        cls.test_csv = "test_data.csv"
        data = {
            "id": [1, 2, 3],
            "age": [25, 30, 22],
            "salary": [50000, 60000, 45000],
            "department": ["sales", "engineering", "sales"],
            "target": [0, 1, 0]
        }
        pd.DataFrame(data).to_csv(cls.test_csv, index=False)
        
        # Create or clear the log file.
        cls.log_file = "test_io_log.txt"
        with open(cls.log_file, "w") as f:
            f.write("Test IO Log\n\n")
    
    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary CSV file.
        if os.path.exists(cls.test_csv):
            os.remove(cls.test_csv)
        # Optionally, you could also remove the log file if desired.
    
    def log_io(self, test_name: str, head_str: str, dtypes: dict, prompt: str, generated_code: str):
        """Append test input (CSV head, dtypes, prompt) and output (generated code) to a log file."""
        with open(self.log_file, "a") as f:
            f.write(f"Test: {test_name}\n")
            f.write("CSV Head:\n")
            f.write(head_str + "\n")
            f.write("Dtypes:\n")
            f.write(str(dtypes) + "\n")
            f.write("Prompt:\n")
            f.write(prompt + "\n")
            f.write("Generated Code:\n")
            f.write(generated_code + "\n")
            f.write("=" * 60 + "\n\n")
    
    def test_get_csv_info(self):
        # Instantiate CodeBuilder using the test CSV.
        builder = CodeBuilder(
            csv_path=self.test_csv,
            target="target",
            model_name="RandomForest",
            provider="openai"
        )
        head_str, dtypes = builder._get_csv_info()
        
        self.assertIn("id", head_str)
        self.assertIn("age", dtypes)
        self.assertEqual(dtypes["age"], "int64")
        
        # Log CSV head and dtypes.
        with open(self.log_file, "a") as f:
            f.write("Test: test_get_csv_info\n")
            f.write("CSV Head:\n" + head_str + "\n")
            f.write("Dtypes:\n" + str(dtypes) + "\n\n")
    
    @patch("mltinu.builder.ChatOpenAI.invoke")
    def test_generate_code_openai(self, mock_invoke):
        # Create a dummy response for the openai provider.
        class DummyResponse:
            content = "Generated ML code from OpenAI"
        mock_invoke.return_value = DummyResponse()
        
        builder = CodeBuilder(
            csv_path=self.test_csv,
            target="target",
            model_name="RandomForest",
            provider="openai"
        )
        head_str, dtypes = builder._get_csv_info()
        prompt_text = builder._get_prompt(head_str, dtypes)
        generated_code = builder.generate_code()
        
        self.assertEqual(generated_code, "Generated ML code from OpenAI")
        self.log_io("test_generate_code_openai", head_str, dtypes, prompt_text, generated_code)
    
    @patch("mltinu.builder.ChatOpenAI.invoke")
    def test_generate_code_groq(self, mock_invoke):
        # Create a dummy response for the groq provider.
        class DummyResponse:
            content = "Generated ML code from Groq"
        mock_invoke.return_value = DummyResponse()
        
        builder = CodeBuilder(
            csv_path=self.test_csv,
            target="target",
            model_name="RandomForest",
            provider="groq"
        )
        head_str, dtypes = builder._get_csv_info()
        prompt_text = builder._get_prompt(head_str, dtypes)
        generated_code = builder.generate_code()
        
        self.assertEqual(generated_code, "Generated ML code from Groq")
        self.log_io("test_generate_code_groq", head_str, dtypes, prompt_text, generated_code)

if __name__ == '__main__':
    unittest.main()
