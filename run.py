import subprocess
import sys
import os

if __name__ == "__main__":
    print("⚡ Starting Ripple OS via Streamlit...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "ui/app.py"])