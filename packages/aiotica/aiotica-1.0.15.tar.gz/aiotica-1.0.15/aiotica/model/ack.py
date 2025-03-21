import json
import sys
from datetime import datetime, timezone


class Ack:
    def __init__(self, json_payload=None):
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.date = formatted_time
        if json_payload is None:
            self.ack_type = None
            self.payload = None
            return

        # Parse the JSON payload if it's a string
        if isinstance(json_payload, str):
            try:
                json_payload = json.loads(json_payload)
            except json.JSONDecodeError:
                self.is_valid_package = False
                return  # Early exit if JSON is invalid

        # Set attributes based on the JSON keys
        self.ack_type = json_payload.get("ackType")
        self.payload = json_payload.get("payload")
        if self.is_valid_package() == False:
            print(f"Failed to initial Command() {json_payload}", file=sys.stderr)

    def is_valid_package(self):
        return all([self.ack_type, self.payload])

    def to_dict(self):
        if self.is_valid_package() == False:
            print("Invalid ack type package", file=sys.stderr)

        return {
            "ackType": self.ack_type,
            "payload": self.payload,
        }
