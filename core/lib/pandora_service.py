# Provides an interface to Pandora

import threading
import multiprocessing

from pandora.clientbuilder import SettingsDictBuilder
from pandora.errors import InvalidUserLogin, InternalServerError
from pydora.audio_backend import VLCPlayer

from music_service import MusicService, FailedLogin, NotLoggedIn

# A class to interface with Pandora
# Uses Pydora to connect to the Pandora API
class PandoraService(MusicService):

    # Initializes the Pandora service by creating an APIClient
    def __init__(self):
        self.player = None

        # The following code is from https://pypi.python.org/pypi/pydora
        self.client = SettingsDictBuilder({
            'DECRYPTION_KEY': 'R=U!LH$O2B#',
            'ENCRYPTION_KEY': '6#26FRL$ZWD',
            'PARTNER_USER': 'android',
            'PARTNER_PASSWORD': 'AC7IBG09A3DTSYM4R41UJWL07VLN8JI7',
            'DEVICE': 'android-generic'
        }).build()

    # Log in to Pandora
    # Raises a FailedLogin exception if login was unsuccessful
    def login(self, username, password):
        try:
            self.client.login(username, password)
        except InvalidUserLogin:
            raise FailedLogin()

    # Returns the stations as a dictionary, with the station token as the key
    # and the station name as the value
    def get_playlists(self):
        station_list = {}
        try:
            for station_id, station in self.client.get_station_list().items():
                station_list[station_id] = station.name
        except InternalServerError:
            raise NotLoggedIn()

        return station_list

    # Starts playing the given station
    # Takes the station token as the id
    def play_playlist(self, playlist_id):
        station = self.client.get_station(playlist_id)
        self.player = StationPlayer(station)
        self.player.start()

    # Stops playing the current station
    def stop_playing(self):
        self.player.stop()

# A wrapper class for controlling a VLCPlayer object
class StationPlayer(threading.Thread):

    # Initializes the player with a given station
    def __init__(self, station):
        self.station = station
        self.comm = VLCPlayerCommunicator()
        self.player = VLCPlayer(self, self.comm)
        self.stop_event = threading.Event()
        super(StationPlayer, self).__init__()

    # The runtime behavior of the thread
    # Does not return until self.stop is called 
    def run(self):
        self.stop_event.clear()
        self.player.start()
        while not self.stop_event.is_set():
            self.player.play_station(self.station)

    # Stops playback and ends the thread
    def stop(self):
        self.stop_event.set()
        self.comm.sendline('Q\n')

    # Required callback for the VLCPlayer
    def play(self, song):
        pass

    # Required callback for the VLCPlayer
    def pre_poll(self):
        pass

    # Required callback for the VLCPlayer
    def post_poll(self):
        pass

    # Required callback for the VLCPlayer
    # Catches input from VLCPlayer's stdin to control the player
    def input(self, value, song):
        if value == "Q":
            self.player.end_station()

# A class to spoof stdin for VLCPlayer by providing fileno and readline methods
class VLCPlayerCommunicator:

    # Initializes the underlying pipe for communication
    def __init__(self):
        self.receiver, self.sender = multiprocessing.Pipe(duplex=False)

    # Returns the file number of the receiver
    def fileno(self):
        return self.receiver.fileno()

    # Reads any object from the underlying pipe
    def readline(self):
        return self.receiver.recv()

    # Sends an object across the pipe
    def sendline(self, line):
        self.sender.send(line)
