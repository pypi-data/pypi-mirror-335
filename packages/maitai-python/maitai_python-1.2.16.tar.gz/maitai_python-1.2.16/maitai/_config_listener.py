import json
import logging
import os
import threading

import websocket

from maitai.models.application import Application


class ConfigListener:
    def __init__(self, config, path, type, key=None):
        self.config = config
        self.ws_url = f"{path}?type={type}"
        if key:
            self.ws_url += f"&key={key}"

        self.ws = None
        self.ws_thread = None
        self.running = False

    def on_message(self, ws, message):
        event = json.loads(message)
        if event.get("event_type") == "APPLICATION_CONFIG_CHANGE":
            application_json = event.get("event_data")
            if application_json:
                try:
                    application = Application.model_validate(application_json)
                    logging.log("Maitai received configuration change")
                    self.config.store_application_metadata([application])
                except Exception as e:
                    if os.environ.get("MAITAI_ENV") in [
                        "development",
                        "staging",
                        "prod",
                    ]:
                        logging.error(
                            "Error refreshing applications",
                            exc_info=e,
                        )
                    self.config.refresh_applications()
            else:
                self.config.refresh_applications()

    def on_error(self, ws, error):
        if not isinstance(error, (AttributeError, ConnectionError)):
            logging.error(f"Maitai config websocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            f"Maitai config websocket connection closed: {close_status_code} {close_msg}"
        )

    def on_open(self, ws):
        logging.info(f"Maitai config websocket connection established")

    def _websocket_thread(self):
        """Run the websocket client in a thread with automatic reconnection."""
        retry_count = 0
        max_retries = 10
        reconnect_delay = 3  # Start with 3 seconds

        while self.running and retry_count < max_retries:
            try:
                # Create new websocket connection
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )

                # Run the websocket (this blocks until connection closes)
                self.ws.run_forever(ping_interval=30, ping_timeout=10)

                # If we get here, connection closed - retry with backoff if still running
                if self.running:
                    retry_count += 1
                    # Exponential backoff with max of 60 seconds
                    retry_delay = min(reconnect_delay * (2**retry_count), 60)
                    logging.info(f"Websocket reconnecting in {retry_delay} seconds...")
                    threading.Event().wait(retry_delay)
            except Exception as e:
                logging.error(f"Error in websocket thread: {e}")
                if self.running:
                    retry_count += 1
                    # Exponential backoff with max of 60 seconds
                    retry_delay = min(reconnect_delay * (2**retry_count), 60)
                    logging.info(f"Websocket reconnecting in {retry_delay} seconds...")
                    threading.Event().wait(retry_delay)

    def _reconnect(self):
        """Attempt to reconnect the websocket."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None

    def start(self):
        """Start the websocket connection."""
        if self.running:
            return

        self.running = True

        # Start websocket in a separate thread with reconnection logic
        self.ws_thread = threading.Thread(
            target=self._websocket_thread,
            name="WebsocketThread",
            daemon=True,
        )
        self.ws_thread.start()

    def stop(self):
        """Stop the websocket connection."""
        if not self.running:
            return

        self.running = False

        # Close the websocket connection
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logging.debug(f"Error closing websocket: {e}")

        # Wait for the thread to finish
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=2.0)

        self.ws = None
        self.ws_thread = None
