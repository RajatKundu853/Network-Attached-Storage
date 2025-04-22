from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, abort, jsonify, send_file, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import shutil
import json
import mimetypes

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["UPLOAD_FOLDER"] = os.path.abspath("./NAS")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User database (Replace with a real database in production)
USERS = {"admin": "password123"}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in USERS else None

# NAS paths
NAS_DIR = os.path.abspath("./NAS")
BASE_DIR = NAS_DIR
TRASH_DIR = os.path.join(NAS_DIR, ".trash")
TRASH_METADATA_FILE = os.path.join(TRASH_DIR, "trash_metadata.json")

# Ensure trash and metadata file exists
os.makedirs(TRASH_DIR, exist_ok=True)
if not os.path.exists(TRASH_METADATA_FILE):
    with open(TRASH_METADATA_FILE, "w") as f:
        json.dump({}, f)

def load_trash_metadata():
    with open(TRASH_METADATA_FILE, "r") as f:
        return json.load(f)

def save_trash_metadata(data):
    with open(TRASH_METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
@app.route("/browse/", defaults={"subpath": ""})
@app.route("/browse/<path:subpath>")
@login_required
def browse(subpath=""):
    full_path = os.path.join(NAS_DIR, subpath)

    if not os.path.abspath(full_path).startswith(NAS_DIR):
        abort(403, "Access denied!")

    if not os.path.exists(full_path):
        return "Directory not found!", 404

    files = os.listdir(full_path)
    file_list = [
        {"name": file, "is_dir": os.path.isdir(os.path.join(full_path, file))}
        for file in files
        if file != ".trash"
    ]

    return render_template("index.html", files=file_list, subpath=subpath)

@app.route("/create_folder", methods=["POST"])
@login_required
def create_folder():
    data = request.json
    subpath = data.get("subpath", "")
    folder_name = data.get("folder_name", "")

    if not folder_name:
        return jsonify({"error": "Folder name required"}), 400

    new_folder_path = os.path.join(NAS_DIR, subpath, folder_name)

    if not os.path.abspath(new_folder_path).startswith(NAS_DIR):
        abort(403)

    if os.path.exists(new_folder_path):
        return jsonify({"error": "Folder already exists"}), 409

    os.makedirs(new_folder_path)
    return jsonify({"success": True, "message": f"Folder '{folder_name}' created successfully!"})

@app.route("/download/<path:subpath>")
@login_required
def download(subpath):
    file_path = os.path.join(NAS_DIR, subpath)

    if not os.path.abspath(file_path).startswith(NAS_DIR):
        abort(403)

    if os.path.exists(file_path):
        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)
    else:
        return "File not found!", 404

@app.route("/upload", defaults={"subpath": ""}, methods=["POST"])
@app.route("/upload/<path:subpath>", methods=["POST"])
@login_required
def upload_file(subpath=""):
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    save_path = os.path.join(NAS_DIR, subpath) if subpath else NAS_DIR
    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, file.filename)

    if os.path.exists(file_path):
        return jsonify({"exists": True, "filename": file.filename}), 409

    file.save(file_path)
    return jsonify({"success": True, "filename": file.filename})

@app.route("/rename", methods=["POST"])
@login_required
def rename():
    data = request.json
    path = os.path.join(NAS_DIR, data["path"])
    new_name = data["new_name"]

    if not os.path.abspath(path).startswith(NAS_DIR):
        abort(403)

    new_path = os.path.join(os.path.dirname(path), new_name)

    if os.path.exists(new_path):
        return jsonify({"error": "File/folder with new name already exists."}), 409

    os.rename(path, new_path)
    return jsonify({"success": True, "message": f"Renamed to {new_name}"})

@app.route('/soft_delete', methods=['POST'])
@login_required
def soft_delete():
    data = request.get_json()
    rel_path = data.get('path')
    abs_path = os.path.join(BASE_DIR, rel_path)

    if not os.path.exists(abs_path):
        return jsonify({'error': f'File not found: {rel_path}'}), 404

    filename = os.path.basename(abs_path)
    trash_path = os.path.join(TRASH_DIR, filename)

    try:
        shutil.move(abs_path, trash_path)
    except Exception as e:
        return jsonify({'error': f'Failed to move: {str(e)}'}), 500

    with open(TRASH_METADATA_FILE, 'r+') as f:
        metadata = json.load(f)
        metadata[filename] = rel_path
        f.seek(0)
        json.dump(metadata, f)
        f.truncate()

    return jsonify({
    'status': 'success',
    'message': '✅ File moved to trash successfully!'
     })


@app.route("/trash")
@login_required
def view_trash():
    trash_metadata = load_trash_metadata()
    files = [{"name": name, "original": trash_metadata[name]} for name in trash_metadata]
    return render_template("trash.html", files=files)

