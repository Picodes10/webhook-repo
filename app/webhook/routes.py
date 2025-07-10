from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["events"]

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')
CORS(webhook)  # Enable CORS for the frontend

@webhook.route('/receiver', methods=['POST'])
def receiver():
    if not request.is_json:
        return jsonify({"error": "Content type must be application/json"}), 400

    data = request.get_json()
    event = request.headers.get('X-GitHub-Event')
    timestamp = datetime.utcnow().isoformat()

    if event == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = data['head_commit']['timestamp']

        event_data = {
            "type": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "message": f"{author} pushed to {to_branch} on {timestamp}",
            "created_at": datetime.utcnow()
        }
        collection.insert_one(event_data)

    elif event == 'pull_request':
        action = data['action']
        pr_data = data['pull_request']
        author = pr_data['user']['login']
        from_branch = pr_data['head']['ref']
        to_branch = pr_data['base']['ref']

        if action == 'opened':
            timestamp = pr_data['created_at']
            event_data = {
                "type": "pull_request",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp,
                "message": f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}",
                "created_at": datetime.utcnow()
            }
            collection.insert_one(event_data)

        elif action == 'closed' and pr_data['merged']:
            timestamp = pr_data['merged_at']
            event_data = {
                "type": "merge",
                "author": author,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp,
                "message": f"{author} merged branch {from_branch} to {to_branch} on {timestamp}",
                "created_at": datetime.utcnow()
            }
            collection.insert_one(event_data)

    return jsonify({"status": "success"}), 200

@webhook.route('/events', methods=['GET'])
def get_events():
    # Add CORS headers
    events = list(collection.find(
        {},
        {'_id': 0}
    ).sort('created_at', -1).limit(50))

    return jsonify({"events": events}), 200
