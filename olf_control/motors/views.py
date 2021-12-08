"""Single GCODE controled stepper motor
"""

import json
import logging
import time
from typing import List

from labthings import ActionView, PropertyView, fields, find_component, op
from labthings.deque import Deque
from labthings.json import encode_json

log = logging.getLogger(__name__)


class Axes(PropertyView):

    schema = fields.String(required=True)

    @op.readproperty
    def get(self):
        motors = find_component("org.centuri.olf.motors")
        return motors.axes


class Position(PropertyView):
    schema = fields.List(fields.Float(required=True))

    @op.readproperty
    def get(self):
        motors = find_component("org.centuri.olf.motors")
        return motors.pos

    @op.writeproperty
    def put(self, new_pos: List[float]):
        motors = find_component("org.centuri.olf.motors")
        motors.delayed_line(new_pos, relative=False)
        return motors.pos


class Step(ActionView):
    args = {
        "axis": fields.String(
            missing="X",
            example="X",
            description="Axis to step over",
        ),
        "step": fields.Float(
            missing=1.0, description="Step size", minimum=0.001, maximum=10.0
        ),
    }

    schema = fields.List(fields.Float)

    @op.invokeaction
    def post(self, args):
        """ """
        motors = find_component("org.centuri.olf.motors")
        step = args.get("step", 1.0)
        axis = args.get("axis", "X")
        new_pos = [
            0.0,
        ] * motors.dim
        try:
            new_pos[motors.axes.index(axis)] = step
        except ValueError as err:
            raise ValueError(f"Unknown axis, {axis}") from err

        motors.delayed_line(new_pos, relative=True)
        return motors.pos
