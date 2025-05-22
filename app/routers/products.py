from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.product import product_repository
from app.db.session import get_db
from app.schemas.product import ProductCreate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def list_products(
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    if search:
        return product_repository.search(db, search, skip=skip, limit=limit)
    else:
        return product_repository.get_all(db, skip=skip, limit=limit)


@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_repository.create(
        db,
        name=product.name,
        description=product.description,
        price=product.price,
        sku=product.sku,
    )
