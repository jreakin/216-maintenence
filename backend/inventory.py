from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, select
from pydantic import BaseModel
from backend.api import role_required, UserRole, engine

router = APIRouter()

class InventoryItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    quantity: int
    location: str
    task_id: int = Field(default=None, foreign_key="task.id")

class InventoryItemCreate(BaseModel):
    name: str
    quantity: int
    location: str
    task_id: int = None

@router.post('/inventory', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def create_inventory_item(item: InventoryItemCreate):
    new_item = InventoryItem(
        name=item.name,
        quantity=item.quantity,
        location=item.location,
        task_id=item.task_id
    )
    with Session(engine) as session:
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
    return new_item

@router.get('/inventory/{item_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def get_inventory_item(item_id: int):
    with Session(engine) as session:
        item = session.get(InventoryItem, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
        return item

@router.put('/inventory/{item_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def update_inventory_item(item_id: int, item: InventoryItemCreate):
    with Session(engine) as session:
        existing_item = session.get(InventoryItem, item_id)
        if not existing_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
        existing_item.name = item.name
        existing_item.quantity = item.quantity
        existing_item.location = item.location
        existing_item.task_id = item.task_id
        session.commit()
        session.refresh(existing_item)
    return existing_item

@router.delete('/inventory/{item_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def delete_inventory_item(item_id: int):
    with Session(engine) as session:
        item = session.get(InventoryItem, item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
        session.delete(item)
        session.commit()
    return {"detail": "Inventory item deleted"}

@router.get('/inventory', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def list_inventory_items():
    with Session(engine) as session:
        items = session.exec(select(InventoryItem)).all()
        return items

@router.post('/generate_order_list', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def generate_order_list(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        # Example logic to generate order list
        order_list = ["item1", "item2", "item3"]
        return {"order_list": order_list}
