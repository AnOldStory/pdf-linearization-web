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

def process_pdf(input_filename, total_chunks):
    # 모든 청크를 하나로 합칩니다.
    with open(os.path.join(UPLOAD_FOLDER, input_filename), 'wb') as outfile:
        for num in range(total_chunks):
            part_path = os.path.join(UPLOAD_FOLDER, f"{input_filename}.part{num}")
            with open(part_path, 'rb') as part_file:
                outfile.write(part_file.read())
            os.remove(part_path)  # 청크 파일 삭제

    # PDF 파일 선형화
    output_filename = f"linearized_{input_filename}"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    # 최종 파일이 비어 있지 않은지 확인
    if os.path.getsize(os.path.join(UPLOAD_FOLDER, input_filename)) > 0:
        linearize_pdf(os.path.join(UPLOAD_FOLDER, input_filename), output_path)
    else:
        print("최종 파일이 비어 있습니다.")  # 디버깅용 메시지


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():

    # 현재까지의 청크 수 확인
    total_chunks = int(request.form.get('totalChunks', 0))
    chunk_number = int(request.form.get('chunkNumber', 0))
    filename = request.form.get('filename')  # 클라이언트에서 전송한 파일명

    if chunk_number == -1:
        process_pdf(filename, total_chunks)  # 쓰레드 제거하고 직접 호출
        output_filename = f"linearized_{filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)

    if 'file' not in request.files:
        return '파일이 없습니다.', 400

    file = request.files['file']

    if filename == '':
        return '파일명을 입력하세요.', 400

    # 파일명과 경로 설정
    input_path = os.path.join(UPLOAD_FOLDER, f"{filename}.part{chunk_number}")

    file.save(input_path)

    return '청크 업로드 완료', 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    output_filename = f"linearized_{filename}"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)

    return '파일이 존재하지 않습니다.', 404

if __name__ == '__main__':
    app.run(debug=True)
