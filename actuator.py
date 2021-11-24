from abc import ABC, abstractmethod
import RPi.GPIO as GPIO


class Actuator(ABC):
    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def activate(self):
        ...

    @abstractmethod
    def deactivate(self):
        ...


class GPIOActuator(Actuator):
    def __init__(self, pin: int):
        self.pin = pin
        self.initialize()

    def initialize(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)

    def activate(self):
        GPIO.output(self.pin, GPIO.LOW)

    def deactivate(self):
        GPIO.output(self.pin, GPIO.HIGH)
