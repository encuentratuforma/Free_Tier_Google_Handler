import os
import base64
from flask import Flask, request
from google.cloud import run_v2
from google.protobuf import field_mask_pb2

# Simulation mode
USE_GCP = os.environ.get("USE_GCP", "false").lower() == "true"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def stop_services():
    envelope = request.get_json()

    if not envelope:
        return "Bad Request: No Pub/Sub message received", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        return "Bad Request: Invalid Pub/Sub message format", 400

    pubsub_message = envelope["message"]

    # Decode the message
    if "data" in pubsub_message:
        decoded_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        print(f"Received message: {decoded_data}")
    else:
        decoded_data = ""

    project_id = os.environ.get("PROJECT_ID", "obsidian-cgs")
    region = os.environ.get("REGION", "europe-west1")
    services = ["obsidian-calendar-task-sync"]

    if USE_GCP:
        client = run_v2.ServicesClient()
        for service in services:
            name = f"projects/{project_id}/locations/{region}/services/{service}"
            service_obj = client.get_service(name=name)

            # Create a Service object with 0% traffic
            # This routes traffic to no revisions
            service_obj.traffic = []  # empty list == 0% traffic

            update_mask = field_mask_pb2.FieldMask(paths=["traffic"])

            updated_service = client.update_service(service=service_obj, update_mask=update_mask)
            updated_service.result()  # Wait for the operation to complete

            print(f"Traffic stopped (0%) for service: {service}")

        return "Services traffic stopped", 200
    else:
        for service in services:
            print(f"[SIMULATION] Service stopped (0% traffic): {service}")
        return "Services stopped (simulated)", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)