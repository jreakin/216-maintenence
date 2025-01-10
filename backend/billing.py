from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, select
from pydantic import BaseModel
from backend.api import role_required, UserRole, engine

router = APIRouter()

class Estimate(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_ids: str
    total_estimated_cost: float
    region: str
    store: str
    manager: str

class Invoice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_ids: str
    total_final_cost: float
    region: str
    store: str
    manager: str

class EstimateCreate(BaseModel):
    task_ids: str
    total_estimated_cost: float
    region: str
    store: str
    manager: str

class InvoiceCreate(BaseModel):
    task_ids: str
    total_final_cost: float
    region: str
    store: str
    manager: str

@router.post('/estimates', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def create_estimate(estimate: EstimateCreate):
    new_estimate = Estimate(
        task_ids=estimate.task_ids,
        total_estimated_cost=estimate.total_estimated_cost,
        region=estimate.region,
        store=estimate.store,
        manager=estimate.manager
    )
    with Session(engine) as session:
        session.add(new_estimate)
        session.commit()
        session.refresh(new_estimate)
    return new_estimate

@router.post('/invoices', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def create_invoice(invoice: InvoiceCreate):
    new_invoice = Invoice(
        task_ids=invoice.task_ids,
        total_final_cost=invoice.total_final_cost,
        region=invoice.region,
        store=invoice.store,
        manager=invoice.manager
    )
    with Session(engine) as session:
        session.add(new_invoice)
        session.commit()
        session.refresh(new_invoice)
    return new_invoice

@router.get('/estimates/{estimate_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def get_estimate(estimate_id: int):
    with Session(engine) as session:
        estimate = session.get(Estimate, estimate_id)
        if not estimate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")
        return estimate

@router.get('/invoices/{invoice_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def get_invoice(invoice_id: int):
    with Session(engine) as session:
        invoice = session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return invoice

@router.put('/estimates/{estimate_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def update_estimate(estimate_id: int, estimate: EstimateCreate):
    with Session(engine) as session:
        existing_estimate = session.get(Estimate, estimate_id)
        if not existing_estimate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")
        existing_estimate.task_ids = estimate.task_ids
        existing_estimate.total_estimated_cost = estimate.total_estimated_cost
        existing_estimate.region = estimate.region
        existing_estimate.store = estimate.store
        existing_estimate.manager = estimate.manager
        session.commit()
        session.refresh(existing_estimate)
    return existing_estimate

@router.put('/invoices/{invoice_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def update_invoice(invoice_id: int, invoice: InvoiceCreate):
    with Session(engine) as session:
        existing_invoice = session.get(Invoice, invoice_id)
        if not existing_invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        existing_invoice.task_ids = invoice.task_ids
        existing_invoice.total_final_cost = invoice.total_final_cost
        existing_invoice.region = invoice.region
        existing_invoice.store = invoice.store
        existing_invoice.manager = invoice.manager
        session.commit()
        session.refresh(existing_invoice)
    return existing_invoice
