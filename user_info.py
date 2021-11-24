from abc import ABC, abstractmethod
import board
import neopixel


class UserInfo(ABC):
    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def ok(self, show: bool):
        ...

    @abstractmethod
    def nok(self, show: bool):
        ...

    @abstractmethod
    def working(self, show: bool):
        ...

    @abstractmethod
    def clear(self):
        ...


class LEDUserInfo(UserInfo):
    def __init__(self, no_leds: int):
        self.no_leds = no_leds
        self.initialize()

    def initialize(self):
        self.pixels = neopixel.NeoPixel(board.D21, self.no_leds)

    def ok(self, show: bool):
        if show:
            for i in range(self.no_leds):
                self.pixels[i] = (0, 255, 0)
        else:
            self.clear()

    def nok(self, show: bool):
        if show:
            for i in range(self.no_leds):
                self.pixels[i] = (255, 0, 0)
        else:
            self.clear()

    def working(self, show: bool):
        if show:
            for i in range(self.no_leds):
                self.pixels[i] = (0, 0, 255)
        else:
            self.clear()

    def clear(self):
        for i in range(self.no_leds):
            self.pixels[i] = (0, 0, 0)
