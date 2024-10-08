import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import pytz
import pandas as pd

# Retrieve location data from environment variables,  https://www.google.com/maps
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
# https://www.advancedconverter.com/es/herramientas-de-mapa/encontrar-altitud-desde-coordenadas
ALTITUDE = os.getenv('ALTITUDE')

# Retrieve satellite data from environment variables
SATELLITE_ID = os.getenv('SATELLITE_ID')
SATELLITE_API_KEY = os.getenv('SATELLITE_API_KEY')

# Construct the satellite API URL
def construct_url(satellite_id, latitude, longitude, altitude, api_key):
    return f"https://api.n2yo.com/rest/v1/satellite/positions/{satellite_id}/{latitude}/{longitude}/{altitude}/1/&apiKey={api_key}"

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_USER = os.getenv('EMAIL_USER')
# https://myaccount.google.com/apppasswords
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
# Directory and file for store records
LOG_DIRECTORY = os.getenv('LOG_DIRECTORY')
LOG_FILE = os.getenv('LOG_FILE')

def send_email(message):
    """
    Sends an email with the specified message.
    
    Args:
    - message (str): The content of the email.
    """
    msg = MIMEText(message)
    msg['Subject'] = 'Satellite is passing over your area!'
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

def get_look_direction(azimuth):
    """
    Returns the cardinal or intercardinal direction based on the azimuth angle.

    Args:
        azimuth (float): The azimuth angle in degrees (0 to 359).

    Returns:
        str: The direction to look, such as "North", "Northeast", "East", etc.
             If the azimuth is not within 0 to 359 degrees, returns "Invalid azimuth value".
    """
    if azimuth >= 0 and azimuth < 45:
        return "North"
    elif azimuth >= 45 and azimuth < 90:
        return "Northeast"
    elif azimuth >= 90 and azimuth < 135:
        return "East"
    elif azimuth >= 135 and azimuth < 180:
        return "Southeast"
    elif azimuth >= 180 and azimuth < 225:
        return "South"
    elif azimuth >= 225 and azimuth < 270:
        return "Southwest"
    elif azimuth >= 270 and azimuth < 315:
        return "West"
    elif azimuth >= 315 and azimuth < 360:
        return "Northwest"
    else:
        return "Invalid azimuth value"


def convert_utc_to_local(utc_timestamp):
    # Convert UTC timestamp to datetime
    utc_time = datetime.utcfromtimestamp(utc_timestamp)
    
    # Define UTC-5 timezone
    local_tz = pytz.timezone('America/Bogota')  # Bogota is UTC-5
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def check_satellite(url_satellite):
    """
    Checks if the satellite is visible over the specified location by making a request to the satellite API.
    If the satellite is visible, sends an email notification.

    Args:
        url_satellite (str): The URL to fetch satellite position data from the API.

    Returns:
        None
    """
    response = requests.get(url_satellite)
    data = response.json()
    print('API response:', data)
    
    positions = data.get('positions', [])
    info = data.get('info', {})

    df_positions = pd.DataFrame(positions)
    df_info = pd.DataFrame([info])

    print('Dataframe Position:')
    print(df_positions)
    print()
    print('Dataframe Info:')
    print(df_info)
    print()

    # Retrieve satellite name from info
    satellite_name = info.get('satname', 'Unknown')
    satellite_id = info.get('satid', 'Unknown')

    # Check each position to see if the satellite is over the location
    for position in positions:
        print('Position:', position)
        altitude_response = position.get('sataltitude', 0)
        elevation_response = position.get('elevation', 0)
        azimuth_response = position.get('azimuth', 0)
        ra = position.get('ra', 0)
        dec = position.get('dec', 0)
        timestamp = position.get('timestamp', 0)
        eclipsed = position.get('eclipsed', False)

        direction = get_look_direction(int(azimuth_response))
        # Convert timestamp to local time
        local_time = convert_utc_to_local(timestamp)

        print('Satellite Name:', satellite_name)
        print('Altitude Response:', altitude_response)
        print('Altitude Response:', altitude_response)
        print('Satellite Elevation:', elevation_response)
        print(f"Direction to look: {direction} (Azimuth: {azimuth_response}°)")
        print(f"Right Ascension: {ra}°")
        print(f"Declination: {dec}°")    
        print(f"Timestamp: {timestamp}")
        print(f"Local Time: {local_time}")
        print(f"Eclipsed: {'Yes' if eclipsed else 'No'}")
        
        # Check if the satellite is visible
        if elevation_response > 0 and not eclipsed:
            message = f"Satellite ID {satellite_id} with name {satellite_name} is over your area at {azimuth_response}° azimuth. The direction to look is: {direction}. Visible at {local_time} UTC-5!"
            return message
        
        else:
            print(f"Satellite {satellite_name} is not over your area. Altitude: {altitude_response} meters, Direction: {direction}, Azimuth: {azimuth_response}°, Eclipsed: {'Yes' if eclipsed else 'No'}.")

            return None

def save_message_to_file(body_message, log_directory, log_file):
    """
    Saves the body_message to a file with a timestamp in the specified directory.
    
    Args:
    - body_message (str): The message to save.
    - log_directory (str): The directory where the log file will be saved.
    - log_file (str): The name of the log file.
    """
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create the directory if it doesn't exist
    try:
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
    except Exception as e:
        print(f'Error creating directory: {e}')
        return  # Exit the function if we can't create the directory
    
    # Full path to the file
    file_path = os.path.join(log_directory, log_file)

    try:
        # Open the file in append mode
        with open(file_path, mode='a', encoding='utf-8') as file:
            # Write the timestamp and body_message to the file
            file.write(f"{timestamp} - {body_message}\n")
        
        print(f'Message saved to {file_path}')
    
    except Exception as e:
        print(f'Error saving message to file: {e}')
    
# validate the satellite list url URL and run the check
def check_multiple_satellites():
    """
    Retrieves the list of satellite IDs from the environment variable and performs a satellite check for each ID.
    """
    satellite_ids = os.getenv('SATELLITE_ID', '').split(',')

    visible_satellites = list()

    for satellite_id in satellite_ids:
        satellite_id = satellite_id.strip()  # Remove any leading/trailing whitespace
        if satellite_id:  # Check if the satellite_id is not empty
            print('Satellite ID:', satellite_id)
            # Construct the satellite URL for the current ID and run the check
            url_satellite = construct_url(satellite_id, LATITUDE, LONGITUDE, ALTITUDE, SATELLITE_API_KEY)

            satelite = check_satellite(url_satellite)
            if satelite:
                visible_satellites.append(satelite)
    
    if visible_satellites:
        print('List of Visible Satellites:')
        print(visible_satellites)

        body_message = '\n'.join(visible_satellites)
        send_email(body_message)
        print('Email sent successfully.')
        save_message_to_file(body_message, log_directory=LOG_DIRECTORY, log_file=LOG_FILE)

# Call the new function to process the list of satellite IDs
check_multiple_satellites()
