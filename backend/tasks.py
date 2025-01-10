from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select
from googlemaps import Client as GoogleMaps
from usps import USPSApi, Address
from google.cloud import vision
import boto3
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import datetime
import supabase
from backend.user_management import UserRole, check_permission
from apns2.client import APNsClient
from apns2.payload import Payload
from sklearn.linear_model import LinearRegression
import numpy as np

app = FastAPI()

# Supabase setup
supabase_url = "your_supabase_url"
supabase_key = "your_supabase_key"
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Initialize Google Maps API
gmaps = GoogleMaps('your_google_maps_api_key')

# Initialize USPS API
usps = USPSApi('your_usps_api_key')

# Initialize Google Cloud Vision API
vision_client = vision.ImageAnnotatorClient()

# Initialize Amazon Textract
textract = boto3.client('textract', region_name='your_region')

# Initialize Microsoft Azure Cognitive Services - Computer Vision API
computervision_client = ComputerVisionClient(
    'your_azure_endpoint',
    CognitiveServicesCredentials('your_azure_subscription_key')
)

# Initialize APNs client
apns_client = APNsClient('path_to_your_apns_certificate.pem', use_sandbox=True, use_alternative_port=False)

# User model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str
    role: str

# Task model
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str
    location: str
    estimated_cost: float
    final_cost: float = None
    status: str
    priority: str
    deadline: datetime.datetime = None
    dependencies: str = None
    comments: str = None
    attachments: str = None
    before_scan: str = None
    after_scan: str = None

# Estimate model
class Estimate(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_ids: str
    total_estimated_cost: float
    region: str
    store: str
    manager: str

# Invoice model
class Invoice(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    task_ids: str
    total_final_cost: float
    region: str
    store: str
    manager: str

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    description: str
    location: str
    estimated_cost: float
    priority: str
    deadline: datetime.datetime
    before_scan: str = None
    after_scan: str = None

class TaskUpdate(BaseModel):
    description: str
    location: str
    estimated_cost: float
    final_cost: float = None
    status: str
    priority: str
    deadline: datetime.datetime
    dependencies: str = None
    comments: str = None
    attachments: str = None
    before_scan: str = None
    after_scan: str = None

class TaskPriorityUpdate(BaseModel):
    priority: str

class AddressValidation(BaseModel):
    address: str

class ReceiptScan(BaseModel):
    file: bytes

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

# Role-based access control (RBAC) dependency
def role_required(required_role: str):
    def role_dependency(Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == current_user)).first()
            if not check_permission(user.role, required_role):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return role_dependency

# User registration endpoint
@app.post('/register', response_model=UserCreate)
def register(user: UserCreate):
    response = supabase_client.auth.sign_up({
        'email': user.username,
        'password': user.password
    })
    if response.get('error'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response['error']['message'])
    new_user = User(username=user.username, password=user.password, role=user.role)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user

# User login endpoint
@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), Authorize: AuthJWT = Depends()):
    response = supabase_client.auth.sign_in({
        'email': form_data.username,
        'password': form_data.password
    })
    if response.get('error'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=response['error']['message'])
    access_token = Authorize.create_access_token(subject=form_data.username)
    return {"access_token": access_token}

