import os
import smtplib
import ssl
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Render leerá estas variables del panel 'Environment'
        self.email = os.environ.get("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        
        # Primero intentamos leer la variable de entorno (lo más seguro para Render)
        # Si no existe, usamos la nueva clave que generaste como respaldo
        self.password = os.environ.get("EMAIL_PASSWORD", "szpmoziwisyyodav").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        if not self.password:
            print("❌ ERROR: No hay contraseña configurada (EMAIL_PASSWORD vacía)")
            return

        msg = EmailMessage()
        msg["Subject"] = "Confirmación de Reserva - Blessed Barbershop"
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

¡Te esperamos para brindarte el mejor servicio! 💈
""")

        try:
            # Puerto 465 con SSL es el más recomendado para evitar bloqueos en Render
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
            print(f"✅ Correo enviado con éxito a {correo_cliente}")
        except Exception as e:
            # Esto imprimirá el error real en los Logs de Render si falla
            print(f"❌ Fallo al enviar correo: {str(e)}")
