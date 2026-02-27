import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class CalendarSender:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # Intentamos cargar las credenciales
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=self.SCOPES
            )
            self.service = build('calendar', 'v3', credentials=self.credentials)
            # Usamos el correo que te funcionaba antes
            self.calendar_id = os.getenv("CALENDAR_ID", "blessedbarbershopenv@gmail.com")
            self.timezone = ZoneInfo("America/Bogota")
        except Exception as e:
            print(f"❌ Error inicializando Calendario: {e}")
            self.service = None

    def crear_evento(self, correo, cliente, fecha, hora, profesional):
        if not self.service:
            print("⚠️ Servicio de calendario no disponible")
            return

        try:
            inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            inicio = inicio.replace(tzinfo=self.timezone)
            fin = inicio + timedelta(hours=1)

            evento = {
                'summary': f'Corte - {cliente}',
                'description': f'Barbero: {profesional}\nCliente: {correo}',
                'start': {
                    'dateTime': inicio.isoformat(),
                    'timeZone': 'America/Bogota',
                },
                'end': {
                    'dateTime': fin.isoformat(),
                    'timeZone': 'America/Bogota',
                }
            }

            self.service.events().insert(
                calendarId=self.calendar_id,
                body=evento
            ).execute()
            print("✅ Evento de calendario creado")
        except Exception as e:
            print(f"❌ Error al crear evento: {e}")
