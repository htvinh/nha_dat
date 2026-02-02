import os
import subprocess

def main():
    """
    Runs the Streamlit application.
    """
    app_path = os.path.join("dashboard", "app.py")
    command = ["streamlit", "run", app_path]
    
    print("Starting the Streamlit application...")
    print(f"You can view your app in your browser.")
    
    subprocess.run(command)

if __name__ == "__main__":
    main()
