from labthings import create_app

from .things import Configuration, Motors
from .views import Axes, Position, Step


def create_motors_app():
    # Create LabThings Flask app
    app, labthing = create_app(
        __name__,
        title="USB camera app (test)",
        description="Test LabThing-based API",
        version="0.1.0",
    )
    conf = Configuration()
    # Attach an instance of our component
    # Usually a Python object controlling some piece of hardware
    motors = Motors(conf)
    labthing.add_component(motors, "org.centuri.olf.motors")

    # Add routes for the API views we created
    labthing.add_view(Axes, "/axes")
    labthing.add_view(Position, "/position")
    labthing.add_view(Step, "/actions/step")

    return app, labthing


# Start the app
if __name__ == "__main__":
    from labthings import Server

    app, labthing = create_motors_app()
    Server(app).run()
