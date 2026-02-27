let servicioSeleccionado = "";
let barberoIdSeleccionado = null;

// 1. SELECCIONAR SERVICIO
async function seleccionarServicio(nombre, precio) {
    servicioSeleccionado = nombre;
    
    // Cambiar de vista
    document.getElementById('contenedor-servicios').style.display = 'none';
    document.getElementById('formulario-datos').style.display = 'block';
    
    // Actualizar título
    document.getElementById('resumen-servicio').innerText = nombre;
    
    // Cargar barberos desde la DB
    await cargarBarberos();
}

// 2. CARGAR BARBEROS DINÁMICAMENTE
async function cargarBarberos() {
    const contenedor = document.getElementById('contenedor-barberos-fotos');
    contenedor.innerHTML = "<p style='grid-column: span 2; text-align:center;'>Cargando profesionales...</p>";
    
    try {
        const response = await fetch('/barberos/1'); // ID de tu barbería
        const barberos = await response.json();
        
        contenedor.innerHTML = ""; 
        
        barberos.forEach(b => {
            const card = document.createElement('div');
            card.className = "barbero-card";
            card.innerHTML = `
                <img src="${b.foto_url || 'https://via.placeholder.com/100'}" alt="${b.nombre}">
                <span>${b.nombre}</span>
            `;
            
            card.onclick = () => {
                // Lógica de selección visual
                document.querySelectorAll('.barbero-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                barberoIdSeleccionado = b.id;
            };
            
            contenedor.appendChild(card);
        });
    } catch (error) {
        contenedor.innerHTML = "<p style='color:red;'>Error al conectar con el servidor</p>";
        console.error("Error cargando barberos:", error);
    }
}

// 3. VOLVER ATRÁS
function volverAServicios() {
    document.getElementById('contenedor-servicios').style.display = 'block';
    document.getElementById('formulario-datos').style.display = 'none';
    barberoIdSeleccionado = null; // Resetear selección
}

// 4. ENVIAR RESERVA
async function agendarCita() {
    const nombre = document.getElementById('cliente_nombre').value;
    const email = document.getElementById('cliente_email').value;
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;

    if (!barberoIdSeleccionado) {
        alert("Por favor, selecciona un barbero.");
        return;
    }
    if (!nombre || !email || !fecha || !hora) {
        alert("Completa todos los datos personales.");
        return;
    }

    // URL con todos los parámetros necesarios para tu main.py
    const url = `/reservas?barberia_id=1&barbero_id=${barberoIdSeleccionado}&cliente_nombre=${encodeURIComponent(nombre)}&cliente_email=${encodeURIComponent(email)}&servicio=${encodeURIComponent(servicioSeleccionado)}&fecha=${fecha}&hora=${hora}`;

    try {
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            alert("✅ ¡Cita agendada con éxito! Revisa tu email.");
            window.location.reload();
        } else {
            alert("❌ Error: " + data.detail);
        }
    } catch (error) {
        alert("❌ Error de red. Intenta de nuevo.");
    }
}
