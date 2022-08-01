import logging

from app import App
from db import Mongo

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    db = Mongo()
    app = App(db)
    app.run()
