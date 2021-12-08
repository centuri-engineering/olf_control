import datetime
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import List

import serial

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


@dataclass
class Configuration:
    axes: str = "XY"
    origin: List[float] = field(default_factory=lambda: [0.0, 0.0])
    # /dev/ttyACM0 (Joy-it), /dev/ttyUSB0 (original board)
    board_path: str = "/dev/ttyACM0"
    baudrate: int = 115200
    # Motor speed & accelaration
    max_rate_min: float = 4000.0
    max_rate_s: float = max_rate_min / 60
    max_acc: float = 500.0
    # Considering acceleration and deceleration phases (hence *2):
    time_acc: float = (max_rate_s / max_acc) * 2
    dist_acc: float = max_rate_s * time_acc
    delay_for_action: float = 0.01


class MockSerial:
    def __init__(self, board_path, baudrate):
        self.board_path = board_path
        self.baudrate = baudrate
        self.messages = []
        self.in_waiting = 0

    def write(self, msg):
        """Sends message to logger and returns it"""
        log.info("Write to serial %s", msg.decode("utf-8"))
        self.messages.append(msg)
        return msg

    def readline(self):
        """Always ok"""
        return b"ok\r\n"


class Motors:
    """Base class for a GCODE-based  motorized stage"""

    def __init__(self, conf):
        try:
            self.serial = serial.Serial(conf.board_path, conf.baudrate)
        except serial.SerialException:
            self.serial = MockSerial(conf.board_path, conf.baudrate)

        self.conf = conf
        self.axes = conf.axes
        self.dim = len(conf.axes)
        self.pos = [
            0.0,
        ] * self.dim
        self.homing()
        # Move to origin
        self.delayed_line(self.conf.origin)
        self.set_origin()
        self.scanning = False
        self.moving = False

    def serial_com_check(self):
        """Reads the receceived data from grbl."""
        # Wait for the data to be received

        while self.serial.in_waiting != 0:
            theline = self.serial.readline()
            log.debug("- Message received - %s ", theline.decode("utf-8"))
            if theline == b"ALARM:1\r\n":
                msg = """Endstop triggered, re-establishing contact."""
                log.error(msg)
                self.serial.close()
                self.serial.open()
                time.sleep(2)
            time.sleep(0.001)

    def set_origin(self):
        """Sets the present position to X=0, Y=0 (and Z0)"""

        coords_0 = " ".join((f"{C}0" for C in self.axes))
        self.serial.write(f"G92 {coords_0}\r\n".encode())
        self.pos = [
            0.0,
        ] * self.dim
        self.serial_com_check()

    def homing(self):
        """Places the XY stage head at the home position."""

        log.info("Waiting until serial communication is working.")
        self.serial_com_check()
        log.info("Serial communication working.")
        self.serial.write(b"$h\r\n")
        while self.serial.readline() != b"ok\r\n":
            log.debug("Waiting until the homing is done.")
            self.serial_com_check()

        log.info("Waiting until the homing is done.")
        self.serial_com_check()
        log.info("Homing done.")
        self.pos = [-coord for coord in self.conf.origin]

    def simple_line(self, vector, relative=True):
        """Send a simple GCODE line with X and Y (and maybe Z) coords to grbl.

        If `relative` is True, the line is relative to curent position.
        """
        if relative:
            self.serial.write(b"G91 \r\n")
        self.serial_com_check()
        line = " ".join(
            f"G0 {C}{coord} " for C, coord in zip(self.axes, vector)
        ).encode()
        self.serial.write(line)
        self.serial_com_check()
        self.serial.write(b"G90 \r\n")
        self.serial_com_check()
        if relative:
            self.pos = [old_coord + coord for old_coord, coord in zip(self.pos, vector)]
        else:
            self.pos = vector

    def delayed_line(self, new_pos, relative=True):
        """Move to new_pos from prev_pos and sleep while the motor moves.

        if relative is True, prev_pos is taken as the current position, and that
        argument has no effect. If prev_pos is not passed, relative is set to True
        Assumes all axial movements are done at the same speed
        """
        self.simple_line(new_pos, relative=relative)
        self.moving = True
        time.sleep(self.travel_time(new_pos, relative=relative))
        self.moving = False

    def travel_time(self, new_pos, relative=True):
        """Returns an approximate travel time to new_pos (in seconds)

        If relative is True, computes the travel time from the current position
        """
        if relative:
            travel = sum([new ** 2 for new in new_pos]) ** 0.5
        else:
            travel = (
                sum([(new - old) ** 2 for new, old in zip(new_pos, self.pos)]) ** 0.5
            )

        dist_acc = self.conf.dist_acc
        max_rate_s = self.conf.max_rate_s
        time_acc = self.conf.time_acc
        delay = self.conf.delay_for_action

        if travel < dist_acc:
            return time_acc + delay
        else:
            return time_acc + (travel - dist_acc) / max_rate_s + delay
