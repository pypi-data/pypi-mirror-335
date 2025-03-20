import os
import dotenv

DATA_ENV_FILE = os.getenv("DATA_ENV_FILE", "../.env.data")

dotenv.load_dotenv(DATA_ENV_FILE)

BUILDING_AREA = os.environ["BUILDING_AREA"]
GADM = os.environ["GADM"]
POPULATION = os.environ["POPULATION"]
OPEN_BUILDINGS = os.environ["OPEN_BUILDINGS"]
NSI = os.environ["NSI"]