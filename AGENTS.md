## How to run this application

This is a Flask web application with a separate frontend.

### Backend

1.  **Set up Google Drive API Credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Create a new project.
    - Enable the "Google Drive API".
    - Create credentials for a "Web application".
    - From the credentials screen, download the `client_secret.json` file.
    - **Important:** Rename the downloaded file to `credentials.json` and place it in the `backend/` directory.

2.  **Install dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Run the Flask development server:**
    ```bash
    python backend/app.py
    ```
    The backend will be running at `http://127.0.0.1:5000`.

### Frontend

1.  The frontend is a simple set of static files. You can open `frontend/index.html` directly in your browser, but for it to communicate with the backend, it's better to serve it.

2.  For development, the Flask app will serve the `index.html` from the `frontend` directory.

### Project Structure

- `AGENTS.md`: This file.
- `backend/`: The Flask application.
  - `app.py`: The main application file.
  - `requirements.txt`: Python dependencies.
  - `credentials.json`: (You need to create this) Google API credentials.
  - `templates/`: (Will be created) For server-side rendered HTML templates if needed.
  - `static/`: (Will be created) For static assets served by Flask.
- `frontend/`: The user interface.
  - `index.html`: The main page.
  - `style.css`: Styles for the page.
  - `script.js`: JavaScript for interactivity.
