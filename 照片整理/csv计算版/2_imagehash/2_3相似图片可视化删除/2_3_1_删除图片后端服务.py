from flask import Flask, request, jsonify, send_file
from send2trash import send2trash
from flask_cors import CORS
import os
import hashlib
from PIL import Image
import logging

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 禁用 Flask 默认日志
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 临时文件存储路径
TEMP_IMAGE_PATH = "./temp_images"

# 创建临时文件夹
os.makedirs(TEMP_IMAGE_PATH, exist_ok=True)


def calculate_md5(file_path):
    """计算文件路径的 MD5 值"""
    md5_hash = hashlib.md5(file_path.encode()).hexdigest()
    return md5_hash


@app.route('/file-size', methods=['GET'])
def file_size():
    file_path = request.args.get('filePath')
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'size': 1}), 200

        size = os.path.getsize(file_path)
        return jsonify({'size': size}), 200
    except Exception as e:
        print("图片大小获取异常", e)
        return jsonify({'error': str(e)}), 500


@app.route('/convert-image', methods=['GET'])
def convert_image():
    file_path = request.args.get('filePath')
    try:
        # print(f"转换 {file_path} 请求")
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"{file_path} 文件不存在")
            return send_file(r"F:\Warehouse\Epiboly\Pic_Deal_Python\照片整理\csv计算版\2_imagehash\2_3相似图片可视化删除\不存在.jpg", mimetype='image/jpeg')

        pic_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        for pic_format in pic_formats:
            if file_path.lower().endswith(pic_format):
                # 根据文件扩展名设置正确的 MIME 类型
                if pic_format == '.jpg' or pic_format == '.jpeg':
                    mimetype = 'image/jpeg'
                elif pic_format == '.png':
                    mimetype = 'image/png'
                elif pic_format == '.gif':
                    mimetype = 'image/gif'
                elif pic_format == '.bmp':
                    mimetype = 'image/bmp'
                return send_file(file_path, mimetype=mimetype)


        # 生成缩略图文件名
        file_name = os.path.basename(file_path)
        md5_hash = calculate_md5(file_path)
        thumbnail_name = f"thumbnail_{file_name}_{md5_hash}.jpg"
        thumbnail_path = os.path.join(TEMP_IMAGE_PATH, thumbnail_name)

        # 如果缩略图已存在，则直接返回
        if os.path.exists(thumbnail_path):
            # print(f"{thumbnail_path} 缩略图已存在")
            return send_file(thumbnail_path, mimetype='image/jpeg')

        convert_raw_to_jpg(file_path, thumbnail_path)

        # print(f"{thumbnail_path} 成功生成缩略图")

        # 返回缩略图文件
        return send_file(thumbnail_path, mimetype='image/jpeg')
    except Exception as e:
        print(f"接口异常：", e)
        return jsonify({'error': str(e)}), 500


@app.route('/check-file-existence', methods=['GET'])
def check_file_existence():
    file_path = request.args.get('filePath')
    exists = os.path.exists(file_path)
    return jsonify({'exists': exists}), 200


@app.route('/delete', methods=['POST'])
def delete_file():
    data = request.json
    file_path = data.get('filePath')
    try:
        send2trash(file_path)
        return jsonify({'message': '文件已移入回收站'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


import os
import rawpy
from PIL import Image


def convert_raw_to_jpg(input_path, output_path):
    # 获取文件扩展名
    ext = os.path.splitext(input_path)[1].lower()

    # 判断文件类型，选择对应的处理方式
    if ext == '.nef':  # 处理 .NEF 文件
        convert_nef_to_jpg(input_path, output_path)
    elif ext == '.cr3':  # 处理 .CR3 文件
        convert_cr3_to_jpg(input_path, output_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def convert_nef_to_jpg(nef_path, jpg_path):
    # 使用 rawpy 打开 .NEF 文件
    with rawpy.imread(nef_path) as raw:
        # 转换为 RGB 图像
        rgb = raw.postprocess()

        # 使用 Pillow 保存为 .JPG 格式
        image = Image.fromarray(rgb)
        image.save(jpg_path, 'JPEG')


def convert_cr3_to_jpg(cr3_path, jpg_path):
    # 尝试使用 rawpy 处理 .CR3 文件（如果支持）
    try:
        with rawpy.imread(cr3_path) as raw:
            # 转换为 RGB 图像
            rgb = raw.postprocess()

            # 使用 Pillow 保存为 .JPG 格式
            image = Image.fromarray(rgb)
            image.save(jpg_path, 'JPEG')
    except Exception as e:
        raise ValueError(f"Error processing .CR3 file: {e}")

if __name__ == '__main__':
    app.run(debug=False)

