### Resume Keywords Searching

This repository provides a tool to search for keywords within resumes and save the results to a Google Spreadsheet. Below is an overview of the structure and functionality of the repository:

#### Project Structure

- **.devcontainer/**
  - `devcontainer.json`: Configuration for the development container.
- **.vscode/**
  - `launch.json`: Configuration for debugging the application.
- `Procfile`: Instructions for Heroku deployment.
- `README.md`: This file.
- `app.py`: The main Flask application file.
- `credentials.json`: Google API credentials for accessing Google Sheets.
- `requirements.txt`: List of dependencies.
- **static/**
  - `script.js`: JavaScript for client-side functionality.
  - `styles.css`: CSS for styling the web pages.
- `streamlit_app.py`: Streamlit application script to embed the Flask app.
- **templates/**
  - `index.html`: Main HTML template.

#### Files Description

- **app.py**: 
  - Main Flask application that handles:
    - Google Sheets API setup.
    - Downloading and processing PDF resumes.
    - Searching for keywords within resumes.
    - Uploading and searching CSV files.
    - Saving results to Google Sheets.
  - Defines routes for the application (`/`, `/upload_csv`, `/search_keyword`, `/save_results`).

- **streamlit_app.py**: 
  - Script to start the Flask app using Streamlit and embed it in an iframe.

- **requirements.txt**: 
  - Lists all the dependencies required to run the application such as Flask, gunicorn, requests, PyPDF2, Google Auth libraries, and Streamlit.

- **static/script.js**:
  - Client-side JavaScript to handle file upload, keyword search, and saving results. 
  - Provides interactivity and communication between the frontend and backend.

- **static/styles.css**:
  - CSS to style the web pages, ensuring a responsive and user-friendly design.

- **templates/index.html**:
  - Main HTML template for the web application.
  - Includes input fields for uploading CSV files and entering keywords.
  - Displays the results in a table format.

### Usage Instructions

1. **Setup and Installation**:
    - Ensure you have Python and pip installed.
    - Clone the repository:
      ```bash
      git clone https://github.com/kellatirupathi/Resume_key.git
      cd Resume_key
      ```
    - Install the required dependencies:
      ```bash
      pip install -r requirements.txt
      ```
    - Make sure you have the `credentials.json` file in the root directory for Google Sheets API access.

2. **Running the Application**:
    - Start the Flask application:
      ```bash
      python app.py
      ```
    - Alternatively, you can start the application using Streamlit:
      ```bash
      streamlit run streamlit_app.py
      ```

3. **Using the Application**:
    - Open the web application in your browser.
    - Upload a CSV file containing user IDs and resume links.
    - Enter the keywords you want to search for.
    - Click the "Search" button to find matches in the resumes.
    - Save the results to a Google Spreadsheet by clicking the "Save" button.

4. **Deployment**:
    - You can deploy the application to Heroku using the provided `Procfile`.

### Note

- Ensure that the resume links provided in the CSV file are accessible and downloadable.
- Adjust the max workers in `search_keyword_in_pdfs` based on your server capacity.
