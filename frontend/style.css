let servicioSeleccionado = "";

function seleccionarServicio(nombre, precio) {
    servicioSeleccionado = nombre;
    
    // Cambiar vista
    document.getElementById('contenedor-servicios').style.display = 'none';
    document.getElementById('formulario-datos').style.display = 'block';
    
    // Actualizar título del resumen
    document.getElementById('resumen-servicio').innerText = nombre;
}

function volverAServicios() {
    document.getElementById('contenedor-servicios').style.display = 'block';
    document.getElementById('formulario-datos').style.display = 'none';
}

async function agendarCita() {
    const barberiaId = 1; // ID de tu barbería
    const barberoId = document.getElementById('barbero_id').value;
    const nombre = document.getElementById('cliente_nombre').value;
    const email = document.getElementById('cliente_email').value;
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;

    if (!nombre || !email || !fecha || !hora) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    // Construir la URL con el nuevo campo 'servicio'
    const url = `/reservas?barberia_id=${barberiaId}&barbero_id=${barberoId}&cliente_nombre=${encodeURIComponent(nombre)}&cliente_email=${encodeURIComponent(email)}&servicio=${encodeURIComponent(servicioSeleccionado)}&fecha=${fecha}&hora=${hora}`;

    try {
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            alert("✅ ¡Reserva exitosa! Revisa tu correo.");
            location.reload(); // Recargar página
        } else {
            alert("❌ Error: " + data.detail);
        }
    } catch (error) {
        alert("❌ Error de conexión con el servidor.");
    }
}
