import os
import smtplib
import ssl
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Render leerá estas variables del panel Environment
        self.email = os.environ.get("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.environ.get("szpmoziwisyyodav", "").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        if not self.password:
            print("❌ ERROR: No hay contraseña configurada en EMAIL_PASSWORD")
            return

        msg = EmailMessage()
        msg["Subject"] = "Confirmación de Reserva - Blessed Barbershop"
        msg["From"] = self.email
        msg["To"] = correo_cliente
        msg.set_content(f"Hola {nombre},\n\nTu reserva con {profesional} para el {fecha} a las {hora} ha sido confirmada.\n\n¡Te esperamos! 💈")

        try:
            # Intentamos puerto 465 (SSL) que es más directo para servidores
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            print(f"✅ Correo enviado con éxito a {correo_cliente}")
        except Exception as e:
            print(f"❌ Fallo al enviar correo: {str(e)}")
