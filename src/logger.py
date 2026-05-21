import sys
import logging
import asyncio
from datetime import datetime
from typing import Set

class ActiveLogsBroadcast:
    def __init__(self):
        self.subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    def publish(self, log_entry: dict):
        for q in list(self.subscribers):
            try:
                q.put_nowait(log_entry)
            except Exception:
                pass

# Global broadcast instances
log_broadcast = ActiveLogsBroadcast()
state_broadcast = ActiveLogsBroadcast()

class CustomHTMLHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": log_message
        }
        # Publish log
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(log_broadcast.publish, log_entry)
            else:
                pass
        except RuntimeError:
            pass

def setup_agent_logger():
    root_logger = logging.getLogger("alpha_agent")
    root_logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup multiple times
    if root_logger.handlers:
        return root_logger

    formatter = logging.Formatter('%(message)s')
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # HTML Log Broadcast Handler
    html_handler = CustomHTMLHandler()
    html_handler.setLevel(logging.INFO)
    root_logger.addHandler(html_handler)

    return root_logger

# Initialize logger
agent_logger = setup_agent_logger()

# Helper to log and broadcast states
def update_agent_status(status_text: str):
    agent_logger.info(f"[STATUS] {status_text}")
    try:
        loop = asyncio.get_event_loop()
        state_entry = {"status": status_text}
        if loop.is_running():
            loop.call_soon_threadsafe(state_broadcast.publish, state_entry)
    except RuntimeError:
        pass
