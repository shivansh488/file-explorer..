from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import shutil
from datetime import datetime
import mimetypes

app = Flask(__name__)


ROOT_DIR = os.path.expanduser("~")  

def get_file_details(path):
    """Get detailed information about a file"""
    stat = os.stat(path)
    return {
        'size': f"{stat.st_size:,} bytes",
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        'type': mimetypes.guess_type(path)[0] or 'Unknown'
    }

@app.route('/', defaults={'path': ''})
@app.route('/browse', defaults={'path': ''})
@app.route('/browse/<path:path>')
def browse(path):
    abs_path = os.path.join(ROOT_DIR, path)
    if not os.path.exists(abs_path):
        return "Path does not exist", 404

    if os.path.isfile(abs_path):
        return render_template('file_details.html', 
                            file_path=path,
                            file_name=os.path.basename(path),
                            details=get_file_details(abs_path))

    files = []
    with os.scandir(abs_path) as entries:
        for entry in entries:
            files.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'size': f"{entry.stat().st_size:,} bytes" if entry.is_file() else "",
                'modified': datetime.fromtimestamp(entry.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return render_template('index.html', 
                         files=files, 
                         current_path=path,
                         parent_path=os.path.dirname(path))

@app.route('/delete', methods=['POST'])
def delete():
    path = request.form['path']
    abs_path = os.path.join(ROOT_DIR, path)
    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/rename', methods=['POST'])
def rename():
    path = request.form['path']
    new_name = request.form['new_name']
    abs_path = os.path.join(ROOT_DIR, path)
    new_abs_path = os.path.join(ROOT_DIR, os.path.dirname(path), new_name)
    try:
        os.rename(abs_path, new_abs_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload', methods=['POST'])
def upload_file():
    path = request.form.get('path', '')
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    try:
        filename = secure_filename(file.filename)
        save_path = os.path.join(ROOT_DIR, path, filename)
        file.save(save_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=None)
    
    results = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for name in files + dirs:
            if query.lower() in name.lower():
                rel_path = os.path.relpath(os.path.join(root, name), ROOT_DIR)
                results.append({
                    'name': name,
                    'path': rel_path,
                    'is_dir': os.path.isdir(os.path.join(root, name))
                })
    
    return render_template('search.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
