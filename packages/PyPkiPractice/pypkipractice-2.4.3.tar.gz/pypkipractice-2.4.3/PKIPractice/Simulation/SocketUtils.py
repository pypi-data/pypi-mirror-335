"""
Module used for defining the REST API for the Flask web app.

Global Attributes:
    APP: The flask application to serve.
    APP_DATABASE: The PKIDatabase object that will be creating and passed in.
"""

from waitress import serve
from flask import Flask, send_from_directory  # TODO: Use this send_from_directory at some point
from threading import Event, Thread
from time import sleep
from .DBUtils import PKIDatabase


APP = Flask(__name__, static_folder="../../pki-front-end/dist")
APP_DATABASE = None


@APP.route('/')
def index():
    return "Hello, PKI Python!"


def start_socket() -> None:
    # TODO: Confirm this is the place to listen from
    serve(APP, listen='0.0.0.0:5000')


def start_socket_thread(stop_event: Event, db_folder_path: str = 'pki_database') -> None:
    """
    Sets the database and starts the web server using a separate thread.

    Args:
        stop_event: Event - The event to stop the thread on.
        db_folder_path: str - Where to store the PKIDatabase object contents.
    """
    # Set the database to be the db_object passed in
    global APP_DATABASE
    APP_DATABASE = PKIDatabase(db_folder_path)

    # Start the serving the WGSI application
    server_thread = Thread(name='witness_server', target=start_socket, daemon=True)
    server_thread.start()

    while not stop_event.is_set():
        sleep(1)
