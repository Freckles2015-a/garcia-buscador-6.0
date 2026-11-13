
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)
cliente = Groq()

MODELO = "openai/gpt-oss-120b"

PERSONALIDAD = """
Eres GARC IA, una inteligencia artificial creada para ayudar.
Hablas español de España.
Eres amable, inteligente, paciente y explicas claramente.
Tu nombre es GARC IA.
"""

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GARC IA</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #07111f;
    color: white;
    font-family: Arial, sans-serif;
    height: 100vh;
    display: flex;
    justify-content: center;
}
.contenedor {
    width: 100%;
    max-width: 850px;
    display: flex;
    flex-direction: column;
    padding: 20px;
}
header {
    text-align: center;
    padding: 18px;
    color: #00e5ff;
    font-size: 30px;
    font-weight: bold;
    text-shadow: 0 0 15px #00e5ff;
}
#chat {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #16405c;
    border-radius: 15px;
    padding: 18px;
    background: #0b1929;
}
.mensaje {
    padding: 13px;
    margin: 12px 0;
    border-radius: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
}
.usuario { background: #123b58; }
.ia { background: #102b35; border: 1px solid #087e91; }
form {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}
input {
    flex: 1;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #087e91;
    background: #102238;
    color: white;
    font-size: 16px;
    min-width: 0;
}
button {
    background: #00cce5;
    border: none;
    border-radius: 10px;
    padding: 15px 22px;
    font-weight: bold;
    cursor: pointer;
}
button:disabled { opacity: .5; cursor: wait; }
#estado { color: #9bb7c8; text-align: center; padding: 10px; }
</style>
</head>
<body>
<div class="contenedor">
<header>🤖 GARC IA</header>
<div id="chat">
<div class="mensaje ia">¡Hola! Soy GARC IA. ¿En qué puedo ayudarte hoy?</div>
</div>
<div id="estado">Tu inteligencia artificial personal</div>
<form id="formulario">
<input id="pregunta" placeholder="Escribe tu pregunta..." autocomplete="off" required>
<button id="enviar" type="submit">Enviar</button>
</form>
</div>

<script>
const chat = document.getElementById("chat");
const formulario = document.getElementById("formulario");
const pregunta = document.getElementById("pregunta");
const enviar = document.getElementById("enviar");
const estado = document.getElementById("estado");

let historial = [];

function mostrar(texto, tipo) {
    const mensaje = document.createElement("div");
    mensaje.className = "mensaje " + tipo;
    mensaje.textContent = texto;
    chat.appendChild(mensaje);
    chat.scrollTop = chat.scrollHeight;
}

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    const texto = pregunta.value.trim();
    if (!texto) return;

    mostrar(texto, "usuario");
    pregunta.value = "";
    enviar.disabled = true;
    estado.textContent = "GARC IA está pensando...";

    try {
        const respuesta = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                message: texto,
                history: historial
            })
        });

        const datos = await respuesta.json();
        if (!respuesta.ok) throw new Error(datos.error || "Error del servidor");

        mostrar(datos.answer, "ia");
        historial.push({role: "user", content: texto});
        historial.push({role: "assistant", content: datos.answer});
        estado.textContent = "GARC IA está lista";
    } catch (error) {
        mostrar("No he podido responder: " + error.message, "ia");
        estado.textContent = "Comprueba la conexión";
    } finally {
        enviar.disabled = false;
        pregunta.focus();
    }
});
</script>
</body>
</html>
"""

@app.route("/")
def inicio():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    datos = request.get_json(silent=True) or {}
    pregunta = datos.get("message", "").strip()

    if not pregunta or len(pregunta) > 4000:
        return jsonify({"error": "La pregunta está vacía o es demasiado larga."}), 400

    historial = datos.get("history", [])
    mensajes = [{"role": "system", "content": PERSONALIDAD}]

    if isinstance(historial, list):
        for mensaje in historial[-20:]:
            if (isinstance(mensaje, dict)
                and mensaje.get("role") in ("user", "assistant")
                and isinstance(mensaje.get("content"), str)):
                mensajes.append({
                    "role": mensaje["role"],
                    "content": mensaje["content"][:4000]
                })

    mensajes.append({"role": "user", "content": pregunta})

    try:
        resultado = cliente.chat.completions.create(
            model=MODELO,
            messages=mensajes
        )
        respuesta = resultado.choices[0].message.content or ""
        return jsonify({"answer": respuesta})
    except Exception:
        app.logger.exception("Error al consultar el modelo")
        return jsonify({
            "error": "No se ha podido conectar con el servicio de IA."
        }), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
