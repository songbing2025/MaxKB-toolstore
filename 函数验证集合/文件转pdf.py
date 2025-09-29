import requests
import os
import random
import string


def process_documents(doc_list, base_url, auth_token):
    """处理文档：下载->转换->上传->清理"""
    if not doc_list:
        return "错误：文档列表为空"

    doc = doc_list[0]
    name = doc.get('name', '未命名文件')
    file_url = doc.get('url', '')

    if not file_url:
        return "错误：缺少文件URL"

    # 1. 构建完整URL并下载文件
    full_url = base_url.rstrip('/') + "/admin" + file_url.replace(".", "")
    headers = {'AUTHORIZATION': "Bearer " + auth_token}

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return f"下载失败: {name} (状态码: {response.status_code})"
        file_content = response.content
    except Exception as e:
        return f"下载错误: {str(e)}"

    # 2. 定义转换流程
    conversion_flow = []
    if name.lower().endswith('.doc'):
        conversion_flow = [
            ("doc-to-docx", ".docx"),
            ("docx-to-pdf", ".pdf")
        ]
    elif name.lower().endswith('.docx'):
        conversion_flow = [
            ("docx-to-pdf", ".pdf")
        ]

    # 3. 执行多步骤文件转换
    for step, (convert_type, new_ext) in enumerate(conversion_flow, 1):
        convert_url = f"http://124.156.139.70:5000/convert/{convert_type}"
        print(f"执行转换步骤 {step}/{len(conversion_flow)}: {convert_type}")

        try:
            # 更新文件名（保留原始文件名主干）
            base_name = name.rsplit('.', 1)[0]
            current_ext = '.' + name.split('.')[-1] if '.' in name else ''
            temp_name = f"{base_name}_{step}{current_ext}"

            files = {'file': (temp_name, file_content)}
            response = requests.post(convert_url, files=files, timeout=120)

            if response.status_code == 200:
                # 更新文件名和内容
                name = base_name + new_ext
                file_content = response.content
                print(f"转换成功: {name}")
            else:
                return f"转换失败[{convert_type}]: {response.text[:200]}"
        except Exception as e:
            return f"转换错误[{convert_type}]: {str(e)}"

    # 4. 保存临时文件
    temp_dir = "/opt/maxkb-app/sandbox/python-packages/temp/"
    os.makedirs(temp_dir, exist_ok=True)

    # 生成唯一文件名（避免并发冲突）
    base_name = name.rsplit('.', 1)[0]
    ext = '.' + name.split('.')[-1] if '.' in name else ''
    random_suffix = ''.join(random.choices(string.digits, k=6))
    temp_filename = f"temp_{base_name}_{random_suffix}{ext}"
    temp_file = os.path.join(temp_dir, temp_filename)

    try:
        with open(temp_file, 'wb') as f:
            f.write(file_content)
    except Exception as e:
        return f"保存临时文件错误: {str(e)}"

    # 5. 上传文件 (临时2小时)
    upload_url = f"{base_url}/admin/api/oss/file"
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': (name, f)}
            response = requests.post(upload_url, headers=headers, files=files,
                                     data={"source_id": "TEMPORARY_120_MINUTE", "source_type": "TEMPORARY_120_MINUTE"},
                                     timeout=60)

            if response.status_code == 200:
                result = response.json()
                print(f"上传成功: {name}")
                return_data = [{
                    "name": name,
                    "url": result['data'],
                    "status": "success",
                    "file_id": result['data'].split('/')[-1]
                }]
            else:
                return_data = [{
                    "name": name,
                    "data": None,
                    "status": "error",
                    "error_message": f"上传失败 (状态码 {response.status_code}): {response.text[:200]}"
                }]
    except Exception as e:
        return_data = f"上传错误: {str(e)}"

    # 6. 清理临时文件
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"已清理临时文件: {temp_file}")
    except Exception as e:
        print(f"清理临时文件失败: {str(e)}")

    return return_data


if __name__ == "__main__":
    # 示例用法
    auth_token = "user-9163278a0a68200ca4c364d60d5fbb18"
    base_url = "http://democenter.fit2cloud.cn:8882"
    doc_list = [
        {
            "name": "MaxKB 专业版V2-2025v1版.docx",
            "percentage": 0,
            "status": "ready",
            "size": 27591,
            "raw": {
                "uid": 1758096666635
            },
            "uid": 1758096666635,
            "url": "./oss/file/019956ba-4e9d-7a23-bf40-5a17206fe606",
            "file_id": "019956ba-4e9d-7a23-bf40-5a17206fe606"
        }
    ]
    print(process_documents(doc_list, base_url, auth_token))
