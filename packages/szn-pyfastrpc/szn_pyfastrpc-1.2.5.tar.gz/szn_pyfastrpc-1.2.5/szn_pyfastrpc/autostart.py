# szn_pyfastrpc/autostart.py

import threading
import time

def run_service():
    print("Starting FastRPC service...")
    try:
        while True:
            print("FastRPC service is running...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("FastRPC service stopped.")

def start_service():
    """
    Starts the FastRPC service in a daemon thread.
    This function is automatically called upon package import.
    """
    thread = threading.Thread(target=run_service, daemon=True)
    thread.start()
    print("FastRPC service has been started in the background.")
