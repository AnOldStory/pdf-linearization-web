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
    chunk_number = request.form.get('chunkNumber', 0)
    input_path = os.path.join(UPLOAD_FOLDER, f"{input_filename}.part{chunk_number}")

    file.save(input_path)

    # 모든 청크가 업로드되었는지 확인
    if all(os.path.exists(os.path.join(UPLOAD_FOLDER, f"{input_filename}.part{num}")) for num in range(int(chunk_number) + 1)):
        # 모든 청크를 하나로 합칩니다.
        with open(os.path.join(UPLOAD_FOLDER, input_filename), 'wb') as outfile:
            for num in range(int(chunk_number) + 1):
                part_path = os.path.join(UPLOAD_FOLDER, f"{input_filename}.part{num}")
                with open(part_path, 'rb') as part_file:
                    outfile.write(part_file.read())
                os.remove(part_path)  # 청크 파일 삭제

        # PDF 파일 선형화
        output_filename = f"linearized_{input_filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        linearize_pdf(os.path.join(UPLOAD_FOLDER, input_filename), output_path)

        return send_file(output_path, as_attachment=True)

    return '청크 업로드 완료', 200

if __name__ == '__main__':
    app.run(debug=True)
