from labthings import create_app, Server


from olf_control.usb_camera.things import USBCamera
from olf_control.usb_camera.views import AquireAverage, ResolutionProperty
from olf_control.motors.things import Configuration, Motors
from olf_control.motors.views import Axes, Position, Step


def create_olf_app():
    # Create LabThings Flask app
    app, labthing = create_app(
        __name__,
        title="USB camera app (test)",
        description="Test LabThing-based API",
        version="0.1.0",
    )
    conf = Configuration()
    motors = Motors(conf)
    labthing.add_component(motors, "org.centuri.olf.motors")

    # Add routes for the API views we created
    labthing.add_view(Axes, "/axes")
    labthing.add_view(Position, "/position")
    labthing.add_view(Step, "/actions/step")

    my_camera = USBCamera()
    labthing.add_component(my_camera, "org.centuri.olf.usb_camera")

    # Add routes for the API views we created
    labthing.add_view(ResolutionProperty, "/resolution")
    labthing.add_view(AquireAverage, "/actions/average")
    return app, labthing


app, labthing = create_olf_app()
Server(app).run()
