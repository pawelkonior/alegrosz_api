import json
import sys
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

import config
from app.db import init_db, engine, Base
from app.db.models.inventory import InventoryItem
from app.db.models.location import Location
from app.db.models.product import Product
from app.db.session import get_db


def check_database_exists():
    try:
        with engine.connect() as conn:
            inspector = sa.inspect(engine)
            has_tables = inspector.get_table_names()
            return bool(has_tables)
    except SQLAlchemyError:
        return False


def init_database(force_recreate=False):
    db_exists = check_database_exists()

    if db_exists:
        if force_recreate:
            Base.metadata.drop_all(bind=engine)
            print("Tables dropped successfully.")
        else:
            print("Database already exists.")
            return False

    print("Creating database tables...")
    init_db()
    print("Tables created successfully.")
    return True


def load_sample_data():
    file_path = Path(config.ROOT_DIR) / "fixtures" / "sample_data.json"
    print(file_path)

    if not file_path.exists():
        raise FileNotFoundError("Sample data file not found.")

    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)

    db_generator = get_db()
    db = next(db_generator)

    for product in data["products"]:
        db.add(Product(**product))
        db.flush()

    for location in data["locations"]:
        db.add(Location(**location))
        db.flush()

    for inventory in data["inventory"]:
        db.add(InventoryItem(**inventory))
        db.flush()

    db.commit()
    print("Sample data loaded successfully.")


if __name__ == "__main__":
    if "--load-sample-data" in sys.argv:
        load_sample_data()
    elif "--init-db" in sys.argv:
        force = "--force" in sys.argv
        init_database(force)
