from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import OrderStatus, Role, SerialStatus


class FileRead(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    filename: str
    mime: str
    size: int
    download_url: str

    class Config:
        orm_mode = True


class SupplierRead(BaseModel):
    id: int
    name: str
    contact: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]

    class Config:
        orm_mode = True


class ItemCreate(BaseModel):
    name: str
    category: str
    internal_ref: Optional[str] = None
    default_supplier_id: Optional[int] = None
    default_unit_price: Optional[float] = None
    site: Optional[str] = None
    low_stock_threshold: Optional[int] = None
    notes: Optional[str] = None


class ItemRead(BaseModel):
    id: int
    name: str
    category: str
    internal_ref: Optional[str]
    default_unit_price: Optional[float]
    site: Optional[str]
    low_stock_threshold: Optional[int]
    notes: Optional[str]
    stock: int = Field(..., description="Calculated stock based on serials")

    class Config:
        orm_mode = True


class OrderLineCreate(BaseModel):
    item_id: int
    qty: int
    unit_price: float
    tax_rate: float = 0.2


class OrderCreate(BaseModel):
    supplier_id: int
    internal_ref: Optional[str] = None
    expected_delivery_at: Optional[date] = None
    lines: List[OrderLineCreate]


class OrderReadLine(BaseModel):
    item_id: int
    qty: int
    unit_price: float
    tax_rate: float

    class Config:
        orm_mode = True


class OrderRead(BaseModel):
    id: int
    supplier: SupplierRead
    internal_ref: Optional[str]
    status: OrderStatus
    ordered_at: Optional[datetime]
    expected_delivery_at: Optional[date]
    lines: List[OrderReadLine]
    files: List[FileRead] = Field(default_factory=list)

    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class DeliveryCreate(BaseModel):
    delivery_note_ref: Optional[str] = None
    delivered_at: Optional[date] = None
    serial_numbers: List[str] = Field(default_factory=list)
    item_id: Optional[int] = None
    purchase_price: Optional[float] = None
    warranty_duration_days: Optional[int] = None


class SerialRead(BaseModel):
    id: int
    item_id: int
    serial_number: str
    delivery_date: Optional[date]
    warranty_start: Optional[date]
    warranty_end: Optional[date]
    status: SerialStatus
    current_assignee_user_id: Optional[int]

    class Config:
        orm_mode = True


class AssignmentCreate(BaseModel):
    serial_id: int
    assignee_user_id: int
    start_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    notes: Optional[str] = None


class AssignmentRead(BaseModel):
    id: int
    serial_id: int
    assignee_user_id: int
    start_date: date
    expected_return_date: Optional[date]
    end_date: Optional[date]
    notes: Optional[str]
    document_file_id: Optional[int]

    class Config:
        orm_mode = True


class DashboardWidget(BaseModel):
    key: str
    title: str
    data: dict


class DashboardResponse(BaseModel):
    widgets: List[DashboardWidget]


class ReportRow(BaseModel):
    key: str
    value: float


class ReportResponse(BaseModel):
    title: str
    rows: List[ReportRow]


class UserRead(BaseModel):
    id: int
    display_name: str
    email: str
    department: Optional[str]
    site: Optional[str]
    role: Role

    class Config:
        orm_mode = True
