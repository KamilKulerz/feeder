from abc import ABC, abstractmethod
import RPi.GPIO as GPIO


class Sensor(ABC):
    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def read(self):
        ...


class GPIOSensor(Sensor):
    def __init__(self, pin: int):
        self.pin = pin
        self.initialize()

    def initialize(self):
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):
        return GPIO.input(self.pin)
