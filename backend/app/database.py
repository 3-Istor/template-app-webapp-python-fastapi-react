from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.resolved_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                tagline TEXT NOT NULL,
                description TEXT NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                stock INTEGER NOT NULL,
                image TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total NUMERIC(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar_one()
        if count == 0:
            conn.execute(text("""
                INSERT INTO products (name, tagline, description, price, stock, image)
                VALUES (:name, :tagline, :description, :price, :stock, :image)
            """), {
                "name": "RoomPulse IoT Presence Hub",
                "tagline": "Stop paying for empty meeting rooms.",
                "description": "A smart desk-sized IoT device that checks real room occupation, confirms presence, syncs with calendars and helps teams release no-show bookings automatically.",
                "price": 249.00,
                "stock": 42,
                "image": "/smart-room-badge.png",
            })


def db_health() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
