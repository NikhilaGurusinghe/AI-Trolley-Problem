import threading
from asyncio import timeout
from queue import Queue
from typing import Tuple

import pyttsx3


class TTSService:
    def __init__(self):
        self._queue: Queue[Tuple[str, threading.Event] | str | None] = Queue()
        self._thread = threading.Thread(target=self._worker_thread, daemon=True)
        self._thread.start()

    def _worker_thread(self):
        engine = pyttsx3.init()

        engine.setProperty("rate", 120)

        engine.setProperty("volume", 0.5)

        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[1].id)

        while True:
            item: Tuple[str, threading.Event] | str | None = self._queue.get()

            if isinstance(item, tuple):
                text, event = item
            else:
                text, event = item, None

            # way to stop the worker thread
            if text is None:
                break

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
            finally:
                if event:
                    event.set()

    def speak(self, text: str, blocking: bool = True):
        if blocking:
            event = threading.Event()
            self._queue.put((text, event))
            event.wait()
        else:
            if text is None:
                return

            self._queue.put(text)

    def stop_worker_thread(self):
        self._queue.put(None)
        self._thread.join(timeout=1)