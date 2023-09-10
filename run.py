from app.api import create_app
from app.data import DiskDataStore

if __name__ == "__main__":
    app = create_app(DiskDataStore())
    app.run()