# Task creation endpoint
@app.post('/tasks', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def create_task(task: TaskCreate):
    new_task = Task(
        description=task.description,
        location=task.location,
        estimated_cost=task.estimated_cost,
        status='Not Started',
        priority=task.priority,
        deadline=task.deadline,
        before_scan=task.before_scan,
        after_scan=task.after_scan
    )
    with Session(engine) as session:
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
    return new_task

# Task update endpoint
@app.put('/tasks/{task_id}', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def update_task(task_id: int, task: TaskUpdate):
    with Session(engine) as session:
        existing_task = session.get(Task, task_id)
        if not existing_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        existing_task.description = task.description
        existing_task.location = task.location
        existing_task.estimated_cost = task.estimated_cost
        existing_task.final_cost = task.final_cost
        existing_task.status = task.status
        existing_task.priority = task.priority
        existing_task.deadline = task.deadline
        existing_task.dependencies = task.dependencies
        existing_task.comments = task.comments
        existing_task.attachments = task.attachments
        existing_task.before_scan = task.before_scan
        existing_task.after_scan = task.after_scan
        session.commit()
        session.refresh(existing_task)
    return existing_task

# Task prioritization endpoint
@app.put('/tasks/{task_id}/priority', dependencies=[Depends(role_required(UserRole.DISPATCHER))])
def prioritize_task(task_id: int, priority_update: TaskPriorityUpdate):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        task.priority = priority_update.priority
        session.commit()
        session.refresh(task)
    return task

# Address validation endpoint
@app.post('/validate_address', dependencies=[Depends(AuthJWT)])
def validate_address(address_validation: AddressValidation):
    address = address_validation.address
    # Validate address using Google Maps API
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        standardized_address = geocode_result[0]['formatted_address']
        return {"standardized_address": standardized_address}
    # Validate address using USPS Address Verification API
    usps_address = Address(
        name='',
        address_1=address['address_1'],
        address_2=address['address_2'],
        city=address['city'],
        state=address['state'],
        zipcode=address['zipcode']
    )
    usps_result = usps.validate_address(usps_address)
    if usps_result:
        standardized_address = usps_result.result['address']
        return {"standardized_address": standardized_address}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address validation failed")

# Receipt scanning endpoint
@app.post('/scan_receipt', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
def scan_receipt(receipt_scan: ReceiptScan):
    file = receipt_scan.file
    # Use Google Cloud Vision API for receipt scanning
    image = vision.Image(content=file)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return {"text": texts[0].description}
    # Use Amazon Textract for receipt scanning
    response = textract.detect_document_text(Document={'Bytes': file})
    if response['Blocks']:
        text = ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
        return {"text": text}
    # Use Microsoft Azure Cognitive Services - Computer Vision API for receipt scanning
    response = computervision_client.recognize_printed_text_in_stream(file, language='en')
    if response.regions:
        text = ' '.join([line.text for region in response.regions for line in region.lines])
        return {"text": text}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receipt scanning failed")

# Function to calculate drive time using Google Maps API
def calculate_drive_time(origin: str, destination: str) -> int:
    directions_result = gmaps.directions(origin, destination, mode="driving")
    if directions_result:
        drive_time = directions_result[0]['legs'][0]['duration']['value'] // 60  # Convert seconds to minutes
        return drive_time
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Drive time calculation failed")

# Function to send push notifications via APNs
def send_push_notification(device_token: str, message: str):
    payload = Payload(alert=message, sound="default", badge=1)
    apns_client.send_notification(device_token, payload, topic='your_app_bundle_id')

# Machine learning models
task_time_model = LinearRegression()
employee_assignment_model = LinearRegression()
inventory_forecasting_model = LinearRegression()

# Function to train machine learning models
def train_models():
    # Example training data
    task_data = np.array([[1, 2, 3], [4, 5, 6]])
    task_labels = np.array([10, 20])
    employee_data = np.array([[1, 2, 3], [4, 5, 6]])
    employee_labels = np.array([1, 0])
    inventory_data = np.array([[1, 2, 3], [4, 5, 6]])
    inventory_labels = np.array([100, 200])

    task_time_model.fit(task_data, task_labels)
    employee_assignment_model.fit(employee_data, employee_labels)
    inventory_forecasting_model.fit(inventory_data, inventory_labels)

# Endpoint to create aggregated estimates
@app.post('/estimates', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
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

# Endpoint to create invoices
@app.post('/invoices', dependencies=[Depends(role_required(UserRole.OFFICE_ADMIN))])
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

# Function to generate order list when inventory levels are insufficient
def generate_order_list(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        # Example logic to generate order list
        order_list = ["item1", "item2", "item3"]
        return {"order_list": order_list}

if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)
    app.run(debug=True)
