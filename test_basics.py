import unittest
import pandas as pd
from langchain import OpenAI
import llm_interface


class TestTDD(unittest.TestCase):
    """Integration tests to format a table."""

    def test_format_table(self):
        """
        transform a csv file table into pandas table with standardized values

        async llm per record calls required by streamlit
        """
        llm = OpenAI(temperature=0, max_tokens=1000)  # type: ignore
        csv_table = "table_B.csv"
        input_table = pd.read_csv(csv_table)
        output_table = llm_interface.format_table(llm, input_table)  # type: ignore
        print(output_table)

    def test_retrain(self):
        """
        retrain AI system by addin the corrected record as a new example in the
        prompt template
        """
        llm = OpenAI(temperature=0, max_tokens=1000)  # type: ignore
        csv_table = "table_B.csv"
        input_table = pd.read_csv(csv_table)
        output_table = llm_interface.format_table(llm, input_table)  # type: ignore
        print(output_table)
        # LLM will translate the user's natural langauge fix into a SQL query to reset the examples
        # table
        # Date.value
        # Date.tranform_rationale
