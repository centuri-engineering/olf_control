import time

from labthings import ActionView, PropertyView, create_app, fields, find_component, op
from labthings.json import encode_json


class ResolutionProperty(PropertyView):

    schema = fields.Tuple(
        (
            fields.Int(required=True, minimum=1, maximum=10000),
            fields.Int(required=True, minimum=1, maximum=10000),
        )
    )

    @op.readproperty
    def get(self):
        # When a GET request is made, we'll find our attached component
        my_component = find_component("org.labthings.example.mycomponent")
        return my_component.resolution

    @op.writeproperty
    def put(self, new_property_value):
        # Find our attached component
        my_component = find_component("org.labthings.example.mycomponent")

        # Apply the new value
        my_component.resolution = new_property_value

        return my_component.resolution


"""
Create a view to start an averaged measurement, and register is as a Thing action
"""


class MeasurementAction(ActionView):
    # Expect JSON parameters in the request body.
    # Pass to post function as dictionary argument.
    args = {
        "averages": fields.Integer(
            missing=20,
            example=20,
            description="Number of images sets to average over",
        )
    }
    # Marshal the response as a list of numbers
    schema = fields.List(fields.Number)

    # Main function to handle POST requests
    @op.invokeaction
    def post(self, args):
        """Start an averaged measurement"""

        # Find our attached component
        my_component = find_component("org.labthings.example.mycomponent")

        # Get arguments and start a background task
        n_averages = args.get("averages")

        # Return the task information
        return my_component.average_data(n_averages)
