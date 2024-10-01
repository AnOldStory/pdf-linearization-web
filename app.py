from flask import Flask, request, send_file, render_template
import PyPDF2
import os

app = Flask(__name__)

# 파일 저장 경로
UPLOAD_FOLDER = 'files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def linearize_pdf(input_path, output_path):
    with open(input_path, 'rb') as infile:
        reader = PyPDF2.PdfReader(infile)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, 'wb') as outfile:
            writer.write(outfile)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '파일이 없습니다.', 400

    file = request.files['file']

    if file.filename == '':
        return '파일명을 입력하세요.', 400

    # 파일명과 경로 설정
    input_filename = file.filename
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_filename = f"linearized_{input_filename}"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    file.save(input_path)

    linearize_pdf(input_path, output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
