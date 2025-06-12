# LearnTube AI Career Coach - Streamlit Frontend

This is a Streamlit-based chatbot interface for the LearnTube AI Career Coach application.

## Features

- 🚀 Interactive chat interface with AI career coach
- 📊 Job fit analysis with visual feedback
- 👤 LinkedIn profile integration and display
- 💬 Real-time chat with persistent session state
- 📝 Quick action buttons for common queries
- 🎨 Clean, modern UI with custom styling

## Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. **First, make sure the backend is running** on http://localhost:8000

2. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

3. The app will open in your browser at http://localhost:8501

## Usage

1. **Start a Session**: 
   - Enter your LinkedIn profile URL in the sidebar
   - Or click "Skip LinkedIn" to start without profile analysis

2. **Chat with AI Career Coach**:
   - Type your questions in the chat input
   - Use quick action buttons for common queries
   - View job fit analysis and career recommendations

3. **Profile Management**:
   - Your profile summary appears in the sidebar
   - The AI updates your profile as you share information
   - Start a new session anytime

## Configuration

To change the backend API URL, modify the `API_BASE_URL` variable in `streamlit_app.py`:

```python
API_BASE_URL = "http://localhost:8000"  # Change this to your backend URL
```

## Troubleshooting

- **Connection Error**: Ensure the backend is running on http://localhost:8000
- **Session Issues**: Click "Start New Session" to reset
- **API Errors**: Check the backend logs for detailed error messages 