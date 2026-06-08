from decimal import Decimal
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import db_health, get_db, init_db

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    customer_email: EmailStr
    quantity: int = Field(ge=1, le=10)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root():
    return {"message": "RoomPulse Store API", "env": settings.app_env}


@app.get("/api/status")
def status():
    return {
        "app": settings.app_name,
        "database": db_health(),
        "secret_loaded": settings.secret_key != "dev-secret",
        "currency": settings.shop_currency,
    }


@app.get("/api/products")
def products(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM products ORDER BY id")).mappings().all()
    return [{**dict(row), "price": float(row["price"])} for row in rows]


@app.get("/api/orders")
def orders(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, customer_name, customer_email, quantity, total, created_at FROM orders ORDER BY id DESC LIMIT 8")).mappings().all()
    return [{**dict(row), "total": float(row["total"]), "created_at": row["created_at"].isoformat()} for row in rows]


@app.post("/api/checkout")
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), x_demo_secret: str | None = Header(default=None)):
    if x_demo_secret != settings.secret_key:
        raise HTTPException(status_code=401, detail="Invalid demo secret")

    product = db.execute(text("SELECT id, price, stock FROM products LIMIT 1")).mappings().one()
    if product["stock"] < payload.quantity:
        raise HTTPException(status_code=409, detail="Not enough stock")

    total = Decimal(product["price"]) * payload.quantity
    order = db.execute(text("""
        INSERT INTO orders (customer_name, customer_email, quantity, total)
        VALUES (:name, :email, :quantity, :total)
        RETURNING id, customer_name, customer_email, quantity, total, created_at
    """), {
        "name": payload.customer_name,
        "email": payload.customer_email,
        "quantity": payload.quantity,
        "total": total,
    }).mappings().one()
    db.execute(text("UPDATE products SET stock = stock - :quantity WHERE id = :id"), {"quantity": payload.quantity, "id": product["id"]})
    db.commit()
    return {**dict(order), "total": float(order["total"]), "created_at": order["created_at"].isoformat()}
