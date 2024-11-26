import re
import math
import pandas as pd
import streamlit as st
from io import BytesIO

# Function to process the text files
def process_text_files(uploaded_files):
    results = pd.DataFrame(columns=["Name", "Date", "Trial", "Resultant_Force"])

    # List to store each row of results
    rows = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name

        name_part = file_name.split("_")[0]
        trial_number = file_name.split("_")[1]

        file_date = ""
        max_force = 0
        start_line = False

        # Read the content of the file
        for line in uploaded_file.getvalue().decode("utf-8").splitlines():
            # Check if the line contains the date
            if "Date" in line and not file_date:
                # Extract the full date and time (e.g., "Sep 25, 2024 17:29:18")
                file_date = line.split()[1:4]  # Capturing Month, Day, and Year
                file_date = " ".join(file_date)  # Joining them into a single string

            if start_line:
                line_array = re.split(r'\t+', line.strip())
                if len(line_array) >= 4:
                    try:
                        fx = float(line_array[1])  # Attempt to convert to float
                        fz = float(line_array[3])  # Attempt to convert to float
                        calc_force = math.sqrt(fx ** 2 + fz ** 2)
                        calc_force = round(calc_force, 1)  # Round the resultant force to 1 decimal place
                        if calc_force > max_force:
                            max_force = calc_force
                    except ValueError:
                        # Skip lines where conversion to float fails
                        continue

            if "abs time" in line:
                start_line = True

        # If no date was found in the file content, extract it from the filename
        if not file_date:
            try:
                # Extract the part after the last underscore and before .txt
                date_part = file_name.split("_")[-1].replace(".txt", "")
                day, month, year = date_part.split(".")
                if len(year) == 2:  # If year is 2 digits, add '20' prefix
                    year = f"20{year}"
                file_date = f"{day} {month} {year}"  # Format as day month year
            except Exception as e:
                st.error(f"Error processing date from filename: {file_name}, {str(e)}")
                continue

        # Add the result row to the list
        rows.append({
            "Name": name_part,
            "Date": file_date,
            "Trial": trial_number,
            "Resultant_Force": max_force
        })

    # Concatenate the list of rows into the results DataFrame
    results = pd.concat([results, pd.DataFrame(rows)], ignore_index=True)

    # Convert the Date column to dd/mm/yyyy format
    results['Date'] = pd.to_datetime(results['Date'], format="%d %m %Y").dt.strftime('%d/%m/%Y')
    
    return results

# Streamlit app
def main():
    st.title("Iso Leg Press File Processor")
    st.write("Upload multiple text files to extract the data and calculate resultant forces.")

    # Upload multiple text files
    uploaded_files = st.file_uploader("Choose text files", accept_multiple_files=True, type="txt")

    if uploaded_files:
        if st.button("Process Files"):
            with st.spinner("Processing files..."):
                results = process_text_files(uploaded_files)
                st.success("Processing complete!")
                
                # Show the results
                st.dataframe(results)

                # Allow download of the results as Excel
                towrite = BytesIO()
                results.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                
                st.download_button(label="Download Results as Excel", data=towrite,
                                   file_name="Results.xlsx", mime="application/vnd.ms-excel")

if __name__ == "__main__":
    main()