@app.route("/restore", methods=["POST"])
@login_required
def restore_item():
    data = request.json
    filename = data["filename"]

    trash_metadata = load_trash_metadata()
    if filename not in trash_metadata:
        return jsonify({"error": "Item not found in Trash"}), 404

    original_path = os.path.join(NAS_DIR, trash_metadata[filename])
    os.makedirs(os.path.dirname(original_path), exist_ok=True)
    shutil.move(os.path.join(TRASH_DIR, filename), original_path)

    del trash_metadata[filename]
    save_trash_metadata(trash_metadata)

    return jsonify({"success": True, "message": "Item restored successfully!"})

@app.route("/permanent_delete", methods=["POST"])
@login_required
def permanent_delete():
    data = request.json
    filename = data["filename"]

    trash_metadata = load_trash_metadata()
    trash_file_path = os.path.join(TRASH_DIR, filename)

    try:
        if os.path.isfile(trash_file_path):
            os.remove(trash_file_path)
        elif os.path.isdir(trash_file_path):
            shutil.rmtree(trash_file_path)  # Deletes folder and its contents

        if filename in trash_metadata:
            del trash_metadata[filename]
            save_trash_metadata(trash_metadata)

        return jsonify({"success": True, "message": "Item permanently deleted!"})

    except Exception as e:
        return jsonify({"error": f"Deletion failed: {str(e)}"}), 500

@app.route('/media/<path:filepath>')
@login_required
def serve_file(filepath):
    full_path = os.path.abspath(os.path.join(BASE_DIR, filepath))
    if not full_path.startswith(BASE_DIR) or not os.path.exists(full_path):
        abort(404)
    return send_file(full_path)

@app.route('/preview/<path:filepath>')
@login_required
def preview_file(filepath):
    full_path = os.path.join(BASE_DIR, filepath)

    if not os.path.exists(full_path):
        return abort(404)

    ext = os.path.splitext(filepath)[1].lower()

    if ext in ['.txt', '.py']:
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return render_template_string(f'''
                                          <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>     
                <button onclick="window.history.back()">⬅ Go Back</button>             
                <h3>📄 Text Preview</h3>
                <pre style="white-space: pre-wrap; border:1px solid #ccc; padding:10px;">{content}</pre>
            ''')
        except Exception as e:
            return f"⚠️ Error reading file: {str(e)}", 500

    elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
        return render_template_string(f'''
                                      <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>
            <button onclick="window.history.back()">⬅ Go Back</button>
            <h3>🖼️ Image Preview</h3>
            <img src="/media/{filepath}" style="max-width:100%;" />
        ''')

    elif ext == '.pdf':
        return render_template_string(f'''
                                      <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>
            <button onclick="window.history.back()">⬅ Go Back</button>
            <h3>📄 PDF Preview</h3>
            <embed src="/media/{filepath}" type="application/pdf" width="100%" height="600px"/>
        ''')

    elif ext in ['.mp4', '.webm']:
        mime_type, _ = mimetypes.guess_type(full_path)
        return render_template_string(f'''
                                      <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>
            <button onclick="window.history.back()">⬅ Go Back</button>
            <h3>🎥 Video Preview</h3>
            <video width="100%" height="auto" controls>
                <source src="/media/{filepath}" type="{mime_type}">
                Your browser does not support the video tag.
            </video>
        ''')

    elif ext in ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']:
        return render_template_string(f'''
                                      <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>
            <button onclick="window.history.back()">⬅ Go Back</button>
            <h3>📄 Document Preview (Online)</h3>
            <iframe src="https://view.officeapps.live.com/op/embed.aspx?src={{request.url_root}}media/{filepath}" 
                    width="100%" height="600px" frameborder="0"></iframe>
        ''')

    else:
        return render_template_string(f'''
    <style>
        body {{
            background-color: #0d0d0d;
            color: #00ffcc;
            font-family: "Courier New", monospace;
            text-align: center;
            padding-top: 50px;
        }}
        button {{
            background: #00ffcc;
            color: #0d0d0d;
            font-weight: bold;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 0 10px #00ffcc;
            transition: 0.3s;
        }}
        button:hover {{
            background: #008080;
            box-shadow: 0 0 15px #00ffcc;
        }}
    </style>
    <h3>⚠️ Preview Not Available</h3>
    <p>This file type is not supported for preview.</p>
    <button onclick="/download/{filepath}" download>⬇️ Click to Download</button><br><br>
    <button onclick="window.history.back()">⬅ Go Back</button>
''')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS and USERS[username] == password:
            login_user(User(username))
            return redirect(url_for("browse"))
        flash("Invalid credentials. Try again.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    os.makedirs(NAS_DIR, exist_ok=True)
    os.makedirs(TRASH_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=True)
