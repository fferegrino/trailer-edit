from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__)
app.config['IMAGES_FOLDER'] = '.output/images'

# Ensure images directory exists
os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)

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
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True) 