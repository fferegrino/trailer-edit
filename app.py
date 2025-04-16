from flask import Flask, render_template, jsonify, send_from_directory, request
import os
import json

app = Flask(__name__)
app.config['IMAGES_FOLDER'] = '.output/images'
app.config['GROUPS_FILE'] = '.output/groups.json'

# Ensure images directory exists
os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)
os.makedirs(os.path.dirname(app.config['GROUPS_FILE']), exist_ok=True)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/')
def index():
    # Get list of images from the images directory
    images = []
    for filename in sorted(os.listdir(app.config['IMAGES_FOLDER'])):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            images.append({
                'filename': filename,
                'url': f'/images/{filename}'
            })
    
    # Load existing groups if they exist
    groups = []
    if os.path.exists(app.config['GROUPS_FILE']):
        with open(app.config['GROUPS_FILE'], 'r') as f:
            groups = json.load(f)
    
    return render_template('index.html', images=images, groups=groups)

@app.route('/save-groups', methods=['POST'])
def save_groups():
    groups = request.json
    with open(app.config['GROUPS_FILE'], 'w') as f:
        json.dump(groups, f, indent=2)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True) 