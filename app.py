from labthings import Server

from olf_control.usb_camera.app import create_camera_app

app, labthing = create_camera_app()
Server(app).run()
