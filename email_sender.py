import os
import smtplib
import ssl
from email.message import EmailMessage

class EmailSender:
    def __init__(self):
        # Tomar variables de entorno o valores por defecto
        self.email = os.environ.get("EMAIL_USER", "blessedbarbershopenv@gmail.com")
        self.password = os.environ.get("EMAIL_PASSWORD", "szpmoziwisyyodav").strip()

    def enviar_confirmacion(self, correo_cliente, nombre, fecha, hora, profesional):
        if not self.password:
            print("❌ ERROR: Contraseña no configurada")
            return

        msg = EmailMessage()
        msg["Subject"] = "💈 Confirmación de tu Cita - Blessed Barbershop"
        msg["From"] = self.email
        msg["To"] = correo_cliente
        
        cuerpo = f"""
Hola {nombre},

¡Tu cita ha sido agendada con éxito!

✂️ Barbero: {profesional}
📅 Fecha: {fecha}
⏰ Hora: {hora}

¡Te esperamos!
"""
        msg.set_content(cuerpo)

        try:
            # CAMBIO: Usamos SMTP estándar (587) en lugar de SSL directo
            # Creamos un contexto de seguridad que ignora errores de validación de host si Render los da
            context = ssl.create_default_context()
            
            print(f"Intentando conectar a smtp.gmail.com por el puerto 587...")
            
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
                server.starttls(context=context) # Inicia la encriptación
                server.login(self.email, self.password)
                server.send_message(msg)
                
            print(f"✅ Correo enviado con éxito a {correo_cliente}")
        except Exception as e:
            print(f"❌ Fallo al enviar correo: {str(e)}")
