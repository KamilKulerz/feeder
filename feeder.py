import json
from transitions import Machine
import time
import RPi.GPIO as GPIO
from typing import Type
import time
from .actuator import GPIOActuator, Actuator
from .sensor import GPIOSensor, Sensor
from .user_info import LEDUserInfo, UserInfo


class BowlFeeder(object):
    states = ['barcode_scanned', 'idle_closed', 'cover_state_check', 'r_lock_active', 'r_lock_deactive', 'error_info']

    def __init__(self, dict_of_barcodes: dict, actuator: Type[Actuator], sensor: Type[Sensor], user_info: UserInfo):
        self.dict_of_barcodes = dict_of_barcodes
        self.scanned_barcode = None
        self.selected_output = None
        self.actuators = {key: actuator(self.dict_of_barcodes[key]['actuator']) for key in self.dict_of_barcodes.keys()}
        self.sensors = {key: sensor(self.dict_of_barcodes[key]['sensor']) for key in self.dict_of_barcodes.keys()}
        self.user_info = user_info
        self.user_info.initialize()

        self.machine = Machine(model=self, states=BowlFeeder.states, initial='idle_closed')

        self.machine.add_transition(trigger='scanning_received', source='idle_closed', dest='barcode_scanned')
        self.machine.add_transition(trigger='barcode_nok', source='barcode_scanned', dest='idle_closed', before='wrong_barcode_info')
        self.machine.add_transition(trigger='barcode_ok', source='barcode_scanned', dest='cover_state_check', before='select_output')
        self.machine.add_transition(trigger='not_all_covers_closed', source='cover_state_check', dest='error_info')
        self.machine.add_transition(trigger='info_shown', source='error_info', dest='idle_closed')
        self.machine.add_transition(trigger='all_covers_closed', source='cover_state_check', dest='r_lock_active')
        self.machine.add_transition(trigger='lock_moved_from_base', source='r_lock_active', dest='r_lock_deactive')
        self.machine.add_transition(trigger='lock_moved_to_base', source='r_lock_deactive', dest='idle_closed')

    def select_output(self, scanned: str):
        self.scanned_barcode = scanned
        self.selected_output = self.dict_of_barcodes[self.scanned_barcode]

    def wrong_barcode_info(self):
        print('Barcode not correct!!')

    def get_covers_closed(self):
        state = [sensor.read() for sensor in self.sensors.values()]
        print(state)
        if 0 in state:
            return False
        else:
            return True

    def show_error_info(self):
        print('error')

    def get_is_lock_opened(self):
        if self.sensors[self.scanned_barcode].read() == 1:
            return False
        else:
            self.actuators[self.scanned_barcode].deactivate()
            return True

    def open_lock(self):
        self.actuators[self.scanned_barcode].activate()
        print(f"set low state on: {self.dict_of_barcodes[self.scanned_barcode]['actuator']}")
        while self.sensors[self.scanned_barcode].read() != 0:
            time.sleep(0.01)
        print(f"set high state on: {self.dict_of_barcodes[self.scanned_barcode]['actuator']}")


def callback(channel):
    print(channel)


def main():

    with open('settings.json') as f:
        dict_of_barcodes = json.load(f)

    GPIO.setmode(GPIO.BCM)

    my_user_info = LEDUserInfo(10)
    bf = BowlFeeder(dict_of_barcodes, GPIOActuator, GPIOSensor, my_user_info)

    while True:
        time.sleep(0.001)

        if bf.is_idle_closed():
            print(f'State: {bf.state}')
            scanned = input('Scan code: ')
            bf.scanning_received()

        if bf.is_barcode_scanned():
            print(f'State: {bf.state}')
            if len(scanned) > 0 and scanned in bf.dict_of_barcodes.keys():
                bf.barcode_ok(scanned)
                bf.user_info.ok(show=True)
            else:
                bf.barcode_nok()
                bf.user_info.nok(show=True)

        if bf.is_cover_state_check():
            print(f'State: {bf.state}')
            if bf.get_covers_closed():
                bf.all_covers_closed()
            else:
                bf.not_all_covers_closed()

        if bf.is_error_info():
            print(f'State: {bf.state}')
            bf.user_info.nok(show=True)
            bf.show_error_info()
            bf.info_shown()

        if bf.is_r_lock_active():
            bf.open_lock()
            if bf.get_is_lock_opened():
                bf.user_info.working(show=True)
                bf.lock_moved_from_base()

        if bf.is_r_lock_deactive():
            if not bf.get_is_lock_opened():
                bf.user_info.clear()
                bf.lock_moved_to_base()


if __name__ == '__main__':
    main()
