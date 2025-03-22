import os
import time
import logging
import asyncio
import threading
import atexit
import signal
from typing import Literal, Awaitable, Any, Optional, Callable
from revenium_metering import ReveniumMetering

# Define a StopReason literal type for strict typing of stop_reason
StopReason = Literal["END", "END_SEQUENCE", "TIMEOUT", "TOKEN_LIMIT", "COST_LIMIT", "COMPLETION_LIMIT", "ERROR"]

api_key = os.environ.get("REVENIUM_METERING_API_KEY") or "DUMMY_API_KEY"
client = ReveniumMetering(api_key=api_key)

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
        self.daemon = True
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

def run_async_in_thread(coroutine_or_func):
    """
    Helper function to run an async coroutine or a regular function in a background thread
    with better handling of interpreter shutdown.
    
    Args:
        coroutine_or_func: Either an awaitable coroutine or a regular function
        
    Returns:
        threading.Thread: The thread running the task
    """
    if shutdown_event.is_set():
        logging.warning("Not starting new metering thread during shutdown")
        return None

    # Check if we received a coroutine or a regular function
    if asyncio.iscoroutine(coroutine_or_func):
        # It's a coroutine, use it directly
        coro = coroutine_or_func
    else:
        # It's a regular function or already the result, wrap it in a coroutine
        async def wrapper():
            return coroutine_or_func
        coro = wrapper()

    thread = MeteringThread(coro)
    active_threads.append(thread)
    thread.start()
    return thread
