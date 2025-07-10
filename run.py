from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import json
import hashlib
import hmac
import os
from bson import ObjectId
from bson.json_util import dumps

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'github_webhooks'
COLLECTION_NAME = 'actions'

# GitHub webhook secret (set this in your environment variables)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def verify_signature(payload_body, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256 signature."""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

def parse_timestamp(timestamp_str):
    """Parse GitHub timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%d %B %Y - %I:%M %p UTC')
    except:
        return datetime.now().strftime('%d %B %Y - %I:%M %p UTC')

@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events."""
    try:
        # Get the signature from headers
        signature_header = request.headers.get('X-Hub-Signature-256')
        
        # Parse the payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        # Extract common data
        action_type = None
        author = None
        from_branch = None
        to_branch = None
        timestamp = datetime.now().isoformat()
        
        # Determine action type and extract relevant data
        if 'push' in request.headers.get('X-GitHub-Event', ''):
            action_type = 'push'
            author = payload.get('pusher', {}).get('name', 'Unknown')
            ref = payload.get('ref', '')
            to_branch = ref.split('/')[-1] if ref else 'Unknown'
            
        elif 'pull_request' in request.headers.get('X-GitHub-Event', ''):
            action_type = 'pull_request'
            pr_data = payload.get('pull_request', {})
            author = pr_data.get('user', {}).get('login', 'Unknown')
            from_branch = pr_data.get('head', {}).get('ref', 'Unknown')
            to_branch = pr_data.get('base', {}).get('ref', 'Unknown')
            
            # Check if it's a merge (closed + merged)
            if (payload.get('action') == 'closed' and 
                pr_data.get('merged') == True):
                action_type = 'merge'
        
        # Create document for MongoDB
        document = {
            'id': str(ObjectId()),
            'author': author,
            'action': action_type,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'request_id': payload.get('zen', str(ObjectId())),
            'created_at': datetime.now()
        }
        
        # Insert into MongoDB
        result = collection.insert_one(document)
        
        print(f"Webhook received: {action_type} by {author}")
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook processed successfully',
            'document_id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/actions', methods=['GET'])
def get_actions():
    """API endpoint to get recent actions for the UI."""
    try:
        # Get the latest 50 actions, sorted by creation time
        actions = list(collection.find().sort('created_at', -1).limit(50))
        
        # Format the actions for display
        formatted_actions = []
        for action in actions:
            formatted_action = {
                'id': str(action['_id']),
                'author': action.get('author', 'Unknown'),
                'action': action.get('action', 'unknown'),
                'from_branch': action.get('from_branch'),
                'to_branch': action.get('to_branch'),
                'timestamp': action.get('timestamp'),
                'display_text': format_action_display(action)
            }
            formatted_actions.append(formatted_action)
        
        return jsonify({'actions': formatted_actions}), 200
        
    except Exception as e:
        print(f"Error fetching actions: {str(e)}")
        return jsonify({'error': 'Failed to fetch actions'}), 500

def format_action_display(action):
    """Format action data for display."""
    author = action.get('author', 'Unknown')
    action_type = action.get('action', 'unknown')
    from_branch = action.get('from_branch')
    to_branch = action.get('to_branch')
    timestamp = action.get('timestamp', '')
    
    # Parse timestamp for display
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        formatted_time = dt.strftime('%d %B %Y - %I:%M %p UTC')
    except:
        formatted_time = 'Unknown time'
    
    if action_type == 'push':
        return f'"{author}" pushed to "{to_branch}" on {formatted_time}'
    elif action_type == 'pull_request':
        return f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {formatted_time}'
    elif action_type == 'merge':
        return f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {formatted_time}'
    else:
        return f'"{author}" performed {action_type} on {formatted_time}'

# Test endpoint to simulate webhook events
@app.route('/test-webhook', methods=['POST'])
def test_webhook():
    """Test endpoint to simulate webhook events."""
    test_data = request.get_json()
    
    document = {
        'id': str(ObjectId()),
        'author': test_data.get('author', 'TestUser'),
        'action': test_data.get('action', 'push'),
        'from_branch': test_data.get('from_branch', 'dev'),
        'to_branch': test_data.get('to_branch', 'main'),
        'timestamp': datetime.now().isoformat(),
        'request_id': str(ObjectId()),
        'created_at': datetime.now()
    }
    
    result = collection.insert_one(document)
    return jsonify({'status': 'Test webhook processed', 'id': str(result.inserted_id)})

if __name__ == '__main__':
    # Create indexes for better performance
    collection.create_index([('created_at', -1)])
    collection.create_index([('action', 1)])
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    