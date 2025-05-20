from sqlalchemy.orm import Session

from app.db.models import product, location, inventory
from app.db.session import Base, engine

def init_db():
    Base.metadata.create_all(bind=engine)