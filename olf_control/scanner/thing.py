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

    @op.property
    def get(self):
        scanner = find_component("org.centuri.olf.scanner")
        return scanner.axes


class Position(PropertyView):
    schema = fields.List(fields.Float(required=True))

    @op.property
    def get(self):
        scanner = find_component("org.centuri.olf.scanner")
        return scanner.pos

    @op.property
    def put(self, new_pos: List(float)):
        scanner = find_component("org.centuri.olf.scanner")
        scanner.delayed_line(new_pos, relative=False)
        return scanner.pos


class Step(ActionView):
    args = {
        "Axis": fields.String(
            missing="X",
            example="X",
            description="Axis to step over",
        ),
        "step": fields.Float(
            missing=1.0, description="Step size", minimum=0.001, maximum=10.0
        ),
    }

    schema = fields.list(fields.Float)

    def post(self, args):
        """ """
        scanner = find_component("org.centuri.olf.scanner")
        step = args.get("step", 1.0)
        axis = args.get("Axis", "X")
        new_pos = [
            0.0,
        ] * scanner.dim
        try:
            new_pos[scanner.axes.index(axis)] = step
        except ValueError as err:
            raise ValueError(f"Unknown axis, {axis}") from err

        scanner.delayed_line(new_pos, relative=True)
        return scanner.pos
