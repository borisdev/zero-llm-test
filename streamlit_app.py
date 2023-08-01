"""
User Interface for capturing corrections and rationales for AI table formatting.

TODOs:

    - use callback funtions wih llm calls

Code based on:

    https://github.com/streamlit/example-app-editable-dataframe/blob/main/streamlit_app.py
"""
import os
import streamlit as st
import pandas as pd
from PIL import Image
from langchain.llms import OpenAI
import llm_interface


image = Image.open("wide-mode.png")

if os.environ.get("LOCAL", False):
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
else:
    # streamlit cloud
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


def dataframe_with_selections(df):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop("Select", axis=1)


@st.cache_data
def llm_format_table(input_table: pd.DataFrame) -> pd.DataFrame:
    llm_connection = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, max_tokens=1000)  # type: ignore
    output_table = llm_interface.format_table(llm_connection, input_table)  # type: ignore
    return output_table


st.title("Format tables using corrections and rationales")

st.markdown(
    """
    ## What is happening here?

    - you upload a table and fix the AI transform errors
    - your fix of each error must include a better field mapping rationale or
      value transform rationale
    - your better rationales are then fed back into the AI system

    The code is [here](https://github.com/borisdev/zero-llm-test).

    Please change to the wide mode setting in the top right corner of the
    screen.
    """
)
st.image(image, width=200, caption="wide mode setting")


def data_upload():
    df = pd.read_csv("data.csv")
    return df


llm_connection_random = OpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY, max_tokens=1000)  # type: ignore


st.subheader("① Load a table")
uploaded_file = st.file_uploader("Upload CSV table", type="csv")

if uploaded_file:
    st.info("Table before AI formatting")
    input_table = pd.read_csv(uploaded_file)
    st.dataframe(input_table)
    st.info("Please wait 30 secs for the AI transformation to complete")
    output_table = llm_format_table(input_table)  # type: ignore
    st.success("AI transformation complete, go check it for errors!")
    st.info("Table after AI formatting")
    st.dataframe(output_table)
    # TODO: let user select a row to fix, show row in vertical form
    # selection = dataframe_with_selections(output_table)
    # st.write("Your selection:")
    # st.write(selection)
    st.subheader(" ② Fix AI error")

    with st.form("input_form"):
        st.info(
            """💡 Your fix will re-train the AI system. Submit the fix as a sentence."""
        )
        # fmt: off
        st.warning(
            """This is a UI prototype - how the user's fix is submitted
                must be improved upon by experimentation""")
        example_fix = (
            """
            for row 0 set the 'Date.value' field to '05-01-2023' and set the 'Data.value_rationale' to 'format as MM-DD-YYYY' AND assume USA'
            """
        )
        # fmt: on
        user_fix = st.text_input("Fix", example_fix)
        clickSubmit = st.form_submit_button("Submit")

    if clickSubmit:
        output_table = llm_format_table(input_table)  # type: ignore
        st.info("Table after AI formatting AND and after retrain with your fix")
        st.warning("This is a UI prototype, the retrain is not yet implemented")
        st.dataframe(output_table)
    else:
        st.markdown("Please submit to save")
