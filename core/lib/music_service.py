# Provides an interface for interacting with music services

class MusicService:
    def __init__(self):
        pass

    def login(self, username, password):
        pass

    def logout(self):
        pass

    def get_playlists(self):
        pass

    def play_playlist(self, playlist):
        pass

    def stop_playing(self):
        pass

class FailedLogin(Exception):
    def __init__(self):
        self.expression = ""
        self.message = ""

class NotLoggedIn(Exception):
    def __init__(self):
        self.expression = ""
        self.message = ""
