import json
import time

from labthings import ActionView, PropertyView, fields, find_component, op
from labthings.deque import Deque
from labthings.json import encode_json

from .utilities import ndarray_to_json


class ResolutionProperty(PropertyView):

    schema = fields.List(fields.Int(required=True, minimum=1, maximum=10000))
    # args = {
    #     "width": fields.Integer(
    #         missing=640, example=640, description="Number of images to average over",
    #     ),
    #     "height": fields.Integer(
    #         missing=480, example=480, description="Number of images to average over",
    #     ),
    # }

    @op.readproperty
    def get(self):
        # When a GET request is made, we'll find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        return camera.resolution

    @op.writeproperty
    def put(self, args):
        # Find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        print("args:", args)
        width, height = args
        # Apply the new value
        print(f"setting resolution to ({(width, height)})")
        camera.resolution = (width, height)

        return camera.resolution


"""
Create a view to start an averaged measurement, and register is as a Thing action
"""


class AquireAverage(ActionView):
    # Expect JSON parameters in the request body.
    # Pass to post function as dictionary argument.
    args = {
        "averages": fields.Integer(
            missing=20,
            example=20,
            description="Number of images to average over",
        )
    }
    # Marshal the response as a string representation of the array
    schema = fields.String()
    # Use a smaller deque than the default of length 100
    # TODO - see https://github.com/labthings/python-labthings/issues/300
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self._deque = Deque(maxlen=10)

    # # def __init_subclass__(cls):
    # #     cls._deque = Deque(maxlen=10)  # Action queue

    # Main function to handle POST requests

    @op.invokeaction
    def post(self, args):
        """Start an averaged measurement"""
        # Find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        print("deque length", len(self._deque))
        # Get arguments and start a background task
        n_averages = args.get("averages")
        # Acquire the images
        data = camera.average(n_averages)
        return json.dumps(ndarray_to_json(data))
