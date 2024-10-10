# Split the generated test cases into rows for the DataFrame
rows = [line.strip() for line in test_cases.split('\n') if line.strip()]

# Define columns based on the selected template
if format_option == 'Test Case Template':
    if template_type == 'Jira Template':
        columns = ['Test Case Number', 'Expected Result', 'Actual Result']
        expected_num_columns = 3
    elif template_type == 'Azure Template':
        columns = ['Test Case Number', 'Expected Result', 'Actual Result', 'Bug ID']
        expected_num_columns = 4

    # Split the rows into columns and fill in missing values if necessary
    data = []
    for row in rows:
        split_row = row.split(',')
        if len(split_row) < expected_num_columns:
            # Fill missing columns with None if fewer columns are provided
            split_row.extend([None] * (expected_num_columns - len(split_row)))
        data.append(split_row)

    # Create the DataFrame with the appropriate columns
    df = pd.DataFrame(data, columns=columns)

    # Display the test cases in tabular format
    st.dataframe(df)

    # Provide a download link for the DataFrame as an Excel file
    download_link = create_download_link(df, f"{template_type.replace(' ', '_')}_Test_Cases")
    st.markdown(download_link, unsafe_allow_html=True)
