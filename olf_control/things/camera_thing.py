import json
import time

from labthings import ActionView, PropertyView, fields, find_component, op
from labthings.json import encode_json

from .utilities import ndarray_to_json


class ResolutionProperty(PropertyView):

    schema = fields.List(fields.Int(required=True, minimum=1, maximum=10000))

    @op.readproperty
    def get(self):
        # When a GET request is made, we'll find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        return camera.resolution

    @op.writeproperty
    def put(self, new_property_value):
        # Find our attached component
        camera = find_component("org.centuri.olf.usb_camera")
        # Apply the new value
        camera.resolution = new_property_value
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

    # Main function to handle POST requests
    @op.invokeaction
    def post(self, args):
        """Start an averaged measurement"""
        # Find our attached component
        camera = find_component("org.centuri.olf.usb_camera")

        # Get arguments and start a background task
        n_averages = args.get("averages")
        # Return the task information
        return json.dumps(ndarray_to_json(camera.average(n_averages)))
