import requests
import json
import time
from datetime import datetime

# Test webhook endpoint
WEBHOOK_URL = "http://localhost:5000/test-webhook"
API_URL = "http://localhost:5000/api/actions"

def test_webhook_events():
    """Test different types of webhook events."""
    
    # Test data for different event types
    test_events = [
        {
            "author": "john_doe",
            "action": "push",
            "from_branch": None,
            "to_branch": "main"
        },
        {
            "author": "jane_smith",
            "action": "pull_request",
            "from_branch": "feature/new-feature",
            "to_branch": "develop"
        },
        {
            "author": "bob_wilson",
            "action": "merge",
            "from_branch": "hotfix/critical-bug",
            "to_branch": "main"
        },
        {
            "author": "alice_johnson",
            "action": "push",
            "from_branch": None,
            "to_branch": "staging"
        }
    ]
    
    print("🧪 Testing webhook events...")
    print("=" * 50)
    
    for i, event in enumerate(test_events, 1):
        print(f"\n📡 Sending test event {i}: {event['action']} by {event['author']}")
        
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=event,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Event {i} sent successfully")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Event {i} failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Event {i} failed with error: {e}")
        
        # Wait a bit between events
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🔍 Testing API endpoint...")
    
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            actions = data.get('actions', [])
            print(f"✅ API endpoint working. Retrieved {len(actions)} actions.")
            
            if actions:
                print("\n📋 Recent actions:")
                for action in actions[:5]:  # Show last 5 actions
                    print(f"   • {action.get('display_text', 'No display text')}")
            else:
                print("   No actions found in database.")
        else:
            print(f"❌ API endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API endpoint failed with error: {e}")

def check_server_health():
    """Check if the Flask server is running."""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running and accessible")
            return True
        else:
            print(f"⚠️  Flask server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask server is not accessible: {e}")
        return False

def simulate_github_webhook():
    """Simulate actual GitHub webhook payload."""
    github_push_payload = {
        "ref": "refs/heads/main",
        "before": "abc123",
        "after": "def456",
        "pusher": {
            "name": "github_user",
            "email": "user@example.com"
        },
        "repository": {
            "name": "test-repo",
            "full_name": "user/test-repo"
        },
        "commits": [
            {
                "id": "def456",
                "message": "Fix critical bug",
                "author": {
                    "name": "github_user",
                    "email": "user@example.com"
                }
            }
        ]
    }
    
    print("\n🚀 Simulating real GitHub webhook...")
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json=github_push_payload,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "push"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ GitHub webhook simulation successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ GitHub webhook simulation failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub webhook simulation failed: {e}")

if __name__ == "__main__":
    print("🔧 GitHub Webhook Test Suite")
    print("=" * 50)
    
    # Check server health first
    if not check_server_health():
        print("\n💡 Make sure your Flask server is running:")
        print("   python app.py")
        exit(1)
    
    print("\n⏱️  Starting tests in 3 seconds...")
    time.sleep(3)
    
    # Run tests
    test_webhook_events()
    simulate_github_webhook()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("📱 Check the UI at: http://localhost:5000")
    print("🔗 API endpoint: http://localhost:5000/api/actions")
    