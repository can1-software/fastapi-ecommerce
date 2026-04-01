from __future__ import annotations

import argparse
import random
import sys
from decimal import Decimal

from faker import Faker
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.auth.infrastructure.persistence.models.user import User
from app.modules.auth.infrastructure.repositories.user_repository import UserRepository
from app.modules.auth.infrastructure.security import hash_password
from app.modules.categories.infrastructure.persistence.models.category import Category
from app.modules.categories.infrastructure.repositories.category_repository import CategoryRepository
from app.modules.products.infrastructure.repositories.product_repository import ProductRepository

CATEGORY_NAMES: list[str] = [
    "Electronics",
    "Clothing",
    "Books",
    "Home & Garden",
    "Sports",
    "Toys",
    "Beauty",
    "Food",
    "Automotive",
]

ADMIN_EMAIL = "admin@seed.local"
ADMIN_PASSWORD = "Password123!"


def _ensure_seed_allowed() -> None:
    env = (settings.APP_ENV or "development").strip().lower()
    if env in ("production", "prod"):
        print("Seed refused: APP_ENV is production.", file=sys.stderr)
        sys.exit(1)
    if not settings.DEBUG and not settings.SEED_ALLOW:
        print(
            "Seed refused: set DEBUG=true or SEED_ALLOW=true in .env (development only).",
            file=sys.stderr,
        )
        sys.exit(1)


def _user_count(session: Session) -> int:
    return int(session.execute(select(func.count()).select_from(User)).scalar_one())


def _truncate_seed_tables(session: Session) -> None:
    session.execute(
        text(
            "TRUNCATE TABLE public.products, public.categories, public.users "
            "RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


def _seed_users(session: Session, fake: Faker) -> None:
    repo = UserRepository(session)
    repo.create(
        email=ADMIN_EMAIL.lower(),
        hashed_password=hash_password(ADMIN_PASSWORD),
        is_admin=True,
    )
    for _ in range(9):
        email = fake.unique.email().lower()
        pwd = fake.password(
            length=14,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
        repo.create(
            email=email,
            hashed_password=hash_password(pwd),
            is_admin=False,
        )


def _seed_categories(session: Session) -> list[Category]:
    repo = CategoryRepository(session)
    rows: list[Category] = []
    for name in CATEGORY_NAMES:
        rows.append(repo.create(name=name))
    return rows


def _seed_products(session: Session, fake: Faker, categories: list[Category]) -> int:
    repo = ProductRepository(session)
    cat_ids = [c.id for c in categories]
    n = random.randint(35, 50)
    for _ in range(n):
        cid = random.choice(cat_ids)
        name = fake.catch_phrase()[:255]
        desc = fake.text(max_nb_chars=800)
        price = Decimal(str(round(random.uniform(4.99, 799.99), 2)))
        stock = random.randint(0, 250)
        repo.create(
            name=name,
            description=desc,
            price=price,
            stock=stock,
            image=None,
            category_id=cid,
        )
    return n


def run(*, fresh: bool) -> None:
    _ensure_seed_allowed()
    fake = Faker()
    fake.unique.clear()

    db = SessionLocal()
    try:
        if fresh:
            _truncate_seed_tables(db)
        elif _user_count(db) > 0:
            print(
                "Database already has data. Skip seeding. "
                "Use --fresh to truncate users/categories/products and reseed.",
            )
            return

        _seed_users(db, fake)
        cats = _seed_categories(db)
        n_products = _seed_products(db, fake, cats)

        print("Seed completed.")
        print(f"  Users: 10 (admin: {ADMIN_EMAIL})")
        print(f"  Categories: {len(cats)}")
        print(f"  Products: {n_products}")
        print(f"  Admin password (dev): {ADMIN_PASSWORD}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Development database seed.")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Truncate products, categories, users (CASCADE) then seed.",
    )
    args = parser.parse_args()
    run(fresh=args.fresh)


if __name__ == "__main__":
    main()
