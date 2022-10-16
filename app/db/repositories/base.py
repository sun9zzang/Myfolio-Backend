from app.db.session import db


class BaseRepository:

    def __init__(self):
        self.get_session = db.get_session
