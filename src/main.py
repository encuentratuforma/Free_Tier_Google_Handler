import os
import base64
import logging
from flask import Flask, request
from google.cloud import run_v2
from google.protobuf import field_mask_pb2

# Enable structured logging for Cloud Run / Cloud Logging
logging.basicConfig(level=logging.INFO)

# Load config from environment variables
USE_GCP = os.environ.get("USE_GCP", "false").lower() == "true"
PROJECT_ID = os.environ.get("PROJECT_ID", "your-gcp-project-id")
REGION = os.environ.get("REGION", "europe-west1")
SERVICES = os.environ.get("SERVICES", "obsidian-calendar-task-sync").split(",")

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def stop_services():
    envelope = request.get_json()
    if not envelope or "message" not in envelope:
        logging.error("Invalid Pub/Sub message format.")
        return "Bad Request: Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]
    try:
        if "data" in pubsub_message:
            decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
            logging.info(f"Received Pub/Sub message: {decoded_data}")
    except Exception as e:
        logging.error(f"Failed to decode Pub/Sub data: {e}")
        return "Error decoding Pub/Sub message", 400

    if USE_GCP:
        client = run_v2.ServicesClient()
        for service in SERVICES:
            name = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service.strip()}"
            try:
                service_obj = client.get_service(name=name)
                service_obj.traffic = []
                update_mask = field_mask_pb2.FieldMask(paths=["traffic"])
                operation = client.update_service(service=service_obj, update_mask=update_mask)
                operation.result()
                logging.info(f"Traffic successfully set to 0% for service: {service}")
            except Exception as e:
                logging.error(f"Failed to update service '{service}': {e}")
        return "Service traffic set to 0%", 200
    else:
        for service in SERVICES:
            logging.info(f"[SIMULATION] Would stop traffic for service: {service.strip()}")
        return "Simulation complete", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
