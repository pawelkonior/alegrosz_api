from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db.models.inventory import InventoryItem
from app.db.models.location import Location


class LocationRepository:
    @staticmethod
    def get(db: Session, location_id: int) -> Location | None:
        """Get a location by ID"""
        return db.query(Location).filter(Location.id == location_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[type[Location]]:
        """Get all locations with pagination"""
        return db.query(Location).offset(skip).limit(limit).all()

    @staticmethod
    def search(db: Session, term: str, skip: int = 0, limit: int = 100) -> list[type[Location]]:
        """Search locations by name or address"""
        return db.query(Location).filter(
            or_(
                Location.name.ilike(f"%{term}%"),
                Location.address.ilike(f"%{term}%")
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_with_stock_count(db: Session, location_id: int) -> tuple[Location, int] | None:
        """
        Get a location with its current total stock count
        Returns tuple of (location, total_stock) or None if location not found
        """
        location = LocationRepository.get(db, location_id)
        if not location:
            return None

        stock_count = (
            db.query(func.coalesce(func.sum(InventoryItem.quantity), 0))
            .filter(InventoryItem.location_id == location_id)
            .scalar()
        )

        return location, stock_count

    @staticmethod
    def get_all_with_stock_counts(db: Session, skip: int = 0, limit: int = 100) -> list[tuple[Location, int]]:
        """
        Get all locations with their stock counts
        Returns list of tuples: [(location1, stock1), (location2, stock2), ...]
        """
        locations = LocationRepository.get_all(db, skip=skip, limit=limit)

        if not locations:
            return []

        location_ids = [loc.id for loc in locations]

        stock_subquery = (
            db.query(
                InventoryItem.location.id,
                func.coalesce(func.sum(InventoryItem.quantity), 0).label("total_stock")
            )
            .filter(InventoryItem.location_id.in_(location_ids))
            .group_by(InventoryItem.location_id)
            .subquery()
        )

        stock_counts = {}
        for row in db.query(stock_subquery).all():
            stock_counts[row.location_id] = row.total_stock

        result = []
        for location in locations:
            stock = stock_counts.get(location.id, 0)
            result.append((location, stock))

        return result

    @staticmethod
    def create(db: Session, name: str, address: str, capacity: int) -> Location:
        """Create a new location"""
        location = Location(name=name, address=address, capacity=capacity)
        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def update(db: Session, location_id: int,
               name=None,
               address=None,
               capacity=None) -> Location | None:
        """Update a location"""
        location = LocationRepository.get(db, location_id)

        if not location:
            return None

        if name is not None:
            location.name = name
        if address is not None:
            location.address = address
        if capacity is not None:
            location.capacity = capacity

        db.add(location)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def delete(db: Session, location_id: int) -> bool:
        """Delete a location"""
        location = LocationRepository.get(db, location_id)
        if not location:
            return False

        db.delete(location)
        db.commit()
        return True


location_repository = LocationRepository()
