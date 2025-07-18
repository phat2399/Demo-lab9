import os
import boto3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Lấy thông tin nhạy cảm từ biến môi trường do Kubernetes cung cấp
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_REGION', 'ap-southeast-1')

# Khởi tạo client S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION
)

# Giao diện HTML của trang web
HTML_TEMPLATE = """
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Upload File lên AWS S3 với Kubernetes</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e9ecef; color: #495057; text-align: center; padding-top: 5rem; }
        .container { max-width: 500px; margin: auto; background: white; padding: 2rem; border-radius: 0.5rem; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1); }
        h1 { color: #007bff; }
        input[type=file] { display: block; margin: 1.5rem auto; }
        input[type=submit] { background-color: #007bff; color: white; padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; cursor: pointer; font-size: 1rem; }
        input[type=submit]:hover { background-color: #0056b3; }
        .result { margin-top: 2rem; }
        a { color: #28a745; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload File lên AWS S3</h1>
        <p>Ứng dụng chạy trên Kubernetes</p>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        {% if file_url %}
            <div class="result">
                <p>✅ Upload thành công nheeee!!!</p>
                <a href="{{ file_url }}" target="_blank">Xem file đã upload</a>
            </div>
        {% endif %}
        {% if error %}
            <p style="color: red;">❌ Lỗi: {{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    file_url = None
    error_msg = None
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            error_msg = "Vui lòng chọn một file."
        else:
            file = request.files['file']
            try:
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET_NAME,
                    file.filename,
                    ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
                )
                file_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
            except Exception as e:
                error_msg = str(e)

    return render_template_string(HTML_TEMPLATE, file_url=file_url, error=error_msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)