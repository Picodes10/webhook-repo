#!/usr/bin/env python3
"""
Quick setup script for GitHub Webhook Monitor
"""
import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment."""
    if os.path.exists("venv"):
        print("📁 Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install required packages."""
    if platform.system() == "Windows":
        pip_command = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_command = "venv/bin/pip install -r requirements.txt"
    
    return run_command(pip_command, "Installing dependencies")

def setup_environment_file():
    """Create .env file from template."""
    if os.path.exists(".env"):
        print("📄 .env file already exists")
        return True
    
    if os.path.exists(".env.example"):
        try:
            with open(".env.example", "r") as src:
                content = src.read()
            
            with open(".env", "w") as dst:
                dst.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please update the values in .env file before running the app")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ .env.example file not found")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["templates", "logs", "static"]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"📁 Created {directory} directory")
            except Exception as e:
                print(f"❌ Error creating {directory}: {e}")
                return False
    
    return True

def check_mongodb():
    """Check if MongoDB is available."""
    try:
        import pymongo
        # Try to connect to local MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB is running locally")
        return True
    except Exception:
        print("⚠️  MongoDB is not running locally")
        print("   Options:")
        print("   1. Install and start MongoDB locally")
        print("   2. Use MongoDB Atlas (cloud)")
        print("   3. Use Docker: docker run -d -p 27017:27017 mongo:5.0")
        return False

def display_next_steps():
    """Display instructions for next steps."""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Update your .env file with correct values")
    print("2. Make sure MongoDB is running")
    print("3. Start the application:")
    
    if platform.system() == "Windows":
        print("   venv\\Scripts\\python app.py")
    else:
        print("   source venv/bin/activate")
        print("   python app.py")
    
    print("\n4. Set up GitHub webhook:")
    print("   - Create a repository called 'action-repo'")
    print("   - Go to Settings → Webhooks")
    print("   - Add webhook URL: http://your-domain.com/webhook")
    print("   - For local testing, use ngrok: ngrok http 5000")
    
    print("\n5. Test the setup:")
    print("   - Visit: http://localhost:5000")
    print("   - Run: python test_webhook.py")
    
    print("\n📚 Documentation:")
    print("   - README.md contains detailed instructions")
    print("   - Check the GitHub repository for examples")

def main():
    """Main setup function."""
    print("🚀 GitHub Webhook Monitor Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        (create_directories, "Creating directories"),
        (setup_virtual_environment, "Setting up virtual environment"),
        (install_dependencies, "Installing dependencies"),
        (setup_environment_file, "Setting up environment file"),
        (check_mongodb, "Checking MongoDB availability")
    ]
    
    failed_steps = []
    for step_func, step_name in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n⚠️  Some steps failed: {', '.join(failed_steps)}")
        print("Please resolve these issues before proceeding.")
    else:
        display_next_steps()

if __name__ == "__main__":
    main()
    