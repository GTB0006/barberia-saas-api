from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection
from datetime import datetime, time
import os
from dotenv import load_dotenv

load_dotenv()

# Asegúrate de tener estos archivos o comenta estas líneas si no los usas aún
from email_sender import EmailSender
from calendar_sender import CalendarSender

app = FastAPI(title="Blessed Barbershop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

email_sender = EmailSender()
calendar_sender = CalendarSender()

HORA_APERTURA = time(9, 0)
HORA_CIERRE = time(22, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Servir archivos estáticos (CSS, JS, Imágenes)
app.mount("/frontend", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="frontend")

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.get("/admin")
def admin_panel():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "admin.html"))

# --- LISTAR BARBEROS ---
@app.get("/barberos/{barberia_id}")
def listar_barberos(barberia_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, nombre, foto_url FROM barberos WHERE barberia_id = %s AND activo = TRUE"
        cursor.execute(query, (barberia_id,))
        rows = cursor.fetchall()
        return [{"id": r[0], "nombre": r[1], "foto_url": r[2]} for r in rows]
    finally:
        conn.close()

# --- CREAR RESERVA ---
@app.post("/reservas")
def crear_reserva(
    barberia_id: int, barbero_id: int, cliente_nombre: str,
    cliente_email: str, cliente_telefono: str, servicio: str,
    fecha: str, hora: str, background_tasks: BackgroundTasks
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Validar horario
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        if not (HORA_APERTURA <= hora_obj < HORA_CIERRE):
            raise HTTPException(status_code=400, detail="Barbería cerrada en este horario")

        # Validar disponibilidad (rango 1h)
        cursor.execute("""
            SELECT id FROM reservas 
            WHERE barberia_id = %s AND barbero_id = %s AND fecha = %s 
            AND (hora::time, interval '59 minutes') OVERLAPS (%s::time, interval '59 minutes')
        """, (barberia_id, barbero_id, fecha, hora))
        
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Horario no disponible para este barbero")

        # Insertar
        cursor.execute("""
            INSERT INTO reservas (barberia_id, barbero_id, cliente_nombre, cliente_email, cliente_telefono, servicio, fecha, hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (barberia_id, barbero_id, cliente_nombre, cliente_email, cliente_telefono, servicio, fecha, hora))
        conn.commit()

        # Notificaciones
        cursor.execute("SELECT nombre FROM barberos WHERE id = %s", (barbero_id,))
        profesional = cursor.fetchone()[0]
        
        try:
            email_sender.enviar_confirmacion(cliente_email, cliente_nombre, fecha, hora, profesional)
        except: pass

        background_tasks.add_task(calendar_sender.crear_evento, cliente_email, cliente_nombre, fecha, hora, profesional)

        return {"mensaje": "Reserva exitosa"}
    finally:
        conn.close()

# --- LISTAR RESERVAS (ADMIN) ---
@app.get("/reservas/{barberia_id}")
def listar_reservas(barberia_id: int, token: str = None):
    if token != "Blessed2026":
        raise HTTPException(status_code=401, detail="No autorizado")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.cliente_nombre, r.servicio, r.fecha, r.hora, b.nombre, r.cliente_telefono
            FROM reservas r
            JOIN barberos b ON r.barbero_id = b.id
            WHERE r.barberia_id = %s
            ORDER BY r.fecha DESC, r.hora DESC LIMIT 100
        """, (barberia_id,))
        return [{"cliente": r[0], "servicio": r[1], "fecha": str(r[2]), "hora": str(r[3]), "barbero": r[4], "telefono": r[5]} for r in cursor.fetchall()]
    finally:
        conn.close()
