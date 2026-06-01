import pyttsx3


class TTSService:
    def __init__(self):
        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 100)

        self.engine.setProperty("volume", 0.5)

        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[1].id)

    def say(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()
        self.engine.stop()