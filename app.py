from flask import Flask, request, send_file, jsonify
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
STYLE_FOLDER = os.path.join(BASE_DIR, 'style')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(STYLE_FOLDER, exist_ok=True)

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'content' not in request.files or 'style' not in request.form:
        return jsonify({'error': 'Content image and style name are required'}), 400

    content_image = request.files['content']
    style_name = request.form['style']

    # Optional parameters
    alpha = request.form.get('alpha', 1.0)

    # Save the content image
    content_filename = content_image.filename + '.jpg'
    content_path = os.path.join(UPLOAD_FOLDER, content_filename)
    style_path = os.path.join(STYLE_FOLDER, f'{style_name}.jpg')  # Assuming style images are in 'style' directory

    content_image.save(content_path)

    # Define the result file path
    result_filename = f'{os.path.splitext(content_filename)[0]}_{style_name}.jpg'
    result_path = os.path.join(RESULTS_FOLDER, result_filename)

    # Print paths for debugging
    print(f"Content path: {content_path}")
    print(f"Style path: {style_path}")
    print(f"Result path: {result_path}")

    # Run the style transfer script
    command = f"python test.py --content={content_path} --style={style_path} --result_path={RESULTS_FOLDER} " \
              f"--alpha={alpha}"
    process = subprocess.run(command, shell=True, capture_output=True)

    # Check for errors
    if process.returncode != 0:
        return jsonify({'error': process.stderr.decode('utf-8')}), 500

    # Send the generated image
    return send_file(result_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
