import os
from flask import Flask, request

# Modo simulación (no llamar a APIs reales)
USE_GCP = os.environ.get("USE_GCP", "false").lower() == "true"
if USE_GCP:
    from google.cloud import run_v2

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def stop_services():
    project_id = os.environ.get("PROJECT_ID", "obsidian-cgs")
    region = os.environ.get("REGION", "europe-west1")
    services = ["obsidian-calendar-task-sync"]

    if request.method == "POST":
        if USE_GCP:
            client = run_v2.ServicesClient()
            for service in services:
                name = f"projects/{project_id}/locations/{region}/services/{service}"
                client.delete_service(name=name)
                print(f"Deleted service: {name}")
            return "✅ Services stopped", 200
        else:
            for service in services:
                print(f"[SIMULACIÓN] Servicio detenido: {service}")
            return "✅ Services stopped (simulado)", 200
    else:
        # GET request
        return """
        <h1>🌟 Bienvenido al Budget Exceeded Handler</h1>
        <p>Este servidor está funcionando correctamente.</p>
        <p>Para detener los servicios, envía una solicitud <b>POST</b> a esta URL.</p>
        """, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
