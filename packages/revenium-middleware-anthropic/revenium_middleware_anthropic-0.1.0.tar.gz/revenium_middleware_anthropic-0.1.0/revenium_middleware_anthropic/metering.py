import os
import time
import logging
import asyncio
import threading
import atexit
import signal
from typing import Literal
from revenium_metering import AsyncReveniumMetering

# Define a StopReason literal type for strict typing of stop_reason
StopReason = Literal["END", "END_SEQUENCE", "TIMEOUT", "TOKEN_LIMIT", "COST_LIMIT", "COMPLETION_LIMIT", "ERROR"]

api_key = os.environ.get("REVENIUM_METERING_API_KEY") or "DUMMY_API_KEY"
client = AsyncReveniumMetering(api_key=api_key)

# Keep track of active metering threads
active_threads = []
shutdown_event = threading.Event()

def handle_exit(*_, **__):
    logging.info("Shutdown initiated, waiting for metering calls to complete...")
    shutdown_event.set()

    # Give threads a chance to notice the shutdown event
    time.sleep(0.1)

    for thread in list(active_threads):
        if thread.is_alive():
            logging.debug(f"Waiting for metering thread to finish...")
            thread.join(timeout=5.0)
            if thread.is_alive():
                logging.warning("Metering thread did not complete in time")

    logging.info("Shutdown complete")

atexit.register(handle_exit)
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

class MeteringThread(threading.Thread):
    def __init__(self, coro, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coro = coro
        self.daemon = False
        self.error = None
        self.loop = None

    def run(self):
        if shutdown_event.is_set():
            return
        try:
            # Create a new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self.coro)
            finally:
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
                self.loop.close()
        except Exception as e:
            if not shutdown_event.is_set():
                self.error = e
                logging.warning(f"Error in metering thread: {str(e)}")
        finally:
            if self in active_threads:
                active_threads.remove(self)

def run_async_in_thread(coroutine):
    """
    Helper function to run an async coroutine in a background thread
    with better handling of interpreter shutdown.
    """
    if shutdown_event.is_set():
        logging.warning("Not starting new metering thread during shutdown")
        return None

    thread = MeteringThread(coroutine)
    active_threads.append(thread)
    thread.start()
    return thread
