from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlmodel import Session, func, select

from .database import get_session, init_db
from .dependencies import get_current_role, require_roles
from .models import (
    ActivityEntity,
    ActivityLog,
    Assignment,
    Delivery,
    Item,
    Order,
    OrderLine,
    OrderStatus,
    Quote,
    Role,
    Serial,
    SerialStatus,
    StoredFile,
    Supplier,
    User,
)
from .schemas import (
    AssignmentCreate,
    AssignmentRead,
    DashboardResponse,
    DashboardWidget,
    DeliveryCreate,
    ItemCreate,
    FileRead,
    ItemRead,
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    ReportResponse,
    ReportRow,
    SerialRead,
    SupplierRead,
    UserRead,
)
from .seed import create_demo_data

app = FastAPI(title="Stocky", description="Gestion des stocks, commandes et attributions")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with get_session() as session:
        create_demo_data(session)


@app.get("/users", response_model=List[UserRead])
def list_users(session: Session = Depends(get_session), role: Role = Depends(require_roles(Role.ADMIN, Role.BUYER, Role.STOREKEEPER))):
    return session.exec(select(User)).all()


@app.get("/suppliers", response_model=List[SupplierRead])
def list_suppliers(session: Session = Depends(get_session), role: Role = Depends(get_current_role)):
    return session.exec(select(Supplier)).all()


@app.post("/files", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    attachment: UploadFile = File(...),
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.BUYER, Role.STOREKEEPER)),
) -> FileRead:
    _require_entity(session, entity_type, entity_id)
    content = await attachment.read()
    await attachment.close()
    stored = StoredFile(
        entity_type=entity_type,
        entity_id=entity_id,
        filename=attachment.filename or "fichier",
        mime=attachment.content_type or "application/octet-stream",
        size=len(content),
        content=content,
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)
    return _file_to_schema(stored)


@app.get("/files", response_model=List[FileRead])
def list_files(
    entity_type: str | None = Query(default=None),
    entity_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> List[FileRead]:
    query = select(StoredFile)
    if entity_type:
        query = query.where(StoredFile.entity_type == entity_type)
    if entity_id:
        query = query.where(StoredFile.entity_id == entity_id)
    rows = session.exec(query.order_by(StoredFile.created_at.desc())).all()
    return [_file_to_schema(row) for row in rows]


@app.get("/files/{file_id}/download")
def download_file(
    file_id: int,
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> Response:
    stored = session.get(StoredFile, file_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    headers = {"Content-Disposition": f"attachment; filename=\"{stored.filename}\""}
    return Response(content=stored.content, media_type=stored.mime, headers=headers)


@app.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.BUYER, Role.STOREKEEPER)),
) -> None:
    stored = session.get(StoredFile, file_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    session.delete(stored)
    session.commit()


ENTITY_MODEL_MAP = {
    "order": Order,
    "quote": Quote,
    "item": Item,
    "serial": Serial,
    "assignment": Assignment,
}


def _require_entity(session: Session, entity_type: str, entity_id: int) -> None:
    model = ENTITY_MODEL_MAP.get(entity_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Type d'entité inconnu")
    if session.get(model, entity_id) is None:
        raise HTTPException(status_code=404, detail=f"{entity_type} introuvable")


def _file_to_schema(stored_file: StoredFile) -> FileRead:
    return FileRead.from_orm(stored_file).copy(
        update={"download_url": f"/files/{stored_file.id}/download"}
    )


def _files_for_entity(session: Session, entity_type: str, entity_id: int) -> List[FileRead]:
    rows = session.exec(
        select(StoredFile)
        .where(StoredFile.entity_type == entity_type)
        .where(StoredFile.entity_id == entity_id)
        .order_by(StoredFile.created_at.desc())
    ).all()
    return [_file_to_schema(row) for row in rows]


def _calculate_stock(session: Session, items: Iterable[Item]) -> Dict[int, int]:
    item_ids = [item.id for item in items if item.id is not None]
    if not item_ids:
        return {}
    rows = session.exec(
        select(Serial.item_id, func.count(Serial.id))
        .where(Serial.item_id.in_(item_ids))
        .where(Serial.status == SerialStatus.IN_STOCK)
        .group_by(Serial.item_id)
    ).all()
    return {item_id: count for item_id, count in rows}


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.STOREKEEPER)),
) -> ItemRead:
    item = Item(**payload.dict())
    session.add(item)
    session.commit()
    session.refresh(item)
    stock = _calculate_stock(session, [item]).get(item.id, 0)
    return ItemRead.from_orm(item).copy(update={"stock": stock})


