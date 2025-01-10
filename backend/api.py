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

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)

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

class TaskPriorityUpdate(BaseModel):
    priority: str

class AddressValidation(BaseModel):
    address: str

class ReceiptScan(BaseModel):
    file: bytes

# Role-based access control (RBAC) dependency
def role_required(role: str):
    def role_dependency(Authorize: AuthJWT = Depends()):
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        with Session(engine) as session:
            user = session.exec(select(User).where(User.username == current_user)).first()
            if user.role != role:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return role_dependency

# User registration endpoint
@app.post('/register', response_model=UserCreate)
def register(user: UserCreate):
    with Session(engine) as session:
        new_user = User(username=user.username, password=user.password, role=user.role)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

# User login endpoint
@app.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), Authorize: AuthJWT = Depends()):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or user.password != form_data.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = Authorize.create_access_token(subject=user.username)
        return {"access_token": access_token}

# Task creation endpoint
@app.post('/tasks', dependencies=[Depends(role_required('Office Admin'))])
def create_task(task: TaskCreate):
    with Session(engine) as session:
        new_task = Task(
            description=task.description,
            location=task.location,
            estimated_cost=task.estimated_cost,
            status='Not Started',
            priority=task.priority,
            deadline=task.deadline
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return new_task

# Task update endpoint
@app.put('/tasks/{task_id}', dependencies=[Depends(role_required('Office Admin'))])
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
        session.commit()
        session.refresh(existing_task)
        return existing_task

# Task prioritization endpoint
@app.put('/tasks/{task_id}/priority', dependencies=[Depends(role_required('Dispatcher'))])
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
@app.post('/scan_receipt', dependencies=[Depends(role_required('Office Admin'))])
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

if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)
    app.run(debug=True)
