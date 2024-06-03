from flask import Flask, request, jsonify, flash, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from PIL import Image
import requests
from datetime import timedelta
import base64
from werkzeug.utils import secure_filename
from io import BytesIO
from models.models import Users, SelectedUnit, ImageStats
from database import db, cast, func, Integer, Float
from flask_cors import CORS
import json
from fuzzywuzzy import process
import pytesseract
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
myApiUser = os.getenv('E7_DB_KEY')

script_dir = os.path.dirname(os.path.abspath(__file__))
tesseract_path = os.path.join(script_dir, 'Pytesseract', 'tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

bcrypt = Bcrypt(app)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def home():
    return jsonify({"message": "Welcome to E7 Armory API"})

@app.route("/signup", methods=['POST'])
def signup():
    form = request.get_json()
    if form:
        user = Users(username=form['username'], epic_seven_account=form['epic_seven_account'], streamer_name=form['streamer_name'], rta_rank=form['rta_rank'])
        user.set_password(form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({"message": "User created successfully"}), 201
    return jsonify({"errors": "Form data is invalid"}), 400

@app.route("/login", methods=['POST'])
def login():
    form = request.get_json()
    if form:
        user = Users.query.filter_by(username=form['username']).first()
        if user and user.check_password(form['password']):
            login_user(user)
            return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get_unit_names', methods=['GET'])
def get_unit_names():
    api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
    unit_names = load_unit_names(api_url, 'en')
    unit_names.sort()
    return jsonify(unit_names)

def load_unit_names(api_url, language_code='en'):
    # Load unit names from an API based on the given language code
    response = requests.get(api_url)
    data = response.json()
    unit_names = [unit['name'] for unit in data[language_code]]
    unit_names.sort()
    return unit_names

api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
correct_unit_names = load_unit_names(api_url, 'en')

def fetch_unit_data(unit_name):
    #Fixes unit name edge case, uses e7db to get needed stats 
    if unit_name == "Ainos 2.0":
        formatted_unit_name = "ainos-20"
    else:
        formatted_unit_name = unit_name.replace(' ', '-')

    api_url = f'https://epic7db.com/api/heroes/{formatted_unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def fetch_unit_image(unit_name):
    # Fetch the unit image URL from the new API. Thank you to Epic7db.com
    unit_name = unit_name.replace(' ', '-').lower()
    api_url = f'https://epic7db.com/api/heroes/{unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('image', '')
    return ''   

def correct_name(extracted_name, choices):
    # Correct the extracted name by finding the best match from the choices
    best_match, score = process.extractOne(extracted_name, choices)
    if score > 80:
        return best_match
    return None

@app.route('/display', methods=['GET'])
@login_required
def display_image():
    # Display the image and extracted stats
    filenames = session.get('filenames', [])
    image_urls = session.get('image_urls', [])
    username = current_user.username
    rta_rank = current_user.rta_rank

    print('Filenames:', filenames)

    if not filenames and not image_urls:
        print('No filenames or image URLs found in session.')
        return jsonify({"error": "No images found"}), 400

    results = []

    regions = {
        'unit': {'x': 150, 'y': 170, 'width': 700, 'height': 60},
        'cp': {'x': 207, 'y': 555, 'width': 200, 'height': 50},
        'imprint': {'x': 275, 'y': 360, 'width': 190, 'height': 100},
        'attack': {'x': 385, 'y': 620, 'width': 100, 'height': 29},
        'defense': {'x': 385, 'y': 650, 'width': 100, 'height': 29}, 
        'health': {'x': 385, 'y': 680, 'width': 100, 'height': 29},
        'speed': {'x': 385, 'y': 720, 'width': 100, 'height': 29}, 
        'critical_hit_chance': {'x': 385, 'y': 750, 'width': 100, 'height': 29}, 
        'critical_hit_damage': {'x': 385, 'y': 785, 'width': 100, 'height': 34},
        'effectiveness':  {'x': 385, 'y': 820, 'width': 100, 'height': 34}, 
        'effect_resistance': {'x': 385, 'y': 850, 'width': 100, 'height': 34},
        'set1': {'x': 210, 'y': 942, 'width': 200, 'height': 34},
        'set2':  {'x': 210, 'y': 976, 'width': 200, 'height': 34}, 
        'set3': {'x': 210, 'y': 1010, 'width': 200, 'height': 34}
    }

    for filename in filenames:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = Image.open(image_path)
        process_image(image, regions, results, username, rta_rank)

        db.session.commit()
        
        return jsonify(results), 200

def process_image(image, regions, results, username, rta_rank):
    # Extract stats from the image, correct the unit name, and save to the database
    stats = {name: pytesseract.image_to_string(image.crop((data['x'], data['y'], data['x'] + data['width'], data['y'] + data['height'])), config='--psm 6') for name, data in regions.items()}

    if 'unit' in stats:
        corrected_name = correct_name(stats['unit'], correct_unit_names)
        if corrected_name:
            stats['unit'] = corrected_name
        else:
            print("No matching unit name found or low confidence match for:", stats['unit'])

    new_stats = ImageStats(**stats)
    new_stats.uploaded_by = username
    new_stats.user_rank = rta_rank

    db.session.add(new_stats)
    results.append(new_stats.to_dict())

@app.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    files = request.files.getlist('file')
    filenames = []
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filenames.append(filename)
    
    session['filenames'] = filenames

    return jsonify({"message": "Files uploaded successfully"}), 200

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        form = request.get_json()
        if form:
            current_user.username = form['username']
            current_user.epic_seven_account = form['epic_seven_account']
            current_user.streamer_name = form['streamer_name']
            current_user.rta_rank = form['rta_rank']
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        return jsonify({"errors": "Form data is invalid"}), 400
    else:
        user_data = {
            "username": current_user.username,
            "epic_seven_account": current_user.epic_seven_account,
            "streamer_name": current_user.streamer_name,
            "rta_rank": current_user.rta_rank
        }
        return jsonify(user_data), 200

@app.route('/build_finder', methods=['POST'])
@login_required
def build_finder():
    data = request.json  # Use request.json to handle JSON payloads
    selected_unit = data.get('unit')
    selected_rank = data.get('rank').lower()

    average_stats = db.session.query(
    func.avg(cast(ImageStats.attack, Float)).label('avg_attack'),
    func.avg(cast(ImageStats.defense, Float)).label('avg_defense'),
    func.avg(cast(ImageStats.health, Float)).label('avg_health'),
    func.avg(cast(ImageStats.speed, Float)).label('avg_speed'),
    func.avg(cast(func.replace(ImageStats.critical_hit_chance, '%', ''), Float)).label('avg_crit_chance'),
    func.avg(cast(func.replace(ImageStats.critical_hit_damage, '%', ''), Float)).label('avg_crit_damage'),
    func.avg(cast(func.replace(ImageStats.effectiveness, '%', ''), Float)).label('avg_effectiveness'),
    func.avg(cast(func.replace(ImageStats.effect_resistance, '%', ''), Float)).label('avg_effect_resistance'),
    func.mode().within_group(ImageStats.set1).label('most_common_set1'),
    func.mode().within_group(ImageStats.set2).label('most_common_set2'),
    func.mode().within_group(ImageStats.set3).label('most_common_set3')
).filter(
    ImageStats.unit == selected_unit,
    ImageStats.user_rank == selected_rank
).first()

    if average_stats.avg_crit_chance is None:
        return jsonify({'message': 'No data found for the selected unit and rank.'}), 404
    print (average_stats)
    return jsonify({
        'attack': average_stats[0],
        'defense': average_stats[1],
        'health': average_stats[2],
        'speed': average_stats[3],
        'critical_hit_chance': average_stats[4],
        'critical_hit_damage': average_stats[5],
        'effectiveness': average_stats[6],
        'effect_resistance': average_stats[7],
        'set1': average_stats[8],
        'set2': average_stats[9],
        'set3': average_stats[10]
    })


@app.route('/your_units', methods=['GET', 'POST'])
@login_required
def your_units():
    if request.method == 'GET':
        units = ImageStats.query.filter_by(uploaded_by=current_user.username).all()
        units.sort(key=lambda x: x.unit)
        units_data = [unit.to_dict() for unit in units]
        return jsonify(units_data), 200
    
    if request.method == 'POST':
        form = request.get_json()
        unit_name = form.get('unit')
        unit = ImageStats.query.filter_by(uploaded_by=current_user.username, unit=unit_name).first()
        if unit:
            return jsonify(unit.to_dict()), 200
        return jsonify({"error": "Unit not found"}), 404

    
    return jsonify({"error": "Invalid request method"}), 400

@app.route('/delete_unit', methods=['POST'])
@login_required
def delete_unit():
    data = request.get_json()
    unit_id = data.get('unit_to_delete')
    if unit_id:
        unit = ImageStats.query.get(unit_id)
        db.session.delete(unit)
        db.session.commit()
        return jsonify({"message": "Unit deleted successfully"}), 200
    
    return jsonify({"error": "Unit not found or not authorized"}), 404

@app.route('/get_unit_data', methods=['GET'])
@login_required
def get_unit_data():
    units = ImageStats.query.filter_by(uploaded_by=current_user.username).all()
    units_data = [{'id': unit.id, 'name': unit.unit, 'health': unit.health, 'attack': unit.attack, 'defense': unit.defense, 'speed': unit.speed,
                   'critical_hit_chance': unit.critical_hit_chance, 'critical_hit_damage': unit.critical_hit_damage, 'effectiveness': unit.effectiveness,
                   'effect_resistance': unit.effect_resistance} for unit in units]
    units_data = sorted(units_data, key=lambda x: x['name'])
    print(units_data)
    return jsonify(units_data)

@app.route('/update_selected_units', methods=['POST'])
@login_required
def update_selected_units():
    #Api call for twitch overlay to update the units needed for overlay to the db
    data = request.json
    selected_units = data.get('units', [])
    print(selected_units)
    units = selected_units + [{}] * (4 - len(selected_units))

    unit_id1 = units[0].get('id', None)
    unit_id2 = units[1].get('id', None)
    unit_id3 = units[2].get('id', None)
    unit_id4 = units[3].get('id', None)

    # Clear existing selected units for the user
    SelectedUnit.query.filter_by(user_id=current_user.id).delete()
    
    new_unit = SelectedUnit(
        user_id=current_user.id,
        unit_id1=unit_id1,
        unit_id2=unit_id2,
        unit_id3=unit_id3,
        unit_id4=unit_id4
    )
    db.session.add(new_unit)
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/api/get_selected_units_data', methods=['GET'])
@jwt_required()
def get_selected_units_data():
    #Electron page calls the db for the selected units 
    # current_user_id = get_jwt_identity()
    # user = Users.query.get(current_user_id)
    units_data = []
    
    selected_units = SelectedUnit.query.filter_by(user_id=1).first()
    
    if not selected_units:
        return jsonify({'error': 'No selected units found'}), 404
    
    unit_ids = [selected_units.unit_id1, selected_units.unit_id2, selected_units.unit_id3, selected_units.unit_id4]
    
    unit_ids = [uid for uid in unit_ids if uid is not None and uid != 0]

    for unit_id in unit_ids:
        unit_obj = ImageStats.query.get(unit_id)
        if unit_obj:
            units_data.append({
                'id': unit_obj.id,
                'name': unit_obj.unit,
                'health': unit_obj.health,
                'attack': unit_obj.attack,
                'defense': unit_obj.defense,
                'speed': unit_obj.speed,
                'critical_hit_chance': unit_obj.critical_hit_chance,
                'critical_hit_damage': unit_obj.critical_hit_damage,
                'effectiveness': unit_obj.effectiveness,
                'effect_resistance': unit_obj.effect_resistance,
                'set1': unit_obj.set1,
                'set2': unit_obj.set2,
                'set3': unit_obj.set3
            })
        else:
            print(f'Unit with id {unit_id} not found in the database')

    print('Units data:', units_data)
    return jsonify(units_data)

@app.route('/generate_token', methods=['GET'])
def generate_token():
    # Specify the identity of the user for whom you want to generate the token
    user_id = 'faugnom1'
    
    # Generate the token
    token = create_access_token(identity=user_id)
    print(token)
    return jsonify(token=token)


if __name__ == '__main__':
    app.run(debug=True)
