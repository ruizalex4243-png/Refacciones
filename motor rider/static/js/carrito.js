let carrito = [];

function cargarCarrito() {
    try {
        const guardado = localStorage.getItem("carrito");
        carrito = guardado ? JSON.parse(guardado) : [];
        if (!Array.isArray(carrito)) carrito = [];
    } catch (error) {
        console.error("Error al leer carrito:", error);
        carrito = [];
    }
}

function guardarCarrito() {
    localStorage.setItem("carrito", JSON.stringify(carrito));
}

function actualizarContador() {
    const contador = document.getElementById("cart-count");
    if (!contador) return;
    const total = carrito.reduce((acc, item) => acc + item.cantidad, 0);
    contador.textContent = total;
}

function agregarAlCarrito(id, nombre, precio) {
    const existente = carrito.find(p => p.id === id);
    if (existente) {
        existente.cantidad += 1;
    } else {
        carrito.push({ id, nombre, precio, cantidad: 1 });
    }
    guardarCarrito();
    actualizarContador();
    renderizarCarrito();
    alert(`✅ ${nombre} se agregó al carrito.`);
}

window.eliminarDelCarrito = function(id) {
    carrito = carrito.filter(p => p.id !== id);
    guardarCarrito();
    actualizarContador();
    renderizarCarrito();
};

function renderizarCarrito() {
    const lista = document.getElementById("lista-carrito");
    const totalElemento = document.getElementById("total-carrito");
    if (!lista || !totalElemento) return;

    lista.innerHTML = "";
    let total = 0;

    if (carrito.length === 0) {
        lista.innerHTML = "<p style='color: var(--text-muted); padding-top: 10px;'>Tu carrito está vacío.</p>";
        totalElemento.textContent = "0.00";
        return;
    }

    carrito.forEach(producto => {
        const subtotal = producto.precio * producto.cantidad;
        total += subtotal;

        const li = document.createElement("li");
        li.innerHTML = `
            <div class="item-carrito" style="display:flex; justify-content:space-between; width:100%; align-items:center; gap:12px;">
                <div>
                    <strong style="color:white; font-size:1.1rem;">${producto.nombre}</strong>
                    <p style="color: var(--text-muted); margin-top: 5px;">${producto.cantidad} x $${producto.precio}</p>
                </div>
                <div style="text-align:right;">
                    <span style="color: var(--accent-cyan); display:block; margin-bottom:8px; font-weight:bold;">$${subtotal.toFixed(2)}</span>
                    <button type="button" onclick="eliminarDelCarrito(${producto.id})"
                        style="background: rgba(255,77,77,0.1); color: var(--danger); border: 1px solid var(--danger); padding: 5px 12px; border-radius: 8px; cursor: pointer;">
                        Eliminar
                    </button>
                </div>
            </div>
        `;
        lista.appendChild(li);
    });
    totalElemento.textContent = total.toFixed(2);
}

async function procesarCompra(event) {
    event.preventDefault();
    if (carrito.length === 0) {
        alert("Tu carrito está vacío, agrega algo primero.");
        return;
    }

    const cliente = document.getElementById("cliente")?.value.trim();
    const direccion = document.getElementById("direccion")?.value.trim();
    const pago = document.getElementById("pago")?.value;
    const total = carrito.reduce((acc, item) => acc + item.precio * item.cantidad, 0);

    if (!cliente || !direccion || !pago) {
        alert("Completa todos los datos.");
        return;
    }

    try {
        const response = await fetch("/procesar_pago", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cliente: cliente,
                direccion: direccion,
                pago: pago,
                total: total,
                carrito: carrito // Pasa directo como JSON Array para SQLite
            })
        });

        if (!response.ok) throw new Error(`Error del servidor: ${response.status}`);
        
        const resultado = await response.json();
        
        if (resultado.status === "success") {
            localStorage.removeItem("carrito");
            carrito = [];
            actualizarContador();
            window.location.href = resultado.redirect || "/success";
        } else {
            alert("Error al procesar la compra.");
        }
    } catch (error) {
        console.error("Error procesando compra:", error);
        alert("No se pudo conectar con el servidor.");
    }
}

function iniciarBotonesCarrito() {
    document.addEventListener("click", function(e) {
        const btn = e.target.closest(".btn-agregar-carrito");
        if (!btn) return;
        e.preventDefault();

        const id = parseInt(btn.dataset.id);
        const nombre = btn.dataset.nombre;
        const precio = parseFloat(btn.dataset.precio);

        if (isNaN(id) || !nombre || isNaN(precio)) {
            console.error("Datos inválidos del botón:", btn.dataset);
            return;
        }
        agregarAlCarrito(id, nombre, precio);
    });
}

function iniciarCarruseles() {
    document.querySelectorAll(".producto-carousel").forEach(carrusel => {
        const img = carrusel.querySelector(".img-galeria");
        if (!img) return;

        try {
            const imagenes = JSON.parse(img.dataset.imagenes || "[]");
            if (imagenes.length <= 1) return;
            let index = 0;
            setInterval(() => {
                index = (index + 1) % imagenes.length;
                img.src = imagenes[index];
            }, 2500);
        } catch (error) {
            console.error("Error en carrusel:", error);
        }
    });
}

function iniciarTodo() {
    cargarCarrito();
    actualizarContador();
    renderizarCarrito();
    iniciarBotonesCarrito();
    iniciarCarruseles();

    const formPago = document.getElementById("form-pago");
    if (formPago) {
        formPago.addEventListener("submit", procesarCompra);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciarTodo);
} else {
    iniciarTodo();
}