from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
import os
import json
from werkzeug.utils import secure_filename
import shutil
import secrets
import webbrowser
import socket
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FILE'] = 'data/courses.json'
app.secret_key = secrets.token_hex(16)

# Ensure the upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize data file if it doesn't exist
if not os.path.exists(app.config['DATA_FILE']):
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump({"courses": []}, f)

def get_data():
    with open(app.config['DATA_FILE'], 'r') as f:
        return json.load(f)

def save_data(data):
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump(data, f, indent=2)

def is_first_run():
    data = get_data()
    return 'user_name' not in data

@app.route('/', methods=['GET', 'POST'])
def index():
    data = get_data()
    
    if is_first_run():
        if request.method == 'POST':
            user_name = request.form.get('user_name')
            data['user_name'] = user_name
            save_data(data)
            return redirect(url_for('index'))
        return render_template('welcome.html')
        
    return render_template('index.html', courses=data['courses'], user_name=data.get('user_name'))

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    data = get_data()
    
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_code = request.form.get('course_code')
        
        # Create new course
        new_course = {
            "id": len(data['courses']) + 1,
            "name": course_name,
            "code": course_code,
            "weeks": []
        }
        
        data['courses'].append(new_course)
        save_data(data)
        
        # Create course directory
        course_dir = os.path.join(app.config['UPLOAD_FOLDER'], course_code)
        os.makedirs(course_dir, exist_ok=True)
        
        return redirect(url_for('index'))
    
    return render_template('courses.html')

@app.route('/course/<course_id>')
def course_detail(course_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if not course:
        return redirect(url_for('index'))
    
    return render_template('course_detail.html', course=course)

@app.route('/course/<course_id>/add_week', methods=['POST'])
def add_week(course_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if not course:
        return redirect(url_for('index'))
    
    week_number = request.form.get('week_number')
    week_title = request.form.get('week_title')
    
    new_week = {
        "id": len(course['weeks']) + 1,
        "number": week_number,
        "title": week_title,
        "materials": []
    }
    
    course['weeks'].append(new_week)
    save_data(data)
    
    # Create week directory
    week_dir = os.path.join(app.config['UPLOAD_FOLDER'], course['code'], f"Week_{week_number}")
    os.makedirs(week_dir, exist_ok=True)
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/course/<course_id>/week/<week_id>')
def week_detail(course_id, week_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if not course:
        return redirect(url_for('index'))
    
    week = next((w for w in course['weeks'] if str(w['id']) == week_id), None)
    
    if not week:
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('week_detail.html', course=course, week=week)

@app.route('/course/<course_id>/week/<week_id>/upload', methods=['POST'])
def upload_material(course_id, week_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if not course:
        return redirect(url_for('index'))
    
    week = next((w for w in course['weeks'] if str(w['id']) == week_id), None)
    
    if not week:
        return redirect(url_for('course_detail', course_id=course_id))
    
    file = request.files.get('file')
    material_type = request.form.get('material_type')
    material_name = request.form.get('material_name')
    
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], course['code'], f"Week_{week['number']}")
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, filename))
        
        new_material = {
            "id": len(week['materials']) + 1,
            "name": material_name,
            "type": material_type,
            "filename": filename,
            "path": os.path.join(course['code'], f"Week_{week['number']}", filename)
        }
        
        week['materials'].append(new_material)
        save_data(data)
    
    return redirect(url_for('week_detail', course_id=course_id, week_id=week_id))

@app.route('/download/<path:filepath>')
def download_file(filepath):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filepath, as_attachment=True)

@app.route('/delete/course/<course_id>', methods=['POST'])
def delete_course(course_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if course:
        # Remove course directory
        course_dir = os.path.join(app.config['UPLOAD_FOLDER'], course['code'])
        if os.path.exists(course_dir):
            shutil.rmtree(course_dir)
        
        # Remove from data
        data['courses'] = [c for c in data['courses'] if str(c['id']) != course_id]
        save_data(data)
    
    return redirect(url_for('index'))

@app.route('/delete/week/<course_id>/<week_id>', methods=['POST'])
def delete_week(course_id, week_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if course:
        week = next((w for w in course['weeks'] if str(w['id']) == week_id), None)
        
        if week:
            # Remove week directory
            week_dir = os.path.join(app.config['UPLOAD_FOLDER'], course['code'], f"Week_{week['number']}")
            if os.path.exists(week_dir):
                shutil.rmtree(week_dir)
            
            # Remove from data
            course['weeks'] = [w for w in course['weeks'] if str(w['id']) != week_id]
            save_data(data)
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/delete/material/<course_id>/<week_id>/<material_id>', methods=['POST'])
def delete_material(course_id, week_id, material_id):
    data = get_data()
    course = next((c for c in data['courses'] if str(c['id']) == course_id), None)
    
    if course:
        week = next((w for w in course['weeks'] if str(w['id']) == week_id), None)
        
        if week:
            material = next((m for m in week['materials'] if str(m['id']) == material_id), None)
            
            if material:
                # Remove file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], material['path'])
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove from data
                week['materials'] = [m for m in week['materials'] if str(m['id']) != material_id]
                save_data(data)
    
    return redirect(url_for('week_detail', course_id=course_id, week_id=week_id))


@app.route('/generate-qr')
def generate_qr():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    url = f"http://{local_ip}:5000"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr_code': img_str})


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    
    # Get local IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Open browser
    webbrowser.open(f'http://{local_ip}:{port}')
    
    # Run the app
    app.run(host=host, port=port, debug=True)