@app.get("/items", response_model=List[ItemRead])
def list_items(
    category: str | None = Query(default=None),
    supplier_id: int | None = Query(default=None),
    site: str | None = Query(default=None),
    search: str | None = Query(default=None),
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> List[ItemRead]:
    query = select(Item)
    if category:
        query = query.where(Item.category == category)
    if supplier_id:
        query = query.where(Item.default_supplier_id == supplier_id)
    if site:
        query = query.where(Item.site == site)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(func.lower(Item.name).like(like) | func.lower(Item.internal_ref).like(like))
    items = session.exec(query.order_by(Item.name)).all()
    stock_map = _calculate_stock(session, items)
    return [ItemRead.from_orm(item).copy(update={"stock": stock_map.get(item.id, 0)}) for item in items]


@app.get("/serials", response_model=List[SerialRead])
def list_serials(
    status_filter: SerialStatus | None = Query(default=None, alias="status"),
    item_id: int | None = Query(default=None),
    assigned: bool | None = Query(default=None),
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> List[SerialRead]:
    query = select(Serial)
    if status_filter:
        query = query.where(Serial.status == status_filter)
    if item_id:
        query = query.where(Serial.item_id == item_id)
    if assigned is True:
        query = query.where(Serial.current_assignee_user_id.is_not(None))
    if assigned is False:
        query = query.where(Serial.current_assignee_user_id.is_(None))
    serials = session.exec(query.order_by(Serial.delivery_date.desc().nullslast())).all()
    return [SerialRead.from_orm(serial) for serial in serials]


@app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.BUYER)),
) -> OrderRead:
    supplier = session.get(Supplier, payload.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    order = Order(supplier_id=payload.supplier_id, internal_ref=payload.internal_ref, status=OrderStatus.REQUESTED, ordered_at=datetime.utcnow(), expected_delivery_at=payload.expected_delivery_at)
    session.add(order)
    session.flush()

    for line in payload.lines:
        session.add(OrderLine(order_id=order.id, item_id=line.item_id, qty=line.qty, unit_price=line.unit_price, tax_rate=line.tax_rate))

    session.add(
        ActivityLog(
            entity_type=ActivityEntity.ORDER,
            entity_id=order.id,
            action="create",
            actor_user_id=0,
            payload_json=json.dumps({"status": order.status.value}),
        )
    )
    session.commit()
    session.refresh(order)
    return _serialize_order(session, order)


def _serialize_order(session: Session, order: Order) -> OrderRead:
    session.refresh(order, attribute_names=["supplier", "lines"])
    files = _files_for_entity(session, "order", order.id)
    return OrderRead.from_orm(order).copy(update={"files": files})


@app.get("/orders", response_model=List[OrderRead])
def list_orders(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    supplier_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> List[OrderRead]:
    query = select(Order)
    if status_filter:
        query = query.where(Order.status == status_filter)
    if supplier_id:
        query = query.where(Order.supplier_id == supplier_id)
    if search:
        like = f"%{search.lower()}%"
        query = query.where(func.lower(Order.internal_ref).like(like))
    orders = session.exec(query.order_by(Order.ordered_at.desc().nullslast())).all()
    return [_serialize_order(session, order) for order in orders]


@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session), role: Role = Depends(get_current_role)) -> OrderRead:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(session, order)


def _assert_transition_allowed(current: OrderStatus, new_status: OrderStatus) -> None:
    transitions = {
        OrderStatus.REQUESTED: {OrderStatus.INTERNAL_APPROVAL},
        OrderStatus.INTERNAL_APPROVAL: {OrderStatus.SENT_TO_SUPPLIER},
        OrderStatus.SENT_TO_SUPPLIER: {OrderStatus.DELIVERED},
        OrderStatus.DELIVERED: set(),
    }
    if new_status not in transitions[current]:
        raise HTTPException(status_code=400, detail="Transition non autorisée")


@app.patch("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.BUYER)),
) -> OrderRead:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    _assert_transition_allowed(order.status, payload.status)
    order.status = payload.status
    if payload.status == OrderStatus.SENT_TO_SUPPLIER and order.ordered_at is None:
        order.ordered_at = datetime.utcnow()
    if payload.status == OrderStatus.DELIVERED:
        order.expected_delivery_at = date.today()

    session.add(
        ActivityLog(
            entity_type=ActivityEntity.ORDER,
            entity_id=order.id,
            action="status",
            actor_user_id=0,
            payload_json=json.dumps(payload.dict()),
        )
    )
    session.commit()
    session.refresh(order)
    return _serialize_order(session, order)


