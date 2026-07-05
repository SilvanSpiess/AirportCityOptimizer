import json
import sys
import os

HOUSE = {
      "empty" :                { "passengers":   0, "time":    0, "size": 1 },
      "visa" :                 { "passengers":   0, "time":    0, "size": 1 },
      "road" :                 { "passengers":   0, "time":    0, "size": 1 },
      "tree" :                 { "passengers":   0, "time":    0, "size": 1 },
      "cottage" :              { "passengers":   1, "time":    1, "size": 1 },
      "side_wing" :            { "passengers":   2, "time":    2, "size": 1 },
      "townhouse" :            { "passengers":   8, "time":   10, "size": 1 },
      "futuristic_house" :     { "passengers":   8, "time":   20, "size": 1 },
      "brickhouse" :           { "passengers":   5, "time":    2, "size": 1 },
      "mansion" :              { "passengers":  12, "time":   20, "size": 2 },
      "stone_castle" :         { "passengers":  36, "time":   60, "size": 2 },
      "manor" :                { "passengers":   9, "time":   15, "size": 2 },
      "house_with_pool" :      { "passengers":  18, "time":   60, "size": 2 },
      "villa" :                { "passengers":  48, "time":  240, "size": 2 },
      "country_house" :        { "passengers":  24, "time":  240, "size": 2 },
      "studio" :               { "passengers":  36, "time":  480, "size": 2 },
      "bearing_Wall_house" :   { "passengers":  48, "time": 1080, "size": 2 },
      "round_house" :          { "passengers":  57, "time": 1440, "size": 2 },
      "tower_building" :       { "passengers":  63, "time": 2880, "size": 2 },
      "loft" :                 { "passengers":  72, "time": 1440, "size": 2 },
      "square_house" :         { "passengers":  57, "time":  480, "size": 2 },
      "mirror_house" :         { "passengers":  96, "time":  720, "size": 2 },
      "emerald_house" :        { "passengers":  99, "time":  720, "size": 2 },
      "modular_house" :        { "passengers":  67, "time":  360, "size": 2 },
      "acute_house" :          { "passengers": 102, "time":  720, "size": 2 },
      "apartment_hotel" :      { "passengers": 300, "time": 2880, "size": 2 },
      "apartment_house" :      { "passengers":  60, "time":  240, "size": 2 },
      "smart_house" :          { "passengers":  18, "time":   30, "size": 2 },
      "house_of_disturbance" : { "passengers":  85, "time": 1200, "size": 2 },
      "fall_mansion" :         { "passengers":   9, "time":    5, "size": 2 },
      "rural_life_restaurant": { "passengers":  10, "time":   10, "size": 2 },
      "turf_house" :           { "passengers":   3, "time":    5, "size": 2 },
      "multistory_building" :  { "passengers":  56, "time":  240, "size": 3 },
      "loft_condominium" :     { "passengers":  96, "time":  480, "size": 3 },
      "condominium" :          { "passengers": 190, "time": 1440, "size": 3 },
   }

ICON_FILE_NAME = "resources/Airport_City_Logo.ico"
HOUSES_FILE_NAME = "resources/houses.json"
GIF_FILE_NAME = "resources/loading.gif"

IMAGE_DIR = "resources/images"

EXCLUDE_KEYS = {"empty", "visa", "road", "tree"}

ACTIVE_STYLESHEET = "color: #00ffcc; font-weight: bold; font-size: 16px; margin-bottom: 5px; margin-top: 5px; margin-left: 5px; margin-right: 5px;"

INACTIVE_STYLESHEET = "color: #808588; font-weight: bold; font-size: 16px; margin-bottom: 5px; margin-top: 5px; margin-left: 5px; margin-right: 5px;"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def save_houses(data, fname):
    """Writes the dictionary to a JSON file."""
    filename = resource_path(fname)
    with open(resource_path(filename), "w", encoding="utf-8") as f:
        # indent=4 makes the JSON pretty-printed and easy to read manually
        json.dump(data, f, indent=4)
    print(f"INFO - Successfully saved data to {filename}")


def load_houses(fname):
    """Reads the JSON file and returns it as a Python dictionary."""
    filename = resource_path(fname)
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"INFO - Successfully loaded data from {filename}")
        return data
    except FileNotFoundError:
        print(f"WARN - The file {filename} does not exist.")
        print(f"INFO - Creating new default one...")
        save_houses(HOUSE, HOUSES_FILE_NAME)
        print(f"INFO - New default {filename} created.")
        return None
