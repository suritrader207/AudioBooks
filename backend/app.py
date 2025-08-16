import os
from flask import Flask, send_from_directory, session, redirect, request, url_for, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__, static_folder='../frontend/static')
app.secret_key = 'your_secret_key'  # Replace with a real secret key in production

# This is the path to the client secrets file.
CLIENT_SECRETS_FILE = "backend/credentials.json"

# This is the scope for the Google Drive API. It allows for full access.
SCOPES = ['https://www.googleapis.com/auth/drive']

# --- Routes for serving frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_frontend_files(path):
    return send_from_directory('../frontend', path)

# --- Google Drive API Authentication ---

@app.route('/authorize')
def authorize():
    """Starts the OAuth 2.0 authorization flow."""
    # Create a flow instance to manage the OAuth 2.0 flow.
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )

    # The authorization_url is the URL that the user will be redirected to
    # to give consent to the application.
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    # Store the state so we can verify it in the callback.
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """Handles the callback from the OAuth 2.0 server."""
    state = session['state']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )

    # Use the authorization response code to fetch the access token.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    # ACTION ITEM: In a production app, you would want to store these
    #              credentials in a secure database.
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect(url_for('serve_index'))


@app.route('/clear')
def clear_credentials():
    """Clears the user's credentials from the session."""
    if 'credentials' in session:
        del session['credentials']
    return 'Credentials cleared'

# --- API Endpoints ---
from werkzeug.utils import secure_filename
from googleapiclient.http import MediaFileUpload

@app.route('/api/is_authenticated')
def is_authenticated():
    """Checks if the user is authenticated with Google Drive."""
    return jsonify({'is_authenticated': 'credentials' in session})

@app.route('/api/books', methods=['GET'])
def list_books():
    """Lists all the audiobooks from Google Drive."""
    if 'credentials' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    creds = Credentials(**session['credentials'])
    service = build('drive', 'v3', credentials=creds)

    # List all files in the user's drive.
    # In a real app, you would filter this to only show files created by your app.
    results = service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, webContentLink)"
    ).execute()

    items = results.get('files', [])

    return jsonify(items)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handles file uploads to Google Drive."""
    if 'credentials' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    title = request.form.get('title', 'Untitled')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)

        # Build the Drive API client
        creds = Credentials(**session['credentials'])
        service = build('drive', 'v3', credentials=creds)

        # File metadata
        file_metadata = {
            'name': title,
            # In a real app, you might want to create a specific folder for your app
            # and upload the files there. For this example, we upload to the root.
        }

        # Media body
        media = MediaFileUpload(
            file,
            mimetype=file.mimetype,
            resumable=True
        )

        # Upload the file
        request_obj = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )

        response = None
        while response is None:
            status, response = request_obj.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")

        print(f"File uploaded successfully! File ID: {response.get('id')}")

        return jsonify({'success': True, 'file_id': response.get('id')})

    return jsonify({'error': 'An unexpected error occurred.'}), 500


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production, ensure that you are serving over HTTPS
    #     and remove this line.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    if not os.path.exists(CLIENT_SECRETS_FILE):
        print("Error: credentials.json not found. Please follow the instructions in AGENTS.md to create it.")
    else:
        app.run(debug=True, port=5000)
