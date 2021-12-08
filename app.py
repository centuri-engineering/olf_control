from labthings import Server

from olf_control.motors.app import create_motors_app

app, labthing = create_motors_app()
Server(app).run()
