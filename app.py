from flask import Flask, request, jsonify
import subprocess
import os
import time

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
STYLE_FOLDER = os.path.join(BASE_DIR, 'style')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(STYLE_FOLDER, exist_ok=True)


@app.route('/transfer', methods=['POST'])
def transfer():
    start_time = time.time()

    if 'content' not in request.files or 'style' not in request.form:
        return jsonify({'error': 'Content image and style name are required'}), 400

    content_image = request.files['content']
    style_name = request.form['style']

    alpha = request.form.get('alpha', 1.0)

    content_filename = content_image.filename
    content_path = os.path.join(UPLOAD_FOLDER, content_filename)
    style_path = os.path.join(STYLE_FOLDER, f'{style_name}.jpg')

    content_image.save(content_path)

    result_filename = f'{os.path.splitext(content_filename)[0]}_{style_name}.jpg'
    result_path = os.path.join(RESULTS_FOLDER, result_filename)

    print(f"Content path: {content_path}")
    print(f"Style path: {style_path}")
    print(f"Result path: {result_path}")

    command = f"python test.py --content={content_path} --style={style_path} --result_path={RESULTS_FOLDER} " \
              f"--alpha={alpha}"
    process = subprocess.run(command, shell=True, capture_output=True)

    if process.returncode != 0:
        return jsonify({'error': process.stderr.decode('utf-8')}), 500

    end_time = time.time()
    running_time = end_time - start_time

    print(f"Running time: {running_time} seconds")

    response = {
        'image': result_path
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
