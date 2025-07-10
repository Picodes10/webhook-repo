# GitHub Webhook Monitor

A Flask application that receives GitHub webhooks and displays repository activity in real-time.

## Features

- 📡 Receives GitHub webhooks for push, pull request, and merge events
- 🗄️ Stores webhook data in MongoDB
- 🔄 Real-time UI updates every 15 seconds
- 🎨 Clean, responsive web interface
- 🔐 Webhook signature verification (optional)

## Project Structure

```
webhook-repo/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main UI template
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## Setup Instructions

### 1. Clone and Setup the Webhook Repository

```bash
git clone <your-webhook-repo-url>
cd webhook-repo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB locally
# Start MongoDB service
mongod --dbpath /path/to/your/db
```

**Option B: MongoDB Atlas (Cloud)**
1. Create a free account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a cluster
3. Get your connection string
4. Replace the connection string in your `.env` file

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/

# GitHub Webhook Secret (optional but recommended)
WEBHOOK_SECRET=your-secret-webhook-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Setting Up GitHub Webhooks

### 1. Create Action Repository

Create a new repository called `action-repo` (this will be your test repository).

### 2. Configure Webhook in GitHub

1. Go to your `action-repo` repository
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL**: `http://your-domain.com/webhook` (use ngrok for local testing)
   - **Content type**: `application/json`
   - **Secret**: Use the same secret as in your `.env` file
   - **Events**: Select "Push", "Pull requests", and "Releases"

### 3. Local Testing with ngrok

For local development, use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# Expose your local Flask app
ngrok http 5000

# Use the ngrok URL for GitHub webhook
# Example: https://abc123.ngrok.io/webhook
```

## Testing the Application

### 1. Test Webhook Endpoint

You can test the webhook endpoint manually:

```bash
curl -X POST http://localhost:5000/test-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "author": "testuser",
    "action": "push",
    "from_branch": "dev",
    "to_branch": "main"
  }'
```

### 2. Test with Real GitHub Events

1. Make a push to your `action-repo`
2. Create a pull request
3. Merge a pull request
4. Check the UI at `http://localhost:5000`

## MongoDB Schema

The application stores webhook data with the following schema:

```javascript
{
  "_id": ObjectId,
  "id": String,
  "author": String,
  "action": String,        // "push", "pull_request", "merge"
  "from_branch": String,   // Source branch (for PR/merge)
  "to_branch": String,     // Target branch
  "timestamp": String,     // ISO timestamp
  "request_id": String,    // Unique request identifier
  "created_at": Date       // Document creation time
}
```

## API Endpoints

- `GET /` - Main UI interface
- `POST /webhook` - GitHub webhook receiver
- `GET /api/actions` - JSON API for recent actions
- `POST /test-webhook` - Test endpoint for manual testing

## Deployment

### Heroku Deployment

1. Create a new Heroku app
2. Add MongoDB Atlas add-on or use external MongoDB
3. Set environment variables in Heroku
4. Deploy using Git

```bash
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Expected Output Formats

The UI displays events in the following formats:

- **Push**: `"Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC`
- **Pull Request**: `"Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC`
- **Merge**: `"Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC`

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check if the webhook URL is accessible
   - Verify the GitHub webhook configuration
   - Check ngrok is running (for local testing)

2. **MongoDB connection errors**
   - Ensure MongoDB is running
   - Check connection string in `.env`
   - Verify network access for MongoDB Atlas

3. **Signature verification fails**
   - Ensure the webhook secret matches in GitHub and `.env`
   - Comment out signature verification for testing

### Debug Mode

Enable debug logging by setting `FLASK_DEBUG=True` in your environment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes as part of a technical assessment.
