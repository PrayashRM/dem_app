"""
Seed Script — Product Management System
════════════════════════════════════════
Creates the default admin user and sample products on first run.
Safe to run multiple times — fully idempotent.

Usage:
    python scripts/seed.py
"""

import sys
import os

# ── Path fix so script can import from app/ ───────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.database.db import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.product import Product
from app.core.security import hash_password
import uuid
import logging

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ── Seed Data ─────────────────────────────────────────────────────────────────

ADMIN_USER = {
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "Admin123",
    "role": UserRole.ADMIN,
    "is_active": True
}

REGULAR_USER = {
    "email": "user@example.com",
    "full_name": "Regular User",
    "password": "User1234",
    "role": UserRole.USER,
    "is_active": True
}

SAMPLE_PRODUCTS = [
    {
        "name": "Wireless Noise-Cancelling Headphones",
        "description": "Premium over-ear headphones with active noise cancellation, 30-hour battery life, and foldable design.",
        "price": 299.99,
        "stock": 45,
        "category": "Electronics"
    },
    {
        "name": "Mechanical Keyboard",
        "description": "Tenkeyless mechanical keyboard with Cherry MX switches, RGB backlighting, and PBT keycaps.",
        "price": 149.99,
        "stock": 30,
        "category": "Electronics"
    },
    {
        "name": "Ergonomic Office Chair",
        "description": "Fully adjustable ergonomic chair with lumbar support, breathable mesh back, and 4D armrests.",
        "price": 549.99,
        "stock": 12,
        "category": "Furniture"
    },
    {
        "name": "Standing Desk",
        "description": "Electric height-adjustable standing desk with memory presets, cable management, and solid wood top.",
        "price": 799.99,
        "stock": 8,
        "category": "Furniture"
    },
    {
        "name": "4K Webcam",
        "description": "Ultra HD webcam with autofocus, built-in ring light, noise-cancelling microphone, and wide-angle lens.",
        "price": 199.99,
        "stock": 25,
        "category": "Electronics"
    },
    {
        "name": "USB-C Hub 12-in-1",
        "description": "Multiport USB-C hub with 4K HDMI, 100W PD, SD card reader, Ethernet, and 4 USB ports.",
        "price": 79.99,
        "stock": 60,
        "category": "Electronics"
    },
    {
        "name": "Leather Laptop Bag",
        "description": "Premium full-grain leather laptop bag fits up to 15.6 inch laptops with padded compartments.",
        "price": 129.99,
        "stock": 20,
        "category": "Accessories"
    },
    {
        "name": "Wireless Charging Pad",
        "description": "15W fast wireless charging pad compatible with Qi devices, with LED indicator and anti-slip base.",
        "price": 39.99,
        "stock": 75,
        "category": "Electronics"
    },
    {
        "name": "Portable Monitor 15.6 inch",
        "description": "Full HD IPS portable monitor with USB-C and mini HDMI, built-in speakers, and protective case.",
        "price": 249.99,
        "stock": 15,
        "category": "Electronics"
    },
    {
        "name": "Desk Lamp with Wireless Charger",
        "description": "LED desk lamp with adjustable color temperature, brightness levels, and integrated 10W wireless charger.",
        "price": 69.99,
        "stock": 35,
        "category": "Accessories"
    }
]


# ── Seed Functions ────────────────────────────────────────────────────────────

def seed_user(db: Session, user_data: dict) -> tuple[User, bool]:
    """
    Create a user if they do not already exist.
    Returns (user, created) tuple.
    created = True if newly inserted, False if already existed.
    """
    existing = db.query(User).filter(
        User.email == user_data["email"]
    ).first()

    if existing:
        return existing, False

    user = User(
        id=str(uuid.uuid4()),
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=hash_password(user_data["password"]),
        role=user_data["role"],
        is_active=user_data["is_active"]
    )

    db.add(user)
    db.flush()  # flush to get the ID before commit
    return user, True


def seed_products(db: Session, admin_user: User) -> tuple[int, int]:
    """
    Create sample products if they do not already exist.
    Checks by product name to avoid duplicates.
    Returns (created_count, skipped_count) tuple.
    """
    created = 0
    skipped = 0

    for product_data in SAMPLE_PRODUCTS:
        existing = db.query(Product).filter(
            Product.name == product_data["name"]
        ).first()

        if existing:
            skipped += 1
            continue

        product = Product(
            id=str(uuid.uuid4()),
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            stock=product_data["stock"],
            category=product_data["category"],
            is_active=True,
            created_by=admin_user.id
        )

        db.add(product)
        created += 1

    return created, skipped


def run_seed():
    """
    Main seed function.
    Runs all seed operations inside a single transaction.
    Rolls back everything if any step fails.
    """
    logger.info("━" * 50)
    logger.info("  Product Management System — Seed Script")
    logger.info("━" * 50)

    db: Session = SessionLocal()

    try:
        # ── Seed Admin User ───────────────────────────────────────────────────
        logger.info("► Seeding admin user...")
        admin, admin_created = seed_user(db, ADMIN_USER)

        if admin_created:
            logger.info(f"  ✓ Admin created  : {ADMIN_USER['email']}")
        else:
            logger.info(f"  ↷ Admin exists   : {ADMIN_USER['email']} (skipped)")

        # ── Seed Regular User ─────────────────────────────────────────────────
        logger.info("► Seeding regular user...")
        regular, regular_created = seed_user(db, REGULAR_USER)

        if regular_created:
            logger.info(f"  ✓ User created   : {REGULAR_USER['email']}")
        else:
            logger.info(f"  ↷ User exists    : {REGULAR_USER['email']} (skipped)")

        # ── Seed Sample Products ──────────────────────────────────────────────
        logger.info("► Seeding sample products...")
        created_count, skipped_count = seed_products(db, admin)

        if created_count > 0:
            logger.info(f"  ✓ Products created  : {created_count}")
        if skipped_count > 0:
            logger.info(f"  ↷ Products skipped  : {skipped_count} (already exist)")

        # ── Commit everything at once ─────────────────────────────────────────
        db.commit()

        logger.info("━" * 50)
        logger.info("  Seed completed successfully")
        logger.info("━" * 50)
        logger.info("")
        logger.info("  Default Credentials")
        logger.info("  ───────────────────────────────────────")
        logger.info(f"  Admin  → {ADMIN_USER['email']} / {ADMIN_USER['password']}")
        logger.info(f"  User   → {REGULAR_USER['email']} / {REGULAR_USER['password']}")
        logger.info("  ───────────────────────────────────────")
        logger.info("  Swagger → http://localhost:8000/docs")
        logger.info("━" * 50)

    except Exception as e:
        db.rollback()
        logger.error(f"  ✗ Seed failed: {e}")
        logger.error("  All changes rolled back.")
        raise

    finally:
        db.close()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_seed()