"""
Compose LLM prompt with customer input-output examples and rationales

Rationales are a type of user annotation or tag that the customer is providing
to train the AI system to understand the customer's transform or table
formatting intent.

"""
import json

# import pandas as pd
from langchain.prompts.prompt import PromptTemplate
from langchain import FewShotPromptTemplate
from pydantic import (
    BaseModel,
    Field,
)


def seed_examples() -> list:
    """
    boostrap the retraining process by seeding the prompt with one manually
    formatted example input-output pair from both zero's table A and table B
    """
    # df = pd.read_csv("table_A.csv")
    # table_A_input_example = df.to_dict(orient="records")[0]  # type: ignore
    table_A_input_example = {
        "Date_of_Policy": "05/01/2023",
        "Department": "IT",
        "FullName": "John Doe",
        "Full_Name": "John Doe",
        "Insurance_Plan": "Gold Plan",
        "Insurance_Type": "Gold",
        "JobTitle": "Software Engineer",
        "Monthly_Cost": 150,
        "Monthly_Premium": 150,
        "Policy_No": "AB-12345",
        "Policy_Num": "AB-12345",
        "Policy_Start": "05/01/2023",
    }
    table_A_output_example = {
        "Date.fields": '"Date_of_Policy" OR "Policy_Start"',
        "Date.mapping_rationale": "date like",
        "Date.value": "__invalid__",
        "Date.transform_rationale": "ambiguous input format (mm-dd or dd-mm)",
        "EmployeeName.fields": '"FullName" OR "Full_Name"',
        "EmployeeName.mapping_rationale": "name like",
        "EmployeeName.value": "John Doe",
        "EmployeeName.transform_rationale": "mapped col vals are same AND format correct",
        "Plan.fields": '"Insurance_Plan" OR Insurance_Type"',
        "Plan.mapping_rationale": "insurance plan like",
        "Plan.value": "Gold",
        "Plan.transform_rationale": "keep pattern (Gold, Bronze, Silver)",
        "PolicyNumber.fields": '"Policy_No" OR "Policy_Num"',
        "PolicyNumber.mapping_rationale": "policy number like",
        "PolicyNumber.value": "AB-12345",
        "PolicyNumber.transform_rationale": "mapped cols are same AND format correct",
        "Premium.fields": '"Monthly_Cost" OR "Monthly_Premium"',
        "Premium.mapping_rationale": "premium cost like",
        "Premium.value": 150,
        "Premium.transform_rationale": "mapped cols are same AND format correct",
    }
    io_pair = {
        "record": table_A_input_example,
        "formatted_record": table_A_output_example,
    }
    return [io_pair]


def escaped_json(d):
    """Escape curly braces in json string so that it can be used in f-string"""
    return json.dumps(d, indent=2).replace("{", "{{").replace("}", "}}")


def escaped_json_for_io_examples(io_examples: list) -> list:
    result = []
    for example in io_examples:
        result.append(
            {
                "record": escaped_json(example.record),
                "formatted_record": escaped_json(example.formatted_record),
            }
        )
    return result


class IOExample(BaseModel):
    record: dict = Field(description="unformmated input record")
    formatted_record: dict = Field(description="formatted output record")


class ReTrainer(BaseModel):
    io_examples: list[IOExample] = Field(description="LLM prompt training examples")

    @property
    def _mapping_rationales(self) -> str:
        rationales = []
        for example in self.io_examples:
            for key, value in example.formatted_record.items():
                if key.endswith("mapping_rationale"):
                    rationales.append(value)
        result = list(set(rationales))
        result = escaped_json(result)
        return result

    @property
    def _transform_rationales(self) -> str:
        rationales = []
        for example in self.io_examples:
            for key, value in example.formatted_record.items():
                if key.endswith("transform_rationale"):
                    rationales.append(value)
        result = list(set(rationales))
        result = escaped_json(result)
        return result

    def make_prompt_template(self):
        """dynamically compose the prompt template based on the updated io examples"""
        # fmt: off
        prefix_template = (
            """
            Create a new output object based on the given input object.

            Your output should be a valid json object.

            The new object must have the below additional classes of fields.

                - Date
                - EmployeeName
                - Plan
                - PolicyNumber
                - Premium

            There are two steps to this task.

            The first step is to map the fields from the input object that can be used to populate the output object's fields. Extract the input object's fields that appear to contain the most relevant information. You must provide a rationale for why you selected the input field or fields.


            The second step is to transforming the input values into a standard format. Standard format can be inferred using the rationales and value patterns of the input-output examples below.

            Do not make up your own rationales.

            You must only use field mapping rationales from this list below.

                {mapping_rationales}

            You must only use field transform rationales from this list below.

                {transform_rationales}

            Follow the pattern in the input-output examples listed below.
            """
        ).strip()
        # fmt: on

        io_example_template = """
            INPUT: {record}
            OUTPUT: {formatted_record}
        """
        suffix_template = """
            INPUT: {record}
            OUTPUT:
        """
        prefix = prefix_template.format(
            mapping_rationales=self._mapping_rationales,
            transform_rationales=self._transform_rationales,
        )

        io_example_prompt_template = PromptTemplate(
            input_variables=["record", "formatted_record"], template=io_example_template
        )

        # self.io_examples changes
        prompt_template = FewShotPromptTemplate(
            examples=escaped_json_for_io_examples(self.io_examples),
            example_prompt=io_example_prompt_template,
            prefix=prefix,
            suffix=suffix_template,
            input_variables=["record"],
            example_separator="\n\n",
        )
        return prompt_template


retrainer = ReTrainer(io_examples=seed_examples())
