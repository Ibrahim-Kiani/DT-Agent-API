# Smart Hospital AI Agent API

A Flask API that provides AI-powered hospital management assistance using OpenRouter and the Smart Hospital backend.

## Features

- AI-powered chat interface for hospital queries
- Direct access to hospital data endpoints
- Automatic data fetching based on query context
- RESTful API design
- Easy deployment on Render

## API Endpoints

### 1. Health Check
```
GET /
```
Returns API status and version information.

### 2. Chat Interface
```
POST /chat
```
Send a message to the AI agent.

**Request Body:**
```json
{
  "message": "Show me all patients currently in the hospital",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Based on the current hospital data, here are all patients...",
  "tool_calls_made": 1,
  "tools_used": ["get_all_patients"],
  "conversation_history": [...]
}
```

### 3. Hospital Data Access
```
GET /hospital-data/<endpoint>
```
Direct access to hospital data. Available endpoints:
- `patients` - Get all patients
- `alerts` - Get current alerts
- `staff` - Get all staff
- `rooms` - Get all rooms
- `beds` - Get all beds
- `devices` - Get IoT devices
- `anomalies` - Get anomalies
- `simulation` - Get simulation status

## Deployment Steps

### Step 1: Prepare Your Files

Create a new folder with these files:
- `app.py` (main Flask application)
- `requirements.txt` (Python dependencies)
- `render.yaml` (Render configuration)
- `test_api.py` (testing script)
- `README.md` (this file)

### Step 2: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it something like `smart-hospital-ai-api`
3. Upload all the files to this repository

### Step 3: Deploy on Render

1. Go to [Render](https://render.com) and sign up/log in
2. Click "New +" and select "Web Service"
3. Connect your GitHub account
4. Select your repository
5. Fill in the deployment settings:
   - **Name**: `smart-hospital-ai-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Step 4: Set Environment Variables

In Render dashboard:
1. Go to your service settings
2. Click "Environment"
3. Add environment variable:
   - **Key**: `OPENROUTER_API_KEY`
   - **Value**: Your OpenRouter API key

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your API will be available at: `https://your-app-name.onrender.com`

## Testing Your API

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY="your-api-key-here"

# Run locally
python app.py
```

### Test with curl
```bash
# Health check
curl https://your-app-name.onrender.com/

# Chat endpoint
curl -X POST https://your-app-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all patients"}'

# Hospital data
curl https://your-app-name.onrender.com/hospital-data/patients
```

### Test with Python
```python
import requests

# Test the API
response = requests.post(
    "https://your-app-name.onrender.com/chat",
    json={"message": "What are the current alerts?"}
)
print(response.json())
```

## Example Usage

### Simple Chat
```python
import requests

url = "https://your-app-name.onrender.com/chat"
data = {
    "message": "Show me all critical patients in the ICU"
}

response = requests.post(url, json=data)
result = response.json()
print(result["response"])
```

### With Conversation History
```python
import requests

url = "https://your-app-name.onrender.com/chat"
conversation = []

# First message
data = {
    "message": "Show me all patients",
    "conversation_history": conversation
}
response = requests.post(url, json=data)
result = response.json()
conversation = result["conversation_history"]

# Follow-up message
data = {
    "message": "Which ones are in critical condition?",
    "conversation_history": conversation
}
response = requests.post(url, json=data)
print(response.json()["response"])
```

## Troubleshooting

### Common Issues

1. **404 Error**: Check that your OpenRouter API key is correct
2. **500 Error**: Check the logs in Render dashboard
3. **Timeout**: Hospital backend might be slow, increase timeout if needed

### Checking Logs
In Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Check for any error messages

### Environment Variables
Make sure `OPENROUTER_API_KEY` is set in Render environment variables.

## Customization

### Adding New Endpoints
1. Add new route in `app.py`
2. Test locally
3. Deploy to Render

### Changing AI Model
Update the model in the `SmartHospitalAgent` class:
```python
self.model = "your-preferred-model"
```

### Adding Authentication
Add authentication middleware to protect your API endpoints.

## Support

If you encounter issues:
1. Check the logs in Render dashboard
2. Verify your OpenRouter API key
3. Test the hospital backend endpoints directly
4. Use the provided test script to diagnose issues