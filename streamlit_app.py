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
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


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
    st.success("AI transformation complete")
    st.subheader(" ② Find an AI error to fix as as new training example")
    st.write("")
    st.info(
        """After you edit a row, you must (re) click to the checkbox col to
            save it. Look at the orginal source table above to help you."""
    )
    st.info(
        """In the future we can combine the input and output tables so its
               easier for the user to find errors to fix."""
    )
    df = output_table
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    gd.configure_selection(selection_mode="single", use_checkbox=True)
    gridoptions = gd.build()
    grid_table = AgGrid(
        df,
        gridOptions=gridoptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="material",
    )
    sel_row = grid_table["selected_rows"]
    st.subheader("③ Check your row fix and submit it")
    st.write("")
    df_sel_row = pd.DataFrame(sel_row)
    if not df_sel_row.empty:
        st.write(df_sel_row.to_dict("records"))
        clickSubmitFix = st.button("Submit fix and re-run AI formatting")
        if clickSubmitFix:
            output_table = llm_format_table(input_table)  # type: ignore
            st.info("Formatted Table after retraining with your fix")
            st.warning(
                """This is a UI prototype, the retrain is not yet
                       implemented as a placeholder you see the same table."""
            )
            st.dataframe(output_table)
