
import requests
import json
import chardet
from typing import Optional, Dict, Any, Union


def make_http_request(
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 10,
        auth: Optional[tuple] = None,
        files: Optional[Dict] = None,
        allow_redirects: bool = True,
        encoding: Optional[str] = None  # 新增：强制指定编码
) -> Dict[str, Any]:
    """
    发送一个 HTTP 请求（解决乱码问题版本）。

    参数:
    encoding (str, optional): 强制指定响应编码，如 'utf-8', 'gbk', 'gb2312'等
    """
    try:
        # 合并headers
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)

        if json_data and "Content-Type" not in default_headers:
            default_headers["Content-Type"] = "application/json"

        request_args = {
            "url": url,
            "params": params,
            "headers": default_headers,
            "timeout": timeout,
            "auth": auth,
            "allow_redirects": allow_redirects
        }

        # 根据方法设置不同的参数
        method = method.upper()
        if method in ['POST', 'PUT', 'PATCH']:
            if json_data:
                request_args["json"] = json_data
            elif data:
                request_args["data"] = data
            if files:
                request_args["files"] = files
                if "Content-Type" in request_args["headers"]:
                    del request_args["headers"]["Content-Type"]

        # 发送请求
        if method == 'GET':
            response = requests.get(**request_args)
        elif method == 'POST':
            response = requests.post(**request_args)
        elif method == 'PUT':
            response = requests.put(**request_args)
        elif method == 'DELETE':
            response = requests.delete(**request_args)
        elif method == 'PATCH':
            response = requests.patch(**request_args)
        elif method == 'HEAD':
            response = requests.head(**request_args)
        elif method == 'OPTIONS':
            response = requests.options(**request_args)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")

        # 检查响应状态码
        response.raise_for_status()

        # 解决乱码问题的核心代码
        if encoding:
            # 如果用户明确指定了编码
            response.encoding = encoding
        else:
            # 自动检测编码
            detected_encoding = detect_response_encoding(response)
            response.encoding = detected_encoding

        # 根据Content-Type返回不同的数据
        content_type = response.headers.get('Content-Type', '').lower()

        if 'application/json' in content_type:
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回文本
                response_data = response.text
        else:
            response_data = response.text

        return {
            "success": True,
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers),
            "encoding": response.encoding  # 返回实际使用的编码
        }

    except requests.exceptions.HTTPError as http_err:
        return handle_http_error(http_err, timeout)
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error_type": "TIMEOUT",
            "message": f"请求超时（超过 {timeout} 秒）"
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "success": False,
            "error_type": "REQUEST_ERROR",
            "message": f"请求失败: {req_err}"
        }
    except Exception as err:
        return {
            "success": False,
            "error_type": "UNKNOWN_ERROR",
            "message": f"未知错误: {err}"
        }


def detect_response_encoding(response: requests.Response) -> str:
    """
    自动检测响应内容的编码
    """
    # 1. 首先检查HTTP headers中的编码声明
    content_type = response.headers.get('Content-Type', '').lower()
    if 'charset=' in content_type:
        for part in content_type.split(';'):
            if 'charset=' in part:
                encoding = part.split('charset=')[1].strip()
                return encoding

    # 2. 使用chardet检测编码（更准确）
    if response.content:
        detected = chardet.detect(response.content)
        if detected['confidence'] > 0.7:  # 置信度大于70%
            return detected['encoding']

    # 3. 使用requests的默认编码检测
    if response.encoding:
        return response.encoding

    # 4. 默认使用utf-8
    return 'utf-8'


def handle_http_error(http_err: requests.exceptions.HTTPError, timeout: int) -> Dict[str, Any]:
    """
    处理HTTP错误，同时解决错误响应的乱码问题
    """
    response = getattr(http_err, 'response', None)
    if response:
        # 解决错误响应的编码问题
        detected_encoding = detect_response_encoding(response)
        response.encoding = detected_encoding

        try:
            error_data = response.json()
        except:
            error_data = response.text

        return {
            "success": False,
            "error_type": "HTTP_ERROR",
            "status_code": response.status_code,
            "message": f"HTTP错误: {http_err}",
            "data": error_data,
            "encoding": detected_encoding
        }
    else:
        return {
            "success": False,
            "error_type": "HTTP_ERROR",
            "message": f"HTTP错误: {http_err}"
        }

if __name__ == '__main__':

    # 1. GET请求
    result = make_http_request('GET', 'https://www.baidu.com', None)

    # # 2. POST JSON数据
    # result = make_http_request('POST', 'https://api.example.com/users',
    #                           json_data={'name': 'John', 'email': 'john@example.com'})
    #
    # # 3. 带认证的请求
    # result = make_http_request('GET', 'https://api.example.com/secure',
    #                           auth=('username', 'password'))
    #
    # # 4. 自定义headers
    # headers = {'Authorization': 'Bearer your_token'}
    # result = make_http_request('GET', 'https://api.example.com/protected', headers=headers)
    #
    # # 5. 文件上传
    # with open('file.txt', 'rb') as f:
    #     result = make_http_request('POST', 'https://api.example.com/upload',
    #                               files={'file': f})

    # 检查结果
    if result['success']:
        print("请求成功:", result['data'])
    else:
        print("请求失败:", result['message'])