import os
import base64
import logging
import json
from datetime import datetime, timezone
from flask import Flask, request
from google.cloud import run_v2
from google.protobuf import field_mask_pb2
from google.api_core.retry import Retry, if_transient_error

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
    logging.info("Incoming request received by stop_services()")
    envelope = request.get_json()

    if not envelope or "message" not in envelope:
        logging.error(json.dumps({
            "event": "invalid_request",
            "error": "Missing or malformed Pub/Sub message",
            "raw": envelope
        }))
        return "Bad Request: Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]
    try:
        if "data" in pubsub_message:
            decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
            logging.info(json.dumps({
                "event": "pubsub_received",
                "decoded_message": decoded_data
            }))
    except Exception as e:
        logging.error(json.dumps({
            "event": "decode_error",
            "error": str(e)
        }))
        return "Error decoding Pub/Sub message", 400

    if USE_GCP:
        client = run_v2.ServicesClient()

        retry_policy = Retry(
            predicate=if_transient_error,
            initial=1.0,
            maximum=10.0,
            multiplier=2.0,
            deadline=30.0
        )

        for service in SERVICES:
            service = service.strip()
            name = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service}"
            try:
                service_obj = client.get_service(name=name)
                service_obj.traffic = []
                update_mask = field_mask_pb2.FieldMask(paths=["traffic"])
                operation = client.update_service(service=service_obj, update_mask=update_mask)
                operation.result()
                logging.info(json.dumps({
                    "event": "traffic_update",
                    "service": service,
                    "status": "success",
                    "traffic_percent": 0,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))

            except Exception as e:
                logging.error(json.dumps({
                    "event": "traffic_update",
                    "service": service,
                    "status": "failed",
                    "error": str(e),
                    "traffic_percent": None
                }))
        return "Service traffic set to 0%", 200
    else:
        for service in SERVICES:
            logging.info(json.dumps({
                "event": "simulation",
                "service": service.strip(),
                "status": "would_set_traffic_to_0"
            }))
        return "Simulation complete", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
