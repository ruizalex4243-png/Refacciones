from flask import Flask, render_template, redirect, url_for, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

app = Flask(__name__)

# =========================
# BASE DE DATOS
# =========================
# URL de conexión a tu base de datos Neon (PostgreSQL)
DB_URL = "postgresql://neondb_owner:npg_ehzgA7xIPlv5@ep-soft-feather-a6flzaim-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db():
    # Nos conectamos y usamos RealDictCursor para que los resultados funcionen como diccionarios
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # En PostgreSQL se usa SERIAL para autoincrementar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id SERIAL PRIMARY KEY,
            cliente TEXT,
            direccion TEXT,
            pago TEXT,
            carrito TEXT,
            total REAL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # En PostgreSQL podemos usar ADD COLUMN IF NOT EXISTS de forma directa
    cur.execute("ALTER TABLE ordenes ADD COLUMN IF NOT EXISTS carrito TEXT")
    conn.commit()
    cur.close()
    conn.close()

init_db()

# =========================
# CATÁLOGO DE PRODUCTOS
# =========================
PRODUCTOS = [
    {
        "id": 1,
        "nombre": "Llanta Deportiva Diablo Rosso 17",
        "categoria": "Llantas",
        "precio": 2500,
        "descripcion": "Máximo agarre en asfalto para motos deportivas.",
        "imagenes": [
            "https://i5.walmartimages.com/asr/69dd3636-9783-4188-9dff-5cf4cb02595a.3d1d79c68fdd3dbc58201239e9aed416.png",
            "https://i5.walmartimages.com/asr/38f7e260-189b-41ab-9503-4e895607e060.41401b39358e00aa13d1eecb148b6287.png",
            "https://i5.walmartimages.com/asr/050a0201-efb8-4822-a4a2-60f87ca2aef0.f42ad3c9affba3cf3837159d23f0414b.png",
            "https://i5.walmartimages.com/asr/275b2bad-3b12-4f29-8dfd-18903b058f59.263ed253a92106371e1063be8cd9a553.png"
        ]
    },
    {
        "id": 2,
        "nombre": "Balatas Sinterizadas",
        "categoria": "Frenos",
        "precio": 650,
        "descripcion": "Frenado de alta precisión y resistencia a altas temperaturas.",
        "imagenes": [
            "https://bajajmatriz.com/wp-content/uploads/2024/03/MD-F269.jpg",
            "https://resources.sanborns.com.mx/medios-plazavip/t1/1747881484R091106ZapataFA4424HHEBCDELANTERASDOBLESjpg?scale=700&qlty=80",
            "https://chg.mx/cdn/shop/files/1314-1221.jpg",
            "https://http2.mlstatic.com/D_NQ_NP_2X_923992-MLM99163199096_112025-F.webp"
        ]
    },
    {
        "id": 3,
        "nombre": "Aceite Sintético 4T 10W-40",
        "categoria": "Mantenimiento",
        "precio": 320,
        "descripcion": "Protección extrema para motores de 4 tiempos.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_804282-MLM78417231342_082024-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_750337-MLM78648811273_082024-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_880087-MLM74443605169_022024-F.webp",
            "https://m.media-amazon.com/images/I/717N4ib0CjL._AC_SX522_.jpg"
        ]
    },
    {
        "id": 4,
        "nombre": "Batería de Gel YTX9-BS",
        "categoria": "Eléctrico",
        "precio": 950,
        "descripcion": "Mayor durabilidad y arranque en frío asegurado.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_982691-MLM111475335997_052026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_800936-MLM110532655396_052026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_614246-MLM111475602569_052026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_692985-MLM111475602567_052026-F.webp"
        ]
    },
    {
        "id": 5,
        "nombre": "Amortiguador Monoshock",
        "categoria": "Suspensión",
        "precio": 3200,
        "descripcion": "Suspensión ajustable para máxima comodidad y control.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_859923-MLM101943130651_122025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_872411-MLM101049706967_122025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_760168-MLM101048981751_122025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_914082-MLM101049706991_122025-F.webp"
        ]
    },
    {
        "id": 6,
        "nombre": "Cadena Reforzada O-Ring 520",
        "categoria": "Transmisión",
        "precio": 1200,
        "descripcion": "Alta resistencia a la tensión y menor fricción.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_679837-MLM105503054717_012026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_619039-MLM105502214635_012026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_847057-MLM108520462013_032026-F.webp",
            "https://storage.googleapis.com/bcx-imagenes/Items2/0212750005.webp"
        ]
    },
    {
        "id": 7,
        "nombre": "Bujía de Iridio",
        "categoria": "Motor",
        "precio": 280,
        "descripcion": "Combustión eficiente y mayor respuesta al acelerar.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_723416-CBT109355904460_042026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_741906-CBT106000808050_022026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_706593-CBT106000808068_022026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_825395-CBT106618142573_022026-F.webp"
        ]
    },
    {
        "id": 8,
        "nombre": "Filtro de Aire de Alto Flujo",
        "categoria": "Motor",
        "precio": 750,
        "descripcion": "Mejora la entrada de aire y la potencia del motor.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_625697-MLM91227856829_082025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_652638-MLM79610753678_102024-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_604764-MLM79859832769_102024-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_687695-MLM79610773144_102024-F.webp"
        ]
    },
    {
        "id": 9,
        "nombre": "Faro LED Principal 6000K",
        "categoria": "Eléctrico",
        "precio": 850,
        "descripcion": "Iluminación potente y clara para conducción nocturna.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_817173-CBT98454409004_112025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_722120-CBT52246262591_112022-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_753703-CBT52246321354_112022-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_989283-CBT52246278475_112022-F.webp"
        ]
    },
    {
        "id": 10,
        "nombre": "Kit de Arrastre Deportivo",
        "categoria": "Transmisión",
        "precio": 2100,
        "descripcion": "Sprocket y piñón de aleación ligera para mejor aceleración.",
        "imagenes": [
            "https://http2.mlstatic.com/D_NQ_NP_2X_987415-MLM96792079297_102025-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_717689-MLM103784199716_012026-F.webp",
            "https://http2.mlstatic.com/D_NQ_NP_2X_932199-MLM103784199718_012026-F.webp",
            "https://m.media-amazon.com/images/I/51L4V02exIL._SX342_SY445_QL70_ML2_.jpg"
        ]
    }
]

