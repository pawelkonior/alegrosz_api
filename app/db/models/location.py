from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from app.db.session import Base


class Location(Base):
    """Database model for locations."""
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    capacity = Column(Integer, nullable=False)

    inventory_item = relationship("InventoryItem", back_populates="location", cascade="all, delete")

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id}, name={self.name!r})"