@app.post("/orders/{order_id}/deliveries", response_model=OrderRead)
def register_delivery(
    order_id: int,
    payload: DeliveryCreate,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.STOREKEEPER)),
) -> OrderRead:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    delivery = Delivery(order_id=order_id, delivery_note_ref=payload.delivery_note_ref, delivered_at=payload.delivered_at or date.today())
    session.add(delivery)
    session.flush()

    warranty_start = payload.delivered_at or date.today()
    warranty_end = warranty_start + timedelta(days=payload.warranty_duration_days or 365)

    if payload.serial_numbers and payload.item_id is None:
        raise HTTPException(status_code=400, detail="item_id requis pour créer des numéros de série")

    for serial_number in payload.serial_numbers:
        serial = Serial(
            item_id=payload.item_id,
            serial_number=serial_number,
            delivery_id=delivery.id,
            delivery_date=delivery.delivered_at,
            warranty_start=warranty_start,
            warranty_end=warranty_end,
            supplier_id=order.supplier_id,
            purchase_price=payload.purchase_price,
            status=SerialStatus.IN_STOCK,
        )
        session.add(serial)

    session.add(
        ActivityLog(
            entity_type=ActivityEntity.ORDER,
            entity_id=order_id,
            action="delivery",
            actor_user_id=0,
            payload_json=json.dumps(payload.dict()),
        )
    )
    session.commit()
    session.refresh(order)
    return _serialize_order(session, order)


