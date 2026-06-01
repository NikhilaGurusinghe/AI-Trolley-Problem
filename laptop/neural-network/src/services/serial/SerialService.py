import time

import serial

from services.serial.TrackDirection import TrackDirection

class SerialService:
    # baudrate=115200
    def __init__(self, port: str, baudrate: int, encoding: str = "utf-8"):
        self.arduino_serial = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
        self.encoding = encoding
        time.sleep(10)

    def _write(self, message: str):
        self.arduino_serial.write(bytes(f"{message}\n\r", self.encoding))

    def _read_line(self) -> str:
        data: bytes = self.arduino_serial.readline()
        data_string: str = data.decode(self.encoding)

        return data_string

    def _read(self, line_startswith: str) -> str:
        line: str = self._read_line()

        # TODO this might loop forever lol, set a max recursion depth
        while not line.startswith(line_startswith):
            line = self._read_line()

        return line

    # images are not zero indexed, the first one starts at 1
    def send_images(self, image_a_index: int, image_b_index: int) -> str:
        if image_a_index <= 0 or image_b_index <= 0:
            raise TypeError("SerialService#send_images(): invalid image a or image b index parameter")

        self._write(f"TO;PIC;CMD;SHOW;{str(image_a_index)};{str(image_b_index)}")

        # this replies with ACK;FROM;PIC;STATE;DONE;A;<image number>;<OK|MISS>;B;<image number>;<OK|MISS>
        time.sleep(30) # acknowledgement happens after the drawing has occurred which takes like 20 seconds
        response: str = self._read("ACK")
        return response


    def send_track_direction(self, track_direction: TrackDirection):
        # if not(track_direction.name == TrackDirection.LEFT.name and track_direction.name == TrackDirection.RIGHT.name):
        #     raise TypeError("SerialService#send_track_direction(): invalid track direction parameter")

        self._write(f"TO;LINE;CMD;{track_direction.name.upper()}")

        # no ACK is sent

    def get_tap_response(self) -> TrackDirection:
        tap_response: str = self._read("DEC")
        tap_response_split: list[str] = tap_response.split(";")

        return TrackDirection[tap_response_split[4].upper()]


