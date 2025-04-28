import os
import base64
import json
from flask import Flask, request

# Modo simulación
USE_GCP = os.environ.get("USE_GCP", "false").lower() == "true"
if USE_GCP:
    from google.cloud import run_v2

app = Flask(__name__)

@app.route("/", methods=["POST"])
def stop_services():
    envelope = request.get_json()
    
    if not envelope:
        return "Bad Request: No Pub/Sub message received", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        return "Bad Request: Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]

    # Decodificar el mensaje
    if "data" in pubsub_message:
        decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        print(f"Mensaje recibido: {decoded_data}")
    else:
        decoded_data = ""

    project_id = os.environ.get("PROJECT_ID", "obsidian-cgs")
    region = os.environ.get("REGION", "europe-west1")
    services = ["obsidian-calendar-task-sync"]

    if USE_GCP:
        client = run_v2.ServicesClient()
        for service in services:
            name = f"projects/{project_id}/locations/{region}/services/{service}"
            client.delete_service(name=name)
            print(f"Deleted service: {name}")
        return "Services stopped", 200
    else:
        for service in services:
            print(f"[SIMULACIÓN] Servicio detenido: {service}")
        return "Services stopped (simulado)", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)