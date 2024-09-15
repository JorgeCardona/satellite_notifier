import os
import requests
import smtplib
from email.mime.text import MIMEText

# Datos de la ubicación (reemplazar con tu latitud y longitud)
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')
ALTITUDE = os.getenv('ALTITUDE')

# Datos del satélite (ejemplo con el ID de la Estación Espacial Internacional)
SATELITE_ID = os.getenv('SATELITE_ID')

# N2YO API Key
API_KEY = os.getenv('N2YO_API_KEY')

# URL de la API
N2YO_URL = f"https://api.n2yo.com/rest/v1/satellite/positions/{SATELITE_ID}/{LATITUDE}/{LONGITUDE}/{ALTITUDE}/1/&apiKey={API_KEY}"

# Configuración del correo electrónico
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
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
    positions = data['positions']

    # Verifica si el satélite está sobre tu ubicación
    for position in positions:
        if position['satalt'] > 0:  # Si la altitud es mayor a 0, es visible
            send_email(f"¡El satélite {SATELITE_ID} está sobre tu zona!")
            break

# Ejecutar la verificación del satélite
check_satellite()
