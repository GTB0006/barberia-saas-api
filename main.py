from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import get_connection
from datetime import datetime, time
import pyodbc
import os

# 🔔 WhatsApp
from whatsapp_sender import enviar_mensaje

# ======================================================
# APP
# ======================================================
app = FastAPI(title="API Barbería")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# HORARIOS
# ======================================================
HORA_APERTURA = time(9, 0)
HORA_CIERRE = time(22, 0)

# ======================================================
# FRONTEND
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/frontend",
    StaticFiles(directory=os.path.join(BASE_DIR, "frontend")),
    name="frontend"
)

@app.get("/")
def index():
    return FileResponse(
        os.path.join(BASE_DIR, "frontend", "index.html")
    )

# ======================================================
# CLIENTES
# ======================================================
@app.post("/clientes")
def crear_o_obtener_cliente(nombre: str, telefono: str, cedula: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ClienteId FROM Clientes WHERE Cedula = ?",
            (cedula,)
        )
        row = cursor.fetchone()
        if row:
            return {"cliente_id": row[0]}

        cursor.execute("""
            INSERT INTO Clientes (Nombre, Telefono, Cedula)
            OUTPUT INSERTED.ClienteId
            VALUES (?, ?, ?)
        """, (nombre, telefono, cedula))

        cliente_id = cursor.fetchone()[0]
        conn.commit()
        return {"cliente_id": cliente_id}

    finally:
        conn.close()

# ======================================================
# PROFESIONALES
# ======================================================
@app.get("/profesionales")
def listar_profesionales():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ProfesionalId, Nombre
            FROM Profesionales
            WHERE Activo = 1
            ORDER BY Nombre
        """)

        return [
            {"profesional_id": r[0], "nombre": r[1]}
            for r in cursor.fetchall()
        ]

    finally:
        conn.close()

# ======================================================
# RESERVAS + WHATSAPP
# ======================================================
@app.post("/reservas")
def crear_reserva(cliente_id: int, profesional_id: int, fecha: str, hora: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        hora_inicio = datetime.strptime(hora, "%H:%M").time()

        if not (HORA_APERTURA <= hora_inicio < HORA_CIERRE):
            raise HTTPException(
                status_code=400,
                detail="Horario fuera del rango permitido (09:00 - 22:00)"
            )

        try:
            cursor.execute("""
                INSERT INTO Reservas (ClienteId, ProfesionalId, Fecha, Hora)
                VALUES (?, ?, ?, ?)
            """, (cliente_id, profesional_id, fecha, hora_inicio))

            conn.commit()

        except pyodbc.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="El profesional ya tiene una reserva en ese horario"
            )

        # 📲 DATOS PARA WHATSAPP
        cursor.execute("""
            SELECT C.Nombre, C.Telefono, P.Nombre
            FROM Clientes C
            JOIN Profesionales P ON P.ProfesionalId = ?
            WHERE C.ClienteId = ?
        """, (profesional_id, cliente_id))

        cliente, telefono, profesional = cursor.fetchone()

        mensaje = (
            f"Hola {cliente} 👋\n\n"
            f"✅ Tu reserva fue confirmada:\n"
            f"💈 Profesional: {profesional}\n"
            f"📅 Fecha: {fecha}\n"
            f"⏰ Hora: {hora}\n\n"
            f"Gracias por preferirnos 🙌"
        )

        enviar_mensaje(telefono, mensaje)

        return {"mensaje": "Reserva creada correctamente"}

    finally:
        conn.close()

# ======================================================
# LISTAR RESERVAS
# ======================================================
@app.get("/reservas")
def listar_reservas():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                R.ReservaId,
                C.Nombre,
                C.Telefono,
                P.Nombre,
                R.Fecha,
                R.Hora
            FROM Reservas R
            JOIN Clientes C ON R.ClienteId = C.ClienteId
            JOIN Profesionales P ON R.ProfesionalId = P.ProfesionalId
            ORDER BY R.Fecha, R.Hora
        """)

        return [
            {
                "reserva_id": r[0],
                "cliente": r[1],
                "telefono": r[2],
                "profesional": r[3],
                "fecha": str(r[4]),
                "hora": str(r[5])
            }
            for r in cursor.fetchall()
        ]

    finally:
        conn.close()

# ======================================================
# DISPONIBILIDAD  ✅ (NO SE QUITA)
# ======================================================
@app.get("/disponibilidad")
def disponibilidad(profesional_id: int, fecha: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Hora
            FROM Reservas
            WHERE ProfesionalId = ?
              AND Fecha = ?
        """, (profesional_id, fecha))

        horas_ocupadas = {str(r[0])[:5] for r in cursor.fetchall()}

        horas_disponibles = []
        h = HORA_APERTURA.hour
        while h < HORA_CIERRE.hour:
            hora = f"{h:02d}:00"
            if hora not in horas_ocupadas:
                horas_disponibles.append(hora)
            h += 1

        return horas_disponibles

    finally:
        conn.close()
