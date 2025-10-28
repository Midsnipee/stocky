from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Sequence

from sqlmodel import Session, select

from .models import (
    ActivityEntity,
    ActivityLog,
    Assignment,
    Delivery,
    Item,
    Order,
    OrderLine,
    OrderStatus,
    Role,
    Serial,
    SerialStatus,
    Supplier,
    User,
)

CATEGORIES = ["PC Portable", "Écran", "Dock", "Smartphone"]
SITES = ["Paris", "Lyon", "Marseille"]
SUPPLIERS = [
    {"name": "ACME", "contact": "Jean Dupont"},
    {"name": "Contoso", "contact": "Alice Martin"},
]


def create_demo_data(session: Session) -> None:
    if session.exec(select(User)).first():
        return

    users = [
        User(display_name="Admin", email="admin@example.com", role=Role.ADMIN, site="Paris"),
        User(display_name="Magasinier", email="stock@example.com", role=Role.STOREKEEPER, site="Lyon"),
        User(display_name="Acheteur", email="buyer@example.com", role=Role.BUYER, site="Marseille"),
    ]
    session.add_all(users)

    supplier_models = [Supplier(**supplier) for supplier in SUPPLIERS]
    session.add_all(supplier_models)
    session.flush()

    items: list[Item] = []
    for index in range(10):
        supplier = random.choice(supplier_models)
        item = Item(
            name=f"Matériel {index + 1}",
            category=random.choice(CATEGORIES),
            internal_ref=f"ITM-{index+1:03d}",
            default_supplier_id=supplier.id,
            default_unit_price=round(random.uniform(150, 1500), 2),
            site=random.choice(SITES),
            low_stock_threshold=random.randint(1, 3),
            notes="Démo",
        )
        items.append(item)
    session.add_all(items)
    session.flush()

    orders: list[Order] = []
    serials: list[Serial] = []
    assignments: list[Assignment] = []

    for order_index in range(4):
        supplier = random.choice(supplier_models)
        status = random.choice(list(OrderStatus))
        order = Order(
            supplier_id=supplier.id,
            internal_ref=f"CMD-{order_index+1:03d}",
            status=status,
            ordered_at=date.today() - timedelta(days=30 - order_index * 3),
            expected_delivery_at=date.today() + timedelta(days=7),
        )
        session.add(order)
        session.flush()
        orders.append(order)

        for item in random.sample(items, 3):
            qty = random.randint(1, 5)
            line = OrderLine(order_id=order.id, item_id=item.id, qty=qty, unit_price=item.default_unit_price or 500)
            session.add(line)

            delivered_qty = qty if status == OrderStatus.DELIVERED else random.randint(0, qty)
            if delivered_qty:
                delivery = Delivery(order_id=order.id, delivery_note_ref=f"BL-{order.id}-{item.id}")
                session.add(delivery)
                session.flush()
                for serial_index in range(delivered_qty):
                    serial = Serial(
                        item_id=item.id,
                        serial_number=f"{item.internal_ref}-{order_index}-{serial_index}-{random.randint(1000,9999)}",
                        delivery_id=delivery.id,
                        delivery_date=date.today() - timedelta(days=random.randint(1, 365)),
                        warranty_start=date.today() - timedelta(days=30),
                        warranty_end=date.today() + timedelta(days=random.randint(60, 400)),
                        supplier_id=supplier.id,
                        purchase_price=item.default_unit_price,
                        status=SerialStatus.IN_STOCK,
                    )
                    serials.append(serial)

    session.add_all(serials)
    session.flush()

    for serial in random.sample(serials, min(20, len(serials))):
        assignee = random.choice(users)
        assignment = Assignment(
            serial_id=serial.id,
            assignee_user_id=assignee.id,
            start_date=date.today() - timedelta(days=random.randint(1, 180)),
            expected_return_date=date.today() + timedelta(days=random.randint(30, 120)),
        )
        assignments.append(assignment)
        serial.status = SerialStatus.ASSIGNED
        serial.current_assignee_user_id = assignee.id

    session.add_all(assignments)

    session.add_all(
        ActivityLog(
            entity_type=ActivityEntity.ORDER,
            entity_id=order.id,
            action="seed",
            actor_user_id=users[0].id,
            payload_json="{}",
        )
        for order in orders
    )

    session.commit()


def get_demo_users(session: Session) -> Sequence[User]:
    return session.exec(select(User)).all()
