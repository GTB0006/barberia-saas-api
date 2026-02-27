import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timedelta

class EmailSender:
    def __init__(self):
        # Usamos las variables de entorno de Render
        self.email = os.getenv("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.getenv("EMAIL_PASSWORD", "dkkgsqhzizbyifyi").strip()

    def generar_ics(self, nombre, fecha, hora, profesional):
        try:
            inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            fin = inicio + timedelta(hours=1)

            inicio_fmt = inicio.strftime("%Y%m%dT%H%M%S")
            fin_fmt = fin.strftime("%Y%m%dT%H%M%S")

            return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//BlessedBarbershop//Reserva//ES
BEGIN:VEVENT
UID:{inicio_fmt}@blessedbarbershop
DTSTAMP:{inicio_fmt}
DTSTART:{inicio_fmt}
DTEND:{fin_fmt}
SUMMARY:Cita Barbería 💈 - {nombre}
DESCRIPTION:Barbero: {profesional}
LOCATION:Calle 38 sur 34-22 Envigado
END:VEVENT
END:VCALENDAR
"""
        except Exception as e:
            print(f"Error generando ICS: {e}")
            return ""

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Confirmación de Reserva - {profesional}"
            msg["From"] = self.email
            msg["To"] = correo_cliente

            msg.set_content(f"""
Hola {nombre},

Tu reserva en Blessed Barbershop ha sido confirmada con éxito.

Detalles de la cita:
---------------------------
Barbero: {profesional}
Fecha: {fecha}
Hora: {hora}
---------------------------

Adjunto encontrarás el evento para agregarlo a tu calendario personal.

¡Te esperamos! 💈
""")

            # Adjuntar archivo .ics
            ics_content = self.generar_ics(nombre, fecha, hora, profesional)
            if ics_content:
                msg.add_attachment(
                    ics_content.encode('utf-8'),
                    maintype="text",
                    subtype="calendar",
                    filename="reserva_barberia.ics"
                )

            # Usar SSL directo (Puerto 465) para evitar bloqueos en Render
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            
            print(f"✅ Correo enviado a {correo_cliente}")

        except Exception as e:
            print(f"❌ Error enviando correo: {str(e)}")