# =========================
# RUTAS DE LA APLICACIÓN
# =========================
@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/catalogo")
def catalogo():
    return render_template("catalogo.html", productos=PRODUCTOS)

@app.route("/checkout")
def checkout():
    return render_template("formulario.html")

@app.route("/procesar_pago", methods=["POST"])
def procesar_pago():
    data = request.get_json()

    cliente = data.get("cliente", "Desconocido")
    direccion = data.get("direccion", "No especificada")
    pago = data.get("pago", "No especificado")
    total = data.get("total", 0.0)
    carrito = json.dumps(data.get("carrito", []))

    conn = get_db()
    cur = conn.cursor()
    # Cambiamos los '?' de SQLite por los '%s' de PostgreSQL
    cur.execute(
        """INSERT INTO ordenes (cliente, direccion, pago, carrito, total)
        VALUES (%s, %s, %s, %s, %s)""",
        (cliente, direccion, pago, carrito, total),
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success", "redirect": url_for("compra_realizada")})

@app.route("/compra_realizada")
def compra_realizada():
    return render_template("compra_realizada.html")

@app.route("/referencias")
def referencias():
    return render_template("referencias.html")

@app.route("/registro")
def registro():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ordenes ORDER BY id DESC")
    ventas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("registro.html", ventas=ventas)

@app.route("/juego")
def abrir_juego():
    return render_template("juego.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)