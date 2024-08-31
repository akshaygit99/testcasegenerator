import streamlit as st
import openai
import os

# Retrieve the API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
openai.api_key = OPENAI_API_KEY

st.markdown("""
<h1 style='text-align: center; color: white; background-color:#2c1a5d'>
<span style='color: #fdb825'>((</span>
             CENTRIC 
<span style='color: #fdb825'>))</span></h1>
<p style='font-size: 15px; text-align: left;'>This utility generates detailed software test cases based on user requirements, including BDD format, <b> powered by ChatGPT </b>. It's designed to streamline your testing process and improve efficiency.</p>
""", unsafe_allow_html=True)



# Streamlit app layout
st.title('Test Case Generator :  COE-AI Test')

st.write('Select the format for the test cases:')
format_type = st.selectbox('Choose format', ['BDD', 'NON-BDD'])

st.write('Enter your software requirement(s) to generate test cases:')

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

st.link_button("Centric India - AI Tool Usage Policy", "https://centricconsultingllc.sharepoint.com/sites/CentricIndia/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR%2FCentric%20India%20AI%20Tool%20Usage%20Policy%5F2023%2Epdf&parent=%2Fsites%2FCentricIndia%2FShared%20Documents%2FHR")

# Text area for user to enter the software requirement
requirement = st.text_area("Requirement", height=150)

# Define the function to generate test cases
def generate_test_cases(requirement, format_type):
    system_message = "Generate test cases in BDD format." if format_type == "BDD" else "Generate test cases in text format."

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": requirement}
        ]
    )

    return response.choices[0].message['content']

# Button to generate test cases
if st.button('Generate Test Cases'):
    if requirement:
        with st.spinner('Generating...'):
            try:
                # Generate test cases based on the requirement and selected format
                test_cases = generate_test_cases(requirement, format_type)

                st.success('Generated Test Cases')
                st.write(test_cases)

            except Exception as e:
                st.error('An error occurred while generating test cases.')
                st.error(e)

            st.session_state.search_history.append(requirement)
    else:
        st.error('Please enter a requirement to generate test cases.')

st.write('Search History:')
st.write(st.session_state.search_history)
