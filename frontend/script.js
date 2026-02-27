let servicioSeleccionado = "";
let barberoIdSeleccionado = null;

async function seleccionarServicio(nombre, precio) {
    servicioSeleccionado = nombre;
    document.getElementById('contenedor-servicios').style.display = 'none';
    document.getElementById('formulario-datos').style.display = 'block';
    document.getElementById('resumen-servicio').innerText = nombre;
    await cargarBarberos();
}

async function cargarBarberos() {
    const contenedor = document.getElementById('contenedor-barberos-fotos');
    contenedor.innerHTML = "<p style='text-align:center;'>Cargando barberos...</p>";
    
    try {
        const response = await fetch('/barberos/1');
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
                document.querySelectorAll('.barbero-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                barberoIdSeleccionado = b.id;
            };
            contenedor.appendChild(card);
        });
    } catch (e) {
        contenedor.innerHTML = "<p style='color:red;'>Error al conectar</p>";
    }
}

function volverAServicios() {
    document.getElementById('contenedor-servicios').style.display = 'block';
    document.getElementById('formulario-datos').style.display = 'none';
    barberoIdSeleccionado = null;
}

async function agendarCita() {
    const nombre = document.getElementById('cliente_nombre').value;
    const email = document.getElementById('cliente_email').value;
    const telefono = document.getElementById('cliente_telefono').value;
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;

    if (!barberoIdSeleccionado || !nombre || !fecha || !hora) return alert("Completa todos los datos");

    const params = new URLSearchParams({
        barberia_id: 1, barbero_id: barberoIdSeleccionado,
        cliente_nombre: nombre, cliente_email: email,
        cliente_telefono: telefono, servicio: servicioSeleccionado,
        fecha: fecha, hora: hora
    });

    try {
        const res = await fetch(`/reservas?${params.toString()}`, { method: 'POST' });
        if (res.ok) {
            alert("✅ ¡Cita Agendada!");
            window.location.reload();
        } else {
            const err = await res.json();
            alert("❌ " + err.detail);
        }
    } catch (e) { alert("Error de red"); }
}
