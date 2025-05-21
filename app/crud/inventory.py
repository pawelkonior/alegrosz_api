from typing import Any

from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.db.models.inventory import InventoryItem
from app.db.models.product import Product
from app.db.models.location import Location


class InventoryRepository:
    @staticmethod
    def get(db: Session, product_id: int, location_id: int) -> InventoryItem | None:
        """Get inventory item by product_id and location_id"""
        return (
            db.query(InventoryItem)
            .filter(
                and_(
                    InventoryItem.product_id == product_id,
                    InventoryItem.location_id == location_id)
            ).first()
        )

    @staticmethod
    def get_by_product(db: Session, product_id: int) -> list[Row[tuple[InventoryItem, Location]]]:
        """
        Get all inventory items for a specific product with location information
        Returns list of tuples: [(inventory_item1, location1), (inventory_item2, location2), ...]
        """
        return (
            db.query(InventoryItem, Location)
            .join(Location, InventoryItem.location_id == Location.id)
            .filter(InventoryItem.product_id == product_id)
            .all()
        )

    @staticmethod
    def get_by_location(db: Session, location_id: int) -> list[Row[tuple[InventoryItem, Product]]]:
        """
        Get all inventory items at a specific location with product information
        Returns list of tuples: [(inventory_item1, product1), (inventory_item2, product2), ...]
        """
        return (
            db.query(InventoryItem, Product)
            .join(Product, InventoryItem.product_id == Product.id)
            .filter(InventoryItem.location_id == location_id)
            .all()
        )

    @staticmethod
    def get_low_stock_items(db: Session) -> list[Row[tuple[InventoryItem, Product, Location]]]:
        """
        Get inventory items with quantity below reorder point
        Returns list of tuples: [(inventory_item1, product1, location1), ...]
        """
        return (
            db.query(InventoryItem, Product, Location)
            .join(Product, InventoryItem.product_id == Product.id)
            .join(Location, InventoryItem.location_id == Location.id)
            .filter(InventoryItem.quantity < InventoryItem.reorder_point)
            .all()
        )

    @staticmethod
    def get_total_quantity_by_product(db: Session, product_id: int) -> int:
        """Get total quantity of a product across all locations"""
        result = (
            db.query(func.coalesce(func.sum(InventoryItem.quantity), 0))
            .filter(InventoryItem.product_id == product_id)
            .scalar()
        )

        return result or 0

    @staticmethod
    def update_stock(db: Session, product_id: int, location_id: int,
                     quantity_change: int, reorder_point: int | None = None) -> InventoryItem | None:
        """
        Update stock quantity by adding or removing (if negative) the specified amount
        Optionally update the reorder point
        Creates the inventory item if it doesn't exist and quantity_change is positive
        Returns None if:
          - Item doesn't exist and quantity_change is negative
          - Item exists but would have negative quantity after change
        """
        inventory_item = InventoryRepository.get(db, product_id, location_id)
        if not inventory_item:
            if quantity_change <= 0:
                return None

            inventory_item = InventoryItem(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity_change,
                reorder_point=reorder_point
            )
        else:
            if inventory_item.quantity + quantity_change < 0:
                return None

            inventory_item.quantity += quantity_change

            if reorder_point is not None:
                inventory_item.reorder_point = reorder_point

        db.add(inventory_item)
        db.commit()
        db.refresh(inventory_item)
        return inventory_item

    @staticmethod
    def set_stock(db: Session, product_id: int, location_id: int,
                  quantity: int, reorder_point: int | None = None) -> InventoryItem | None:
        """
        Set absolute stock quantity and optionally the reorder point
        Creates the inventory item if it doesn't exist
        """
        if quantity < 0:
            return None

        inventory_item = InventoryRepository.get(db, product_id, location_id)

        if not inventory_item:
            inventory_item = InventoryItem(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity,
                reorder_point=reorder_point
            )
        else:
            inventory_item.quantity = quantity

            if reorder_point is not None:
                inventory_item.reorder_point = reorder_point

        db.add(inventory_item)
        db.commit()
        db.refresh(inventory_item)
        return inventory_item

    @staticmethod
    def delete(db: Session, product_id: int, location_id: int) -> bool:
        """Delete an inventory item (used for administrative purposes only)"""
        inventory_item = InventoryRepository.get(db, product_id, location_id)

        if not inventory_item:
            return False

        db.delete(inventory_item)
        db.commit()
        return True


inventory_repository = InventoryRepository()
