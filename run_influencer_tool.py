#!/usr/bin/env python3
"""
Instagram Influencer Discovery Tool - Demo Runner

This script demonstrates how to run the influencer discovery tool.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'plotly', 'pandas', 'requests', 
        'beautifulsoup4', 'fastapi', 'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        install_cmd = [
            sys.executable, "-m", "pip", "install", "--break-system-packages"
        ] + missing_packages
        
        try:
            subprocess.run(install_cmd, check=True)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually.")
            return False
    
    return True

def run_streamlit_app():
    """Run the Streamlit application"""
    print("🚀 Starting Instagram Influencer Discovery Tool...")
    print("📱 This will open in your web browser automatically")
    print("⏱️  Starting up (may take a few seconds)...")
    
    # Check if the app file exists
    app_file = "influencer_discovery_app.py"
    if not os.path.exists(app_file):
        print(f"❌ App file {app_file} not found!")
        return False
    
    try:
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", app_file, "--server.port=8501"]
        
        print("🌐 Starting web server...")
        print("📍 URL: http://localhost:8501")
        print("⚠️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Try to open browser
        try:
            webbrowser.open("http://localhost:8501")
            print("🌐 Opened in web browser!")
        except:
            print("💡 Manual step: Open http://localhost:8501 in your browser")
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def run_backend_api():
    """Run the FastAPI backend separately"""
    print("🔧 Starting FastAPI backend...")
    
    try:
        # Change to backend directory
        backend_dir = "app/backend"
        if not os.path.exists(backend_dir):
            print(f"❌ Backend directory {backend_dir} not found!")
            return False
        
        # Run uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--port", "8000", "--host", "0.0.0.0"
        ]
        
        print("🌐 API Server starting on http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("⚠️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Change directory and run
        old_cwd = os.getcwd()
        os.chdir(backend_dir)
        
        try:
            process = subprocess.run(cmd)
        finally:
            os.chdir(old_cwd)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping API server...")
        return True
    except Exception as e:
        print(f"❌ Failed to start API: {e}")
        return False
    
    return True

def show_demo_instructions():
    """Show instructions for using the demo"""
    print("""
🎯 DEMO INSTRUCTIONS
===================

The Instagram Influencer Discovery Tool is now running!

🔍 How to Search for Influencers:
1. Use the sidebar filters to set your criteria
2. Enter keywords like "fashion", "beauty", "fitness"
3. Set follower ranges (e.g., 1K - 100K)
4. Choose engagement rate thresholds
5. Click "🚀 Search Influencers"

⚡ Quick Start Options:
- Click "🔥 Trending" for viral influencers
- Click "💎 Premium" for verified accounts

📊 Features to Try:
- View analytics dashboard with charts
- Select multiple influencers for comparison
- Export data to CSV for further analysis
- Explore individual influencer profiles

💡 Tips:
- Try different category combinations
- Experiment with follower ranges
- Look for high engagement rates (3%+)
- Use location filters for local campaigns

🆘 Need Help?
- Check the sidebar for search tips
- Review the README for detailed instructions
- All data shown is simulated for demonstration

Happy influencer hunting! 🎉
""")

def main():
    """Main function to run the demo"""
    print("=" * 60)
    print("📱 INSTAGRAM INFLUENCER DISCOVERY TOOL")
    print("=" * 60)
    print("🎯 Purpose: Find the perfect influencers for your ecommerce brand")
    print("🔧 Built with: Streamlit, FastAPI, Python")
    print("=" * 60)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("❌ Dependency check failed. Exiting.")
        return
    
    print("✅ All dependencies are ready!")
    
    # Show menu
    print("\n🚀 Choose how to run the tool:")
    print("1. 📱 Full Application (Streamlit) - Recommended")
    print("2. 🔧 Backend API Only (FastAPI)")
    print("3. 📖 Show Instructions Only")
    print("4. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n" + "="*50)
            show_demo_instructions()
            print("="*50)
            run_streamlit_app()
            break
        elif choice == "2":
            print("\n" + "="*50)
            run_backend_api()
            break
        elif choice == "3":
            show_demo_instructions()
            break
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()