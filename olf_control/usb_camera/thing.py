import json
import time
from typing import List

from labthings import ActionView, PropertyView, fields, find_component, op
from labthings.deque import Deque
from labthings.json import encode_json

from ..utilities import ndarray_to_json


class ResolutionProperty(PropertyView):
    """This class defines a resolution property that can be get or set
    through the app REST API

    For exemple:

    .. code:: python
        import requests
        # get the resolution
        req = requests.get("http://localhost:7485/resolution")
        print(req.json())
        # set the resolution
        req = requests.put("http://localhost:7485/resolution", json=[800, 600])
    """

    schema = fields.List(fields.Int(required=True, minimum=1, maximum=10000))

    @op.readproperty
    def get(self):
        """Retrieves the plugged camera's resolution"""
        camera = find_component("org.centuri.olf.usb_camera")
        return camera.resolution

    @op.writeproperty
    def put(self, args: List[int]):
        """Sets the plugged camera's resolution"""
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
    """This action allows to get an image averaged over a certain number of acquitions"""

    args = {
        "averages": fields.Integer(
            missing=1,
            example=20,
            description="Number of images to average over",
        )
    }
    # Marshal the response as a string representation of the array
    schema = fields.String()
    # Main function to handle POST requests

    @op.invokeaction
    def post(self, args):
        """Start an averaged measurement"""
        # Find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        # Get arguments and start a background task
        n_averages = args.get("averages")
        # Acquire the images
        data = camera.average(n_averages)
        return json.dumps(ndarray_to_json(data))
