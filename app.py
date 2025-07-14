# app.py

from flask import Flask, render_template
import csv
import os

# Initialize the Flask app
app = Flask(__name__)

# --- NEW: Route for the Landing Page ---
@app.route('/')
def landing_page():
    """This function serves the new, beautiful landing page."""
    return render_template('landing_page.html')


# --- UPDATED: Route for the Dashboard ---
@app.route('/dashboard')
def dashboard():
    """This function serves the activity log dashboard."""
    
    log_data = []
    header = []
    
    # Path to the CSV file
    csv_file_path = 'seen_articles.csv'
    
    # Check if the file exists before trying to read it
    if os.path.exists(csv_file_path):
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader) # Read the header row
                for row in reader:
                    log_data.append(row)
        except StopIteration:
            # This handles the case where the file exists but is empty
            print("Log file is empty.")
        except Exception as e:
            print(f"Error reading log file: {e}")
    else:
        print("Log file not found. It will be created when the agent runs.")
    
    # Reverse the data so the newest entries are at the top
    log_data.reverse()

    # Render the dashboard template and pass the data to it
    # Make sure your HTML file is named 'dashboard.html'
    return render_template('dashboard.html', logs=log_data, headers=header)


# This allows you to run the app directly
if __name__ == '__main__':
    app.run(debug=True)