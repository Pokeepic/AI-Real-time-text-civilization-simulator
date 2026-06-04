import pickle
import os


SAVE_FOLDER = "saves"
SAVE_FILE = os.path.join(SAVE_FOLDER, "world_save.pkl")


def save_world(sim):
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    with open(SAVE_FILE, "wb") as file:
        pickle.dump(sim, file)


def load_world():
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "rb") as file:
        return pickle.load(file)


def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
