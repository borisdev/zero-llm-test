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
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from langchain.llms import OpenAI
import llm_interface


image = Image.open("wide-mode.png")

if os.environ.get("LOCAL", False):
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
else:
    # streamlit cloud
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


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


llm_connection = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, max_tokens=1000)  # type: ignore
llm_connection_random = OpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY, max_tokens=1000)  # type: ignore


st.subheader("① Load a table")
uploaded_file = st.file_uploader("Upload CSV table", type="csv")

if uploaded_file:
    st.info("Table before AI formatting")
    input_table = pd.read_csv(uploaded_file)
    st.dataframe(input_table)
    st.write("")
    st.write("")
    st.info("Please wait for the AI transformation to complete")
    output_table = llm_interface.format_table(llm_connection, input_table)
    output_table.to_csv("data.csv", index=False)  # on disk for editable table
    st.success("AI transformation complete, go check it for errors!")
    st.subheader(" ② AI Output of a Formatted Table")
    st.info(
        """💡 You must select a row using the checkbox then fix the value and
        rationale. This fix will be used to re-train the AI (make a new prompt)
        and re-run the formating. Look at the above Table from step ① to see the
        original values."""
    )
    st.caption("")

    def show_grid():
        df = data_upload()
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True, groupable=True)
        # gd.configure_selection(selection_mode="multiple", use_checkbox=True)
        gridoptions = gd.build()

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)
        grid_table = AgGrid(
            df,
            # height=400,
            # gridOptions=gb.build(),
            gridOptions=gridoptions,
            # fit_columns_on_grid_load=True,
            theme="material",
            allow_unsafe_jscode=True,
        )
        return grid_table

    def update(grid_table):
        """write the new edits to the disk and then re-load this app to show new
        grid"""
        grid_table_df = pd.DataFrame(grid_table["data"])
        grid_table_df.to_csv("data.csv", index=False)

    grid_table = show_grid()
    # button push event will write the new table edits to the disk and then re-load this app
    st.sidebar.button(
        "Retrain AI with corrected examples and rationales",
        on_click=update,
        args=[grid_table],
    )
