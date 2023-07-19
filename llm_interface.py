import json
import asyncio
import pandas as pd
from langchain.chains import LLMChain
from prompt_template import retrainer
from py_console import console


async def _async_chain(llm_connection, record):
    llm_chain = LLMChain(llm=llm_connection, prompt=retrainer.make_prompt_template())
    llm_input = json.dumps(record, indent=4)
    completion = await llm_chain.arun(llm_input)
    tranformed_record = json.loads(completion)
    console.info(record)
    return tranformed_record


async def _generate_concurrently(llm_connection, records):
    tasks = [_async_chain(llm_connection, record) for record in records]
    transformed_records = await asyncio.gather(*tasks)
    return transformed_records


def format_table(llm_connection, table: pd.DataFrame) -> pd.DataFrame:
    """
    sends many async calls to LLM to format rows
    """
    records = table.to_dict(orient="records")  # type: ignore

    transformed_records = asyncio.run(_generate_concurrently(llm_connection, records))
    output_table = pd.DataFrame(transformed_records)
    console.success(output_table.to_string())
    return output_table
