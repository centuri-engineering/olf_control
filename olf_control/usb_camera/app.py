"""Standalone  app for a USB camera
"""

from labthings import create_app

from .thing import AquireAverage, ResolutionProperty
from .usb_camera import USBCamera


def create_camera_app():
    # Create LabThings Flask app
    app, labthing = create_app(
        __name__,
        title="USB camera app (test)",
        description="Test LabThing-based API",
        version="0.1.0",
    )

    # Attach an instance of our component
    # Usually a Python object controlling some piece of hardware
    my_camera = USBCamera()
    labthing.add_component(my_camera, "org.centuri.olf.usb_camera")

    # Add routes for the API views we created
    labthing.add_view(ResolutionProperty, "/resolution")
    labthing.add_view(AquireAverage, "/actions/average")

    return app, labthing


# Start the app
if __name__ == "__main__":
    from labthings import Server

    app, labthing = create_camera_app()
    Server(app).run()
