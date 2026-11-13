from groq import Groq

print("=" * 40)
print("       GARC IA")
print("  Tu inteligencia artificial")
print("=" * 40)

# Modelo que utilizaremos
MODELO = "openai/gpt-oss-120b"

# Aquí guardaremos la conversación
mensajes = [
    {
        "role": "system",
        "content": (
            "Eres GARC IA, una inteligencia artificial creada "
            "para ayudar a las personas. Hablas español de España. "
            "Eres amable, inteligente y paciente. Explicas las cosas "
            "claramente y puedes mantener conversaciones."
        )
    }
]

# Conexión segura: la clave se configurará fuera del código
cliente = Groq()

print("\n¡Hola! Soy GARC IA.")
print("Escribe 'salir' para terminar.\n")

while True:
    pregunta = input("TÚ: ")

    if pregunta.lower() == "salir":
        print("GARC IA: ¡Hasta pronto!")
        break

    mensajes.append({
        "role": "user",
        "content": pregunta
    })

    try:
        respuesta = cliente.chat.completions.create(
            model=MODELO,
            messages=mensajes
        )

        texto = respuesta.choices[0].message.content

        print("\nGARC IA:", texto, "\n")

        mensajes.append({
            "role": "assistant",
            "content": texto
        })

    except Exception as error:
        print("\nNo he podido responder. Comprueba la conexión.\n")
        print("Detalles:", error)
        mensajes.pop()