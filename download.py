import streamlit as st
import openai
import os
import csv
from io import StringIO, BytesIO

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Streamlit UI Design
st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements <b> powered by Open AI </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)

# Radio Button for Input Type Selection
test_case_source = st.radio("Generate test cases from:", ('Text Input', 'Uploaded Image'))

# Function to generate test cases
def generate_test_cases(requirement, format_option):
    # Append format-specific instructions
    if format_option == 'BDD':
        requirement += "\n\nGenerate the test cases in Gherkin syntax."
    elif format_option == 'NON-BDD':
        requirement += "\n\nGenerate the test cases in plain text format."
    elif format_option == 'Azure Template':
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

# Function to download CSV
def generate_csv(data, filename):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    output.seek(0)
    return st.download_button(
        label=f"Download {filename}.csv",
        data=output.getvalue(),
        file_name=f"{filename}.csv",
        mime="text/csv"
    )

# Function to render HTML table
def render_html_table(data, headers):
    html = "<table style='width: 100%; border: 1px solid black; border-collapse: collapse;'>"
    # Add header row
    html += "<tr>" + "".join([f"<th style='border: 1px solid black; padding: 8px;'>{header}</th>" for header in headers]) + "</tr>"
    # Add data rows
    for row in data:
        html += "<tr>" + "".join([f"<td style='border: 1px solid black; padding: 8px;'>{cell}</td>" for cell in row]) + "</tr>"
    html += "</table>"
    return html

# Text Input or Image Upload
if test_case_source == 'Text Input':
    requirement = st.text_area("Enter your requirement:", height=150)
else:
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        requirement = "Generate test cases based on the attached flow diagram."
    else:
        requirement = None

# Dropdown to Select Format
format_option = st.selectbox('Select Test Case Format', ['BDD', 'NON-BDD', 'Azure Template', 'Jira Template'])

# Generate Test Cases Button
if st.button('Generate Test Cases'):
    if requirement:
        with st.spinner('Generating test cases...'):
            try:
                test_cases = generate_test_cases(requirement, format_option)

                # For Azure and Jira Templates, handle data manually
                if format_option in ['Azure Template', 'Jira Template']:
                    # Define headers and process rows
                    if format_option == 'Azure Template':
                        headers = ['ID', 'Work Item Type', 'Title', 'Test Step', 'Step Action', 'Step Expected']
                    else:
                        headers = ['Description', 'Test Name', 'Test Step', 'Test Data', 'Expected Result']

                    # Parse test cases into rows
                    rows = [row.split(",") for row in test_cases.split("\n") if row]
                    st.markdown(render_html_table(rows, headers), unsafe_allow_html=True)
                    generate_csv([headers] + rows, format_option)
                else:
                    # Display plain text test cases
                    st.text_area("Generated Test Cases", test_cases, height=300)

                st.success("Test cases generated successfully!")
            except Exception as e:
                st.error("An error occurred while generating test cases.")
                st.error(e)
    else:
        st.error("Please provide a requirement or upload an image.")
