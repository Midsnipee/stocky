from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, LargeBinary
from sqlmodel import Field, Relationship, SQLModel


class Role(str, Enum):
    ADMIN = "admin"
    STOREKEEPER = "storekeeper"
    BUYER = "buyer"
    VIEWER = "viewer"


class OrderStatus(str, Enum):
    REQUESTED = "demanded"
    INTERNAL_APPROVAL = "internal"
    SENT_TO_SUPPLIER = "ordered"
    DELIVERED = "delivered"


class SerialStatus(str, Enum):
    IN_STOCK = "in_stock"
    ASSIGNED = "assigned"
    IN_REPAIR = "in_repair"
    RETIRED = "retired"


class ActivityEntity(str, Enum):
    QUOTE = "quote"
    ORDER = "order"
    ITEM = "item"
    SERIAL = "serial"
    ASSIGNMENT = "assignment"


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str
    email: str
    department: Optional[str] = None
    site: Optional[str] = None
    role: Role = Field(default=Role.VIEWER)

    assignments: List["Assignment"] = Relationship(back_populates="assignee")


class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contact: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    quotes: List["Quote"] = Relationship(back_populates="supplier")
    orders: List["Order"] = Relationship(back_populates="supplier")


class StoredFile(SQLModel, table=True):
    __tablename__ = "files"

    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: str = Field(index=True)
    entity_id: int = Field(index=True)
    filename: str
    mime: str
    size: int
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    content: bytes = Field(sa_column=Column(LargeBinary))


class Quote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    ref: str
    amount: float
    currency: str = Field(default="EUR")
    status: OrderStatus = Field(default=OrderStatus.REQUESTED)
    requested_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    supplier: Supplier = Relationship(back_populates="quotes")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quote_id: Optional[int] = Field(default=None, foreign_key="quote.id")
    supplier_id: int = Field(foreign_key="supplier.id")
    internal_ref: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.REQUESTED, index=True)
    ordered_at: Optional[datetime] = None
    expected_delivery_at: Optional[date] = None

    supplier: Supplier = Relationship(back_populates="orders")
    quote: Optional[Quote] = Relationship()
    lines: List["OrderLine"] = Relationship(back_populates="order")
    deliveries: List["Delivery"] = Relationship(back_populates="order")


class OrderLine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    item_id: int = Field(foreign_key="item.id")
    qty: int
    unit_price: float
    tax_rate: float = Field(default=0.2)

    order: Order = Relationship(back_populates="lines")
    item: "Item" = Relationship(back_populates="order_lines")


class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    delivery_note_ref: Optional[str] = None
    delivered_at: date = Field(default_factory=date.today)

    order: Order = Relationship(back_populates="deliveries")
    serials: List["Serial"] = Relationship(back_populates="delivery")


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    internal_ref: Optional[str] = Field(default=None, index=True)
    default_supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")
    default_unit_price: Optional[float] = None
    site: Optional[str] = None
    low_stock_threshold: Optional[int] = Field(default=None)
    notes: Optional[str] = None

    order_lines: List[OrderLine] = Relationship(back_populates="item")
    serials: List["Serial"] = Relationship(back_populates="item")


class Serial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    serial_number: str = Field(index=True)
    delivery_id: Optional[int] = Field(default=None, foreign_key="delivery.id")
    delivery_date: Optional[date] = None
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")
    purchase_price: Optional[float] = None
    status: SerialStatus = Field(default=SerialStatus.IN_STOCK)
    current_assignee_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    item: Item = Relationship(back_populates="serials")
    supplier: Optional[Supplier] = Relationship()
    delivery: Optional[Delivery] = Relationship(back_populates="serials")
    assignments: List["Assignment"] = Relationship(back_populates="serial")


class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    serial_id: int = Field(foreign_key="serial.id")
    assignee_user_id: int = Field(foreign_key="user.id")
    start_date: date = Field(default_factory=date.today)
    expected_return_date: Optional[date] = None
    end_date: Optional[date] = None
    document_file_id: Optional[int] = Field(default=None, foreign_key="files.id")
    notes: Optional[str] = None

    serial: Serial = Relationship(back_populates="assignments")
    assignee: User = Relationship(back_populates="assignments")


class ActivityLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: ActivityEntity
    entity_id: int
    action: str
    actor_user_id: int = Field(foreign_key="user.id")
    at: datetime = Field(default_factory=datetime.utcnow)
    payload_json: Optional[str] = None

