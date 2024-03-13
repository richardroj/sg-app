from flask import Flask, render_template, json, request, redirect, url_for, jsonify, send_file
from replacement_strings import replacement_strings
import os
import time
from threading import Thread
import threading
from werkzeug.utils import secure_filename


app = Flask(__name__)

replacement_strings = replacement_strings
current_filename = None
current_brand = None
current_ecu = None
current_engine = None
progress = 0
download_url = None
UPLOAD_FOLDER = './templates/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "secret_key"
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['APPLICATION_ROOT'] = '/'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/processFile/<filename>')
def processFile(filename):
    list(replacement_strings.keys())
    brands = list(replacement_strings.keys())

    return render_template('process_file.html', brands=brands)

@app.route('/getEcu/<brand>')
def getEcu(brand):
    return list(replacement_strings.get(brand, {}).keys())

@app.route('/getEngine/brand/<brand>/ecu/<ecu>')
def getEngine(brand, ecu):
    return list(replacement_strings.get(brand, {}).get(ecu, {}).keys())
   

@app.route("/upload", methods=['POST'])
def uploader():
 global current_filename
 if request.method == 'POST':
  f = request.files['archivo']
  filename = secure_filename(f.filename)
  current_filename = filename 
  f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  return redirect(url_for('processFile', filename=filename))
 
@app.route("/process", methods=['POST'])
def process():
 print("process file")
 if request.method == 'POST':
  brand = request.form['brand']
  ecu = request.form['ecu']
  engine = request.form['engine']
  #file_replaced = search_and_replace(brand, ecu, engine, file_path = current_filename)
  #print("file generated: "+ file_replaced)
  threading.Thread(target=search_and_replace, args=(brand, ecu, engine, current_filename)).start()

  return redirect(url_for('result'))


def search_and_replace(brand, ecu, engine, file_path):
        global progress
        global download_url
        with app.app_context():
            file_path = app.config['UPLOAD_FOLDER']+"/"+current_filename
            print("replacing file otro", file_path, brand, ecu, engine)
            if not file_path or file_path is None:
                
                return "Error"

            if not brand or not ecu or not engine:
                return "Error", "Por favor, selecciona una marca, ECU y motor."

            replacements = []

            strings = replacement_strings.get(brand, {}).get(ecu, {}).get(engine, {})
            print("strings", strings)
            for name, values in strings.items():
                search_string = values.get("search_string", b"")
                replace_string = values.get("replace_string", b"")
                threshold = 0.7  # Umbral de similitud para la búsqueda de cadenas
                replacements.append((search_string, replace_string, threshold, name))

            block_size = 8192  # Tamaño del bloque de lectura/escritura
            output_file_path = os.path.splitext(file_path)[0] + "_modified" + os.path.splitext(file_path)[1]

            with open(file_path, "rb") as input_file:
                with open(output_file_path, "wb") as output_file:
                    total_size = os.path.getsize(file_path)
                    processed_size = 0
                    print("modifiying file")
                    while True:
                        block_content = bytearray(input_file.read(block_size))
                        if not block_content:
                            break

                        block_content = process_block(block_content, replacements)

                        output_file.write(block_content)

                        processed_size += len(block_content)
                        progress = int(processed_size / total_size * 100)
                        #update_progress()

                    #update_progress()
                    #self.show_result("Búsqueda y reemplazo completados. Nuevo archivo generado en: " + output_file_path)
            if progress == 100:
                download_url = url_for('download_file', filename=os.path.basename(output_file_path))


def process_block(block_content, replacements):
    for search_string, replace_string, threshold, _ in replacements:
        search_size = len(search_string)
        i = 0
        while i < len(block_content) - search_size + 1:
            window = block_content[i:i + search_size]
            similarity = sum(a == b for a, b in zip(window, search_string)) / search_size
            if similarity >= threshold:
                block_content[i:i + search_size] = replace_string
                i += search_size
            else:
                i += 1
    return block_content

@app.route('/download/<filename>')
def download_file(filename):

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "El archivo no existe."


@app.route('/get_progress')
def get_progress():
    global progress
    return jsonify(progress=progress)

@app.route('/get_download_url')
def get_download_url():
    global download_url
    return jsonify(download_url=download_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
