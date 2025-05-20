from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.product import Product


class ProductRepository:
    @staticmethod
    def get(db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Product | None:
        return db.query(Product).filter(Product.sku == sku).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[type[Product]]:
        return db.query(Product).offset(skip).limit(limit).all()

    @staticmethod
    def search(db: Session, term: str, skip: int = 0, limit: int = 100) -> list[type[Product]]:
        return db.query(Product).filter(
            or_(
                Product.name.ilike(f"%{term}%"),
                Product.description.ilike(f"%{term}%"),
                Product.sku.ilike(f"%{term}%")
            )
        ).offset(skip).limit(limit).all()

    @staticmethod
    def filter_by_price(db: Session, min_price: float | None = None, max_price: float | None = None, skip: int = 0,
                        limit: int = 100) -> list[type[Product]]:
        query = db.query(Product)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, name: str, description: str, sku: str, price: float) -> Product:
        product = Product(name=name, description=description, sku=sku, price=price)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        product = ProductRepository.get(db, product_id)
        if not product:
            return False

        db.delete(product)
        db.commit()
        return True

    @staticmethod
    def update(
            db: Session,
            product_id: int,
            name: str | None = None,
            description: str | None = None,
            sku: str | None = None,
            price: float | None = None) -> Product | None:
        product = ProductRepository.get(db, product_id)
        if not product:
            return None

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if sku is not None:
            product.sku = sku
        if price is not None:
            product.price = price

        db.add(product)
        db.commit()
        db.refresh(product)
        return product
