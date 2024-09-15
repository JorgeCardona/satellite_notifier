import os
import requests
import smtplib
from email.mime.text import MIMEText


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

def check_satellite(url_satellite):
    """
    Checks if the satellite is over the specified location and sends an email if it is.
    
    Args:
    - url_satellite (str): The URL to fetch satellite data.
    """
    response = requests.get(url_satellite)
    data = response.json()
    print('API response:', data)
    
    positions = data.get('positions', [])
    info = data.get('info', {})

    # Retrieve satellite name from info
    satellite_name = info.get('satname', 'Unknown')

    # Check each position to see if the satellite is over the location
    for position in positions:
        print('Position:', position)
        altitude_response = position.get('sataltitude', 0)
        
        print('Satellite Name:', satellite_name)
        print('Satellite ID:', SATELLITE_ID)
        print('Altitude Response:', altitude_response)
        
        if altitude_response > int(ALTITUDE):
            send_email(f"Satellite {satellite_name} is over your area!")
            print('Email sent successfully.')
            break  # Exit loop after sending the email

        else:
            print(f"Satellite {satellite_name} is far from your area with an altitude of {altitude_response}.")

# Construct the satellite URL and run the check
url_satellite = construct_url(SATELLITE_ID, LATITUDE, LONGITUDE, ALTITUDE, SATELLITE_API_KEY)
check_satellite(url_satellite)
