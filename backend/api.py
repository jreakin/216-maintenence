from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from googlemaps import Client as GoogleMaps
from usps import USPSApi, Address
from google.cloud import vision
import boto3
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import datetime
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

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

# Role-based access control (RBAC) decorator
def role_required(role):
    def decorator(func):
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            user = User.query.filter_by(username=current_user).first()
            if user.role != role:
                return jsonify({"msg": "Access denied"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'], role=data['role'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# Task creation endpoint
@app.route('/tasks', methods=['POST'])
@role_required('Office Admin')
def create_task():
    data = request.get_json()
    new_task = Task(
        description=data['description'],
        location=data['location'],
        estimated_cost=data['estimated_cost'],
        status='Not Started',
        priority=data['priority'],
        deadline=datetime.datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"msg": "Task created successfully"}), 201

# Task update endpoint
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@role_required('Office Admin')
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    task.description = data['description']
    task.location = data['location']
    task.estimated_cost = data['estimated_cost']
    task.final_cost = data['final_cost']
    task.status = data['status']
    task.priority = data['priority']
    task.deadline = datetime.datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M:%S')
    task.dependencies = data['dependencies']
    task.comments = data['comments']
    task.attachments = data['attachments']
    db.session.commit()
    return jsonify({"msg": "Task updated successfully"}), 200

# Task prioritization endpoint
@app.route('/tasks/<int:task_id>/priority', methods=['PUT'])
@role_required('Dispatcher')
def prioritize_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    task.priority = data['priority']
    db.session.commit()
    return jsonify({"msg": "Task priority updated successfully"}), 200

# Address validation endpoint
@app.route('/validate_address', methods=['POST'])
@jwt_required()
def validate_address():
    data = request.get_json()
    address = data['address']
    # Validate address using Google Maps API
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        standardized_address = geocode_result[0]['formatted_address']
        return jsonify({"standardized_address": standardized_address}), 200
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
        return jsonify({"standardized_address": standardized_address}), 200
    return jsonify({"msg": "Address validation failed"}), 400

# Receipt scanning endpoint
@app.route('/scan_receipt', methods=['POST'])
@role_required('Office Admin')
def scan_receipt():
    file = request.files['file']
    # Use Google Cloud Vision API for receipt scanning
    image = vision.Image(content=file.read())
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return jsonify({"text": texts[0].description}), 200
    # Use Amazon Textract for receipt scanning
    response = textract.detect_document_text(Document={'Bytes': file.read()})
    if response['Blocks']:
        text = ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
        return jsonify({"text": text}), 200
    # Use Microsoft Azure Cognitive Services - Computer Vision API for receipt scanning
    response = computervision_client.recognize_printed_text_in_stream(file, language='en')
    if response.regions:
        text = ' '.join([line.text for region in response.regions for line in region.lines])
        return jsonify({"text": text}), 200
    return jsonify({"msg": "Receipt scanning failed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
