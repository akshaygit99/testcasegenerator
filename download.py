import streamlit as st
import openai
import pandas as pd
from io import BytesIO

# Retrieve the API key from the environment variable
openai.api_key = "your_openai_api_key"  # Replace with your API key

# Function to generate test cases
def generate_test_cases(requirement, format_option):
    # Append additional instructions based on format
    if format_option == 'Azure Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "ID (leave this column empty), Work Item Type (set to 'Test Case'), Title, Test Step, Step Action, and Step Expected. "
            "Ensure each test case contains more than one test step."
        )
    elif format_option == 'Jira Template':
        requirement += (
            "\n\nGenerate the test cases in a tabular format with the following columns: "
            "Description, Test Name, Test Step, Test Data, and Expected Result. "
            "Ensure each test case contains more than one test step."
        )

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant capable of generating software test cases."},
            {"role": "user", "content": requirement}
        ]
    )
    return response.choices[0].message['content']

# Function to download data as a CSV file
def download_button(dataframe, filename):
    output = BytesIO()
    dataframe.to_csv(output, index=False)
    output.seek(0)
    return st.download_button(
        label=f"Download {filename}",
        data=output,
        file_name=filename,
        mime="text/csv"
    )

# Streamlit UI
st.title("Test Case Generator")

# Input for test case requirements
requirement = st.text_area("Enter your requirement", height=150)

# Dropdown for test case format selection
format_option = st.selectbox('Choose Test Case Format', ['Azure Template', 'Jira Template'])

# Button to generate test cases
if st.button('Generate Test Cases'):
    if requirement.strip():
        with st.spinner("Generating test cases..."):
            try:
                test_cases = generate_test_cases(requirement, format_option)

                # Process test cases into a DataFrame for Azure and Jira templates
                if format_option == 'Azure Template':
                    columns = ['ID', 'Work Item Type', 'Title', 'Test Step', 'Step Action', 'Step Expected']
                elif format_option == 'Jira Template':
                    columns = ['Description', 'Test Name', 'Test Step', 'Test Data', 'Expected Result']

                rows = [row.split(",") for row in test_cases.strip().split("\n") if row]
                df = pd.DataFrame(rows, columns=columns)

                # Display the table and download button
                st.write("Generated Test Cases:")
                st.dataframe(df)
                download_button(df, f"{format_option}_Test_Cases.csv")

            except Exception as e:
                st.error("An error occurred while generating test cases.")
                st.error(e)
    else:
        st.error("Please enter a requirement to generate test cases.")
