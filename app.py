import logging
from flask import Flask, request, jsonify, render_template
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from celery.result import AsyncResult
from celery_worker import app as celery_app, process_pdf

flask_app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Path to your credentials file

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
spreadsheet_id = '1v4FnbxnHkUIG0MSo3aHRFFAVHa4l51hcXF_YlLq6PaI'  # Replace with your Google Spreadsheet ID

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        data = []
        stream = file.stream.read().decode("UTF8")
        csv_reader = csv.reader(stream.splitlines())
        for row in csv_reader:
            if row:  # skip empty rows
                data.append({'user_id': row[0], 'resume_link': row[1]})
        return jsonify(data), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@flask_app.route('/search_keyword', methods=['POST'])
def search_keyword():
    data = request.json.get('data')
    keywords = request.json.get('keywords')
    if not keywords or not data:
        return jsonify({'error': 'Keywords and PDF URLs are required'}), 400

    total_keywords = len(keywords)
    task_ids = []

    for entry in data:
        task = process_pdf.apply_async(args=[entry, keywords, total_keywords])
        task_ids.append(task.id)

    return jsonify({'task_ids': task_ids}), 200

@flask_app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = AsyncResult(task_id, app=celery_app)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info,
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@flask_app.route('/save_results', methods=['POST'])
def save_results():
    results = request.json.get('results')
    if not results:
        return jsonify({'error': 'No results to save'}), 400

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        values = [['Timestamp', 'User ID', 'Resume Link', 'Checked', 'Percentage', 'Matched Technologies', 'Existing Technologies']]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for result in results:
            checked = 'Yes' if result['checked'] else 'No'
            values.append([
                timestamp, 
                result['user_id'], 
                result['resume_link'], 
                checked,
                result['percentage'], 
                ', '.join(result['matched_technologies']),
                ', '.join(result['existing_technologies'])
            ])

        body = {
            'values': values
        }

        append_result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        # Calculate the range to update formatting
        start_row = append_result['updates']['updatedRange'].split('!')[1].split(':')[0][1:]
        end_row = append_result['updates']['updatedRows'] + int(start_row) - 1
        range_to_format = f'Sheet1!A{start_row}:G{end_row}'

        # Remove bold formatting
        requests = [{
            'repeatCell': {
                'range': {
                    'startRowIndex': int(start_row) - 1,
                    'endRowIndex': end_row,
                    'startColumnIndex': 0,
                    'endColumnIndex': 7
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': False
                        }
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        }]

        body = {
            'requests': requests
        }

        sheet.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=8000, debug=True)
