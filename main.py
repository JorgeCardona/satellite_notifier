import os
import requests
import smtplib
from email.mime.text import MIMEText

# Datos de la ubicación (reemplazar con tu latitud y longitud) https://www.google.com/maps
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
# https://www.advancedconverter.com/es/herramientas-de-mapa/encontrar-altitud-desde-coordenadas
ALTITUDE = os.getenv('ALTITUDE')

# Datos del satélite (ejemplo con el ID de la Estación Espacial Internacional)
SATELLITE_ID = os.getenv('SATELLITE_ID')

# SATELLITE API Key
SATELLITE_API_KEY = os.getenv('SATELLITE_API_KEY')

# URL de la API
N2YO_URL = f"https://api.n2yo.com/rest/v1/satellite/positions/{SATELLITE_ID}/{LATITUDE}/{LONGITUDE}/{ALTITUDE}/1/&apiKey={SATELLITE_API_KEY}"

# Configuración del correo electrónico
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

def send_email(message):
    msg = MIMEText(message)
    msg['Subject'] = '¡El satélite está pasando por tu zona!'
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

def check_satellite():
    response = requests.get(N2YO_URL)
    data = response.json()
    print('api response',data)
    positions = data.get('positions', [])

    # Verifica si el satélite está sobre tu ubicación
    for position in positions:
        print('position',position)
        SATELITTE_NAME = info['satname']
        ALTITUDE_RESPONSE = position['sataltitude']

        print('SATELITTE_NAME',SATELITTE_NAME)
        print('SATELLITE_ID',SATELLITE_ID)
        print('ALTITUDE_RESPONSE',ALTITUDE_RESPONSE)
        
        if 'sataltitude' in position and position['sataltitude'] > 0:
            send_email(f"¡El satélite {SATELLITE_ID} - {SATELITTE_NAME} está sobre tu zona!")
            print('ENAIL SENT SUCCESDFULLY')
            break

# Ejecutar la verificación del satélite
check_satellite()
