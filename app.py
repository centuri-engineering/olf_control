from labthings import Server

from olf_control.things.camera_app import create_camera_app

app, labthing = create_camera_app()
Server(app).run()
