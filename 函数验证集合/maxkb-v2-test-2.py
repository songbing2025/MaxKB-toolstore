import requests
from io import BytesIO
from docx import Document
import pdfplumber
import re


# pip install python-docx pdfplumber

def get_file(document_path, base_url):
    """
    直接读取文件内容并返回文本，支持多种文件格式

    Args:
        document_path (list): 包含文件信息的列表
        base_url (str): 基础URL

    Returns:
        str: 文件的文本内容
    """
    if isinstance(document_path, list):
        # 处理列表类型
        print("document_path 是列表类型")
        if not document_path:
            print("错误: document_path 列表为空")
            return None
        doc = document_path[0]
        name = doc.get('name', '未命名文件')
        file_url = doc.get('url', '').split('/')[-1]
    else:
        print(f"错误: document_path 类型不支持，期望 list，实际收到 {type(document_path)}")
        return f"错误: document_path 类型不支持，期望 list，实际收到 {type(document_path)}"

    # 获取对话文件信息
    url = base_url.rstrip('/') + "/admin/oss/file/" + file_url

    header = {
        # 'Authorization': f'{user_key}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()  # 检查HTTP错误
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

    # 检查响应是否为空
    if not response.content:
        print("响应内容为空")
        return None

    # 根据文件扩展名处理不同类型的内容
    if name.endswith('.docx'):
        # 处理.docx文件
        try:
            doc_file = BytesIO(response.content)
            document = Document(doc_file)

            full_text = []
            for paragraph in document.paragraphs:
                full_text.append(paragraph.text)

            return '\n'.join(full_text)
        except Exception as e:
            print(f"解析.docx文件时出错: {e}")
            return None

    elif name.endswith('.pdf'):
        # 处理.pdf文件 - 使用pdfplumber转换为Markdown格式
        try:
            pdf_file = BytesIO(response.content)
            markdown_content = []

            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # 添加页面分隔
                    if page_num > 1:
                        markdown_content.append("\n\n---\n\n")

                    # 提取页面文本
                    text = page.extract_text()
                    if text:
                        # 简单的文本清理和格式化
                        text = re.sub(r'\n{3,}', '\n\n', text)  # 合并多个换行符
                        markdown_content.append(text)

                    # 提取表格并转换为Markdown表格
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            markdown_content.append("\n\n")
                            # 创建表头
                            if table[0]:
                                header = "| " + " | ".join(str(cell) if cell else "" for cell in table[0]) + " |"
                                separator = "|" + "|".join("---" for _ in table[0]) + "|"
                                markdown_content.append(header)
                                markdown_content.append(separator)

                                # 添加表内容
                                for row in table[1:]:
                                    if row:
                                        row_str = "| " + " | ".join(str(cell) if cell else "" for cell in row) + " |"
                                        markdown_content.append(row_str)

            return "".join(markdown_content)
        except Exception as e:
            print(f"处理.pdf文件时出错: {e}")
            return None

    elif name.endswith('.txt') or name.endswith('.md'):
        # 处理.txt和.md文件
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']

            for encoding in encodings:
                try:
                    return response.content.decode(encoding)
                except UnicodeDecodeError:
                    continue

            # 如果所有编码都失败，返回原始内容
            return response.content
        except Exception as e:
            print(f"处理文本文件 {name} 时出错: {e}")
            return response.content

    else:
        # 对于其他文件类型，尝试以文本方式处理
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']

            for encoding in encodings:
                try:
                    return response.content.decode(encoding)
                except UnicodeDecodeError:
                    continue

            # 如果所有编码都失败，返回原始内容
            return response.content
        except Exception as e:
            print(f"处理文件 {name} 时出错: {e}")
            return response.content


if __name__ == "__main__":
    document_test = [{'name': 'MaxKB 专业版V2-2025v1版.pdf', 'url': './oss/file/0199570d-ac63-7541-981d-3e772d61e946',
                      'status': 'success', 'file_id': '0199570d-ac63-7541-981d-3e772d61e946'}]
    base_url = "http://democenter.fit2cloud.cn:8882"

    result = get_file(document_test, base_url)
    if result:
        print("文件内容提取成功!")
        print(f"内容长度: {len(result)} 字符")
        # 显示前500个字符作为预览
        preview = result[:500] + "..." if len(result) > 500 else result
        print(f"预览: {preview}")
    else:
        print("文件内容提取失败!")