@app.post("/assignments", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_serial(
    payload: AssignmentCreate,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.STOREKEEPER)),
) -> AssignmentRead:
    serial = session.get(Serial, payload.serial_id)
    if serial is None:
        raise HTTPException(status_code=404, detail="Serial not found")
    if serial.status != SerialStatus.IN_STOCK:
        raise HTTPException(status_code=400, detail="Le numéro de série n'est pas disponible")

    user = session.get(User, payload.assignee_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    assignment = Assignment(
        serial_id=serial.id,
        assignee_user_id=user.id,
        start_date=payload.start_date or date.today(),
        expected_return_date=payload.expected_return_date,
        notes=payload.notes,
    )
    serial.status = SerialStatus.ASSIGNED
    serial.current_assignee_user_id = user.id

    session.add(assignment)
    session.add(serial)
    session.add(
        ActivityLog(
            entity_type=ActivityEntity.ASSIGNMENT,
            entity_id=serial.id,
            action="assign",
            actor_user_id=0,
            payload_json=json.dumps(payload.dict()),
        )
    )
    session.commit()
    session.refresh(assignment)
    return AssignmentRead.from_orm(assignment)


@app.post("/assignments/{assignment_id}/return", response_model=AssignmentRead)
def close_assignment(
    assignment_id: int,
    session: Session = Depends(get_session),
    role: Role = Depends(require_roles(Role.ADMIN, Role.STOREKEEPER)),
) -> AssignmentRead:
    assignment = session.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if assignment.end_date is not None:
        return AssignmentRead.from_orm(assignment)

    assignment.end_date = date.today()
    serial = session.get(Serial, assignment.serial_id)
    if serial:
        serial.status = SerialStatus.IN_STOCK
        serial.current_assignee_user_id = None
        session.add(serial)

    session.add(
        ActivityLog(
            entity_type=ActivityEntity.ASSIGNMENT,
            entity_id=assignment.serial_id,
            action="return",
            actor_user_id=0,
            payload_json=json.dumps({"assignment_id": assignment_id}),
        )
    )
    session.commit()
    session.refresh(assignment)
    return AssignmentRead.from_orm(assignment)


@app.get("/assignments", response_model=List[AssignmentRead])
def list_assignments(
    user_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    session: Session = Depends(get_session),
    role: Role = Depends(get_current_role),
) -> List[AssignmentRead]:
    query = select(Assignment)
    if user_id:
        query = query.where(Assignment.assignee_user_id == user_id)
    if active_only:
        query = query.where(Assignment.end_date.is_(None))
    assignments = session.exec(query.order_by(Assignment.start_date.desc())).all()
    return [AssignmentRead.from_orm(assignment) for assignment in assignments]


def _widget_stock_by_category(session: Session) -> DashboardWidget:
    rows = session.exec(
        select(Item.category, func.count(Serial.id))
        .join(Serial, Serial.item_id == Item.id)
        .where(Serial.status == SerialStatus.IN_STOCK)
        .group_by(Item.category)
    ).all()
    data = {category or "Non défini": count for category, count in rows}
    return DashboardWidget(key="stock_by_category", title="Stock par catégorie", data={"series": data})


def _widget_pending_deliveries(session: Session) -> DashboardWidget:
    rows = session.exec(select(Order).where(Order.status == OrderStatus.SENT_TO_SUPPLIER)).all()
    return DashboardWidget(
        key="pending_deliveries",
        title="Livraisons en attente",
        data={
            "count": len(rows),
            "orders": [order.internal_ref for order in rows],
        },
    )


def _widget_warranty(session: Session) -> DashboardWidget:
    upcoming = date.today() + timedelta(days=90)
    rows = session.exec(
        select(Serial.serial_number, Serial.warranty_end)
        .where(Serial.warranty_end.is_not(None), Serial.warranty_end <= upcoming)
        .order_by(Serial.warranty_end)
    ).all()
    return DashboardWidget(
        key="warranties",
        title="Garanties à échéance",
        data={"count": len(rows), "serials": rows},
    )


def _widget_recent_assignments(session: Session) -> DashboardWidget:
    rows = session.exec(select(Assignment).order_by(Assignment.start_date.desc()).limit(10)).all()
    return DashboardWidget(
        key="assignments",
        title="Attributions récentes",
        data={
            "timeline": [
                {
                    "serial_id": assignment.serial_id,
                    "assignee": assignment.assignee_user_id,
                    "start_date": assignment.start_date.isoformat(),
                }
                for assignment in rows
            ]
        },
    )


def _widget_stock_value(session: Session) -> DashboardWidget:
    result = session.exec(
        select(func.coalesce(func.sum(Serial.purchase_price), 0))
        .where(Serial.status == SerialStatus.IN_STOCK)
    ).one()
    total = result[0] if isinstance(result, tuple) else result
    return DashboardWidget(key="stock_value", title="Valeur de stock", data={"amount": float(total or 0)})


def _widget_alerts(session: Session) -> DashboardWidget:
    items = session.exec(select(Item)).all()
    stock_map = _calculate_stock(session, items)
    alerts = []
    for item in items:
        threshold = item.low_stock_threshold or 0
        if threshold and stock_map.get(item.id, 0) <= threshold:
            alerts.append({"type": "stock", "item": item.name, "stock": stock_map.get(item.id, 0)})
    expired = session.exec(
        select(Serial.serial_number, Serial.warranty_end)
        .where(Serial.warranty_end.is_not(None), Serial.warranty_end < date.today())
    ).all()
    for serial_number, warranty_end in expired:
        alerts.append({"type": "warranty", "serial": serial_number, "ended": warranty_end.isoformat()})
    return DashboardWidget(key="alerts", title="Alertes", data={"alerts": alerts})


@app.get("/dashboard/widgets", response_model=DashboardResponse)
def get_dashboard(session: Session = Depends(get_session), role: Role = Depends(get_current_role)) -> DashboardResponse:
    widgets = [
        _widget_stock_by_category(session),
        _widget_pending_deliveries(session),
        _widget_warranty(session),
        _widget_recent_assignments(session),
        _widget_stock_value(session),
        _widget_alerts(session),
    ]
    return DashboardResponse(widgets=widgets)


@app.get("/reports/stock-by-site", response_model=ReportResponse)
def report_stock_by_site(session: Session = Depends(get_session), role: Role = Depends(get_current_role)) -> ReportResponse:
    rows = session.exec(
        select(Item.site, func.count(Serial.id)).join(Serial, Serial.item_id == Item.id).where(Serial.status == SerialStatus.IN_STOCK).group_by(Item.site)
    ).all()
    return ReportResponse(title="Stock par site", rows=[ReportRow(key=site or "Non défini", value=count) for site, count in rows])


@app.get("/reports/orders-by-status", response_model=ReportResponse)
def report_orders_by_status(session: Session = Depends(get_session), role: Role = Depends(get_current_role)) -> ReportResponse:
    rows = session.exec(select(Order.status, func.count(Order.id)).group_by(Order.status)).all()
    return ReportResponse(title="Commandes par état", rows=[ReportRow(key=status.value, value=count) for status, count in rows])


@app.get("/reports/assignments-by-department", response_model=ReportResponse)
def report_assignments_by_department(session: Session = Depends(get_session), role: Role = Depends(get_current_role)) -> ReportResponse:
    rows = session.exec(
        select(User.department, func.count(Assignment.id))
        .join(Assignment, Assignment.assignee_user_id == User.id)
        .where(Assignment.end_date.is_(None))
        .group_by(User.department)
    ).all()
    return ReportResponse(title="Attributions actives par service", rows=[ReportRow(key=dept or "Non défini", value=count) for dept, count in rows])
