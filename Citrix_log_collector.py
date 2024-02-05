import os
import sqlite3
import datetime
from datetime import datetime, timedelta, timezone
import glob
from time import sleep


def parse_chrome_history(profile_path, output_file, max_retries=2, retry_delay=1):
    
        
    # Path to the Chrome history database
    history_db_path = os.path.join(profile_path, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    print(history_db_path)
    if not os.path.exists(history_db_path):
        return

    retry_count = 0
    while retry_count < max_retries:
        try:
            # Connect to the database
            conn = sqlite3.connect(history_db_path)
            cursor = conn.cursor()

            # Query to select browsing history data
            query = "SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC"

            # Execute the query
            cursor.execute(query)

            # Fetch all rows
            rows = cursor.fetchall()
            

            # Print or format the data
            with open(output_file, "a", encoding="utf-8") as file:
                for row in rows:
                    url = row[0]
                    title = row[1]
                    visit_time = row[2]
                    # Convert timestamp to human-readable date
                    visit_time += 12600000000
                    visit_time_formatted = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                    file.write(f"User: {os.path.basename(profile_path)} | Browser: Chrome\nURL: {url}\nTitle: {title}\nVisit Time: {visit_time_formatted}\n\n")

            # Close the database connection
            conn.close()

            # If no exception occurred, break out of the retry loop
            break
        except sqlite3.OperationalError as e:
            print(f"Error accessing Chrome history database: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")

def parse_firefox_history(profile_path, output_file):
    # Path to the Firefox history database (places.sqlite)
    history_db_path = os.path.join(profile_path, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles", "*", "places.sqlite")
    print(history_db_path)
    profiles = glob.glob(history_db_path)

    for profile in profiles:
        # Connect to the database
        conn = sqlite3.connect(profile)
        cursor = conn.cursor()

        # Query to select browsing history data
        query = "SELECT url, title, visit_date/1000000 FROM moz_places JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id ORDER BY visit_date DESC"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Print or format the data
        with open(output_file, "a",encoding="utf-8") as file:
            for row in rows:
                url = row[0]
                title = row[1]
                visit_time = row[2]
                # Convert timestamp to human-readable date
                visit_time_formatted = datetime.fromtimestamp(visit_time).strftime('%Y-%m-%d %H:%M:%S')
                file.write(f"User: {os.path.basename(profile_path)} | Browser: Firefox\nURL: {url}\nTitle: {title}\nVisit Time: {visit_time_formatted}\n\n")

        # Close the database connection
        conn.close()




# Path to user profiles directory
profiles_dir = os.path.join(os.environ['SYSTEMDRIVE'], r'\Users')
# Get the current user's username
current_user = os.getlogin()

# Construct the path to the Desktop directory within the log folder
log_folder_path = os.path.join(os.environ['SYSTEMDRIVE'], r'\Users', current_user, "Desktop","History-LOG")

# Create the directory if it doesn't exist
if not os.path.exists(log_folder_path):
    os.makedirs(log_folder_path)

# Get the current date as a string
output_dir = datetime.now().strftime("%Y-%m-%d")

# Final directory path
final_directory_path = os.path.join(log_folder_path, output_dir)
print("FILE IS OUTPUT TO : "+ final_directory_path+"\n\n")

if not os.path.exists(final_directory_path):
    os.makedirs(final_directory_path)
# Iterate through each user profile directory
for user_dir in os.listdir(profiles_dir):
    profile_path = os.path.join(profiles_dir, user_dir)
    if os.path.isdir(profile_path):
        try:
            user_log_file_path = os.path.join(final_directory_path, f"{user_dir}_history.txt")
            parse_chrome_history(profile_path, user_log_file_path)
            parse_firefox_history(profile_path, user_log_file_path)
        except Exception as e:
            print("error: " + str(e))
