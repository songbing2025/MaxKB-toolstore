import os.path
import requests
import uuid
from datetime import datetime


def upload_file(url, headers, file_path, file_name=None, mime_type=None):
    """
    通用函数：上传文件到指定的 URL。

    参数:
        url (str): 目标上传地址。
        headers (dict): 请求头。
        file_path (str): 要上传的文件路径。
        file_name (str, optional): 文件在请求中的名称，默认为文件路径的文件名。
        mime_type (str, optional): 文件的 MIME 类型，默认为 'application/octet-stream'。

    返回:
        dict: 服务器返回的响应内容（JSON 格式）。
    """
    # 如果没有指定文件名，则使用文件路径的文件名部分
    if not file_name:
        file_name = os.path.basename(file_path)

    # 如果没有指定 MIME 类型，则默认为二进制文件
    if not mime_type:
        mime_type = 'application/octet-stream'

    # 准备文件数据
    try:
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_name, f, mime_type)
            }

            # 发送 POST 请求
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()  # 返回 JSON 格式的响应内容

    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None
    except Exception as e:
        print(f"上传文件时发生错误：{e}")
        return None


def convert_html_to_pdf(html_content, output_path=None, css=None, base_url=None, filename=None,
                        upload_url=None, upload_headers=None):
    """
    调用 PDF API 服务并上传生成的PDF

    参数:
        html_content: HTML 字符串内容或文件路径
        output_path: 输出 PDF 文件路径 (可选)
        css: 额外的 CSS 样式 (可选)
        base_url: 基础 URL (可选)
        filename: 输出文件名 (可选)
        upload_url: 文件上传地址 (可选)
        upload_headers: 上传请求头 (可选)
    """
    # 如果是文件路径，则读取内容
    if os.path.isfile(html_content):
        with open(html_content, 'r', encoding='utf-8') as f:
            html_content = f.read()

    # API 端点
    api_url = "http://124.156.139.70:8899/convert"

    # 准备请求数据
    data = {"html": html_content}

    if css:
        data["css"] = css
    if base_url:
        data["base_url"] = base_url
    if filename:
        data["filename"] = filename

    try:
        # 发送转换请求
        response = requests.post(
            api_url,
            json=data,
            headers={"Content-Type": "application/json"}
        )

        # 检查响应
        if response.status_code != 200:
            error = response.json().get("error", "未知错误")
            print(f"❌ 转换失败 ({response.status_code}): {error}")
            return False

        # 生成临时文件路径
        temp_dir = "/opt/maxkb-app/sandbox/python-packages/temp/"
        os.makedirs(temp_dir, exist_ok=True)

        # 生成唯一文件名: tem_随机数_时间戳.pdf
        random_str = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = f"tem_{random_str}_{timestamp}.pdf"
        temp_pdf_path = os.path.join(temp_dir, pdf_filename)

        # 保存 PDF
        with open(temp_pdf_path, "wb") as f:
            f.write(response.content)
        print(f"✅ PDF 保存成功: {temp_pdf_path}")

        # 如果需要上传
        if upload_url and upload_headers:
            print(f"⬆️ 开始上传文件: {pdf_filename}")
            upload_result = upload_file(
                url=upload_url + "/admin/api/oss/file",
                headers={
                    "Authorization": "Bearer " +upload_headers
                },
                file_path=temp_pdf_path,
                file_name=pdf_filename,
                mime_type='application/pdf'
            )

            if upload_result is not None:
                print(f"✅ 文件上传成功: {upload_result}")
                file_path = upload_result['data'].replace(".","/admin")
                return f'<html_rander> <a href="{upload_url + file_path}"  target="_blank"  style="color: blue" >{filename}</a> </html_rander>'
            else:
                print("❌ 文件上传失败")
                return False

        return True

    except requests.exceptions.RequestException as e:
        print(f"🚨 网络请求失败: {str(e)}")
        return False
    except Exception as e:
        print(f"🚨 发生未知错误: {str(e)}")
        return False
    finally:
        # 确保删除临时文件
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
                print(f"🗑️ 已删除临时文件: {temp_pdf_path}")
            except Exception as e:
                print(f"⚠️ 删除临时文件失败: {str(e)}")


if __name__ == "__main__":
    # 调用 API 并上传
    result = convert_html_to_pdf(
        html_content="<html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>飞致云报价单</title><style>@page { size: A4; margin: 1.5cm; } body { font-family: \"Microsoft YaHei\", \"Helvetica Neue\", Arial, sans-serif; line-height: 1.5; margin: 0; padding: 20px; color: #333; background-color: #f9f9f9; font-size: 14px; } /* 所有类名添加唯一前缀 fz- 实现样式隔离 */ .fz-container { width: 210mm; min-height: 297mm; margin: 0 auto; padding: 20px; box-sizing: border-box; background-color: #fff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); position: relative; overflow: hidden; /* 多水印背景 */ background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150' viewBox='0 0 150 150'%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='16' fill='rgba(204,204,204,0.25)' text-anchor='middle' transform='rotate(-45, 75, 75)'%3E飞致云%3C/text%3E%3C/svg%3E\"); background-repeat: repeat; background-size: 150px 150px; } .fz-header, .fz-info-section, .fz-quote-table, .fz-terms-section, .fz-footer { position: relative; z-index: 1; } .fz-header { text-align: center; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #1a5276; } .fz-header h1 { font-size: 24px; margin: 0; color: #1a5276; font-weight: bold; } .fz-info-section { margin-bottom: 20px; } .fz-info-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #ddd; box-shadow: 0 2px 3px rgba(0, 0, 0, 0.05); } .fz-info-table td { padding: 12px; vertical-align: top; border-bottom: 1px solid #eee; width: 50%; } .fz-info-table tr:last-child td { border-bottom: none; } .fz-info-label { font-weight: bold; color: #1a5276; margin-bottom: 5px; display: block; } .fz-info-value { display: block; } .fz-quote-title, .fz-terms-title { color: #1a5276; margin: 15px 0 8px; font-size: 17px; border-left: 4px solid #1a5276; padding-left: 10px; } .fz-quote-table { width: 100%; border-collapse: collapse; margin-top: 12px; border: 1px solid #ddd; } .fz-quote-table th, .fz-quote-table td { border: 1px solid #ddd; padding: 10px 12px; text-align: left; } .fz-quote-table th { background-color: #1a5276; color: #fff; font-weight: bold; } .fz-quote-table tr:nth-child(even) { background-color: #f8f9fa; } .fz-total-row { font-weight: bold; background-color: #e8f4f8 !important; color: #1a5276; } .fz-terms-section { margin: 15px 0; padding: 10px 0; font-size: 12px; line-height: 1.3; color: #444; } .fz-terms-section p { margin: 6px 0; } .fz-terms-subtitle { font-weight: bold; color: #1a5276; display: inline; margin-right: 5px; } .fz-footer { margin-top: 15px; text-align: right; color: #666; font-size: 13px; padding-top: 10px; border-top: 1px dashed #ccc; } .fz-logo { margin-bottom: 15px; text-align: center; font-size: 28px; font-weight: bold; color: #1a5276; } .fz-service-table { width: 100%; border-collapse: collapse; margin-top: 15px; border: 1px solid #ddd; font-size: 12px; } .fz-service-table th, .fz-service-table td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; font-size: 12px; } .fz-service-table th { background-color: #1a5276; color: #fff; font-weight: bold; } .fz-service-table tr:nth-child(even) { background-color: #f8f9fa; } .fz-group-separator { height: 20px; } @media print { body { background-color: #fff; padding: 0; } .fz-container { width: 100%; height: 100%; margin: 0; padding: 0; box-shadow: none; /* 确保打印时水印可见 */ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; } .fz-footer { position: static; text-align: right; } }</style></head><body><div class=\"fz-container\"><div class=\"fz-header\"><div class=\"fz-logo\">FIT2CLOUD 飞致云</div><h1>产品和服务-订阅报价单</h1></div><div class=\"fz-info-section\"><table class=\"fz-info-table\"><tr><td><span class=\"fz-info-label\">客户名称</span><span class=\"fz-info-value\">百度信息科技有限公司</span></td><td><span class=\"fz-info-label\">客户联系人</span><span class=\"fz-info-value\">客户联系人</span></td></tr><tr><td><span class=\"fz-info-label\">客户项目</span><span class=\"fz-info-value\">2025年度数据可视化大屏工具采购项目</span></td><td><span class=\"fz-info-label\">客户电话</span><span class=\"fz-info-value\">18510000000</span></td></tr><tr class=\"fz-group-separator\"><td colspan=\"2\"></td></tr><tr><td><span class=\"fz-info-label\">客户经理</span><span class=\"fz-info-value\">张三</span></td><td><span class=\"fz-info-label\">联系电话</span><span class=\"fz-info-value\">18610000000</span></td></tr><tr><td colspan=\"2\" style=\"text-align: left;\"><span class=\"fz-info-label\">电子邮箱</span><span class=\"fz-info-value\">zhangsan@foxmail.com</span></td></tr><tr class=\"fz-group-separator\"><td colspan=\"2\"></td></tr><tr><td><span class=\"fz-info-label\">报价日期</span><span class=\"fz-info-value\">2025-09-08</span></td><td><span class=\"fz-info-label\">有效期至</span><span class=\"fz-info-value\">2025-10-08</span></td></tr></table></div><h2 class=\"fz-quote-title\">报价明细（币种：人民币）</h2><table class=\"fz-quote-table\"><thead><tr><th>产品SKU</th><th>产品描述</th><th>单价<br/>（含税）</th><th>数量</th><th>年度</th><th>税率</th><th>服务等级</th><th>合计<br/>（含税）</th></tr></thead><tbody><tr><td>2025v2-DE-ENT-SNS</td><td>DataEase 企业版的 1 年订阅：1套，账号数量不限，支持单机/冷备/热备/集群部署模式。含 X-Pack。</td><td>90,000/套*年</td><td>1</td><td>1</td><td>6%</td><td>增强级</td><td>90,000</td></tr><tr class=\"fz-total-row\"><td colspan=\"7\">总价</td><td>90,000</td></tr></tbody></table><h2 class=\"fz-terms-title\">报价条款</h2><div class=\"fz-terms-section\"><p><span class=\"fz-terms-subtitle\">1.报价说明：</span>本报价有效期30天；最终价格以正式合同为准，飞致云保留解释权。</p><p><span class=\"fz-terms-subtitle\">2.付款条款：</span>合同签署后，甲方须在10个工作日内一次性支付全部款项。</p><p><span class=\"fz-terms-subtitle\">3.交付条款：</span>乙方在收到全款且客户申请后的3个工作日交付许可文件，15天内完成软件安装部署及调试。</p></div><h2 class=\"fz-terms-title\">服务等级说明</h2><table class=\"fz-service-table\"><thead><tr><th>服务项目</th><th>增强级</th></tr></thead><tbody><tr><td>支持服务</td><td>7x24 工单及电话支持服务，1 个小时内响应客户工单； 接到故障申报后，工程师通过电话支持、远程接入等方式协助客户及时排除软件故障。</td></tr><tr><td>安装架构</td><td>单机架构、主备架构、集群架构、分布式架构</td></tr><tr><td>培训方式</td><td>提供离线视频、远程会议、现场培训</td></tr><tr><td>产品安装</td><td>提供安装文档、远程安装、现场安装</td></tr><tr><td>现场紧急救助服务</td><td>合计 5 人天的原厂专业服务：可提供现场安装服务、现场紧急救助服务、软件故障排査等服务。</td></tr><tr><td>软件升级服务</td><td>提供软件X-Pack增强功能包，提供软件小版本无缝升级服务。</td></tr><tr><td>在线自助服务</td><td>提供客户支持门户，支持客户在线访问网站并下载相关资料, 及时掌握最新的软件特性、维护经验、使用技巧等相关知识。</td></tr></tbody></table><div class=\"fz-footer\"><p>杭州飞致云信息科技有限公司</p><p style=\"text-align: center; font-size: 10px;\">软件用起来才有价值，才有改进的机会。</p></div></div></body></html>",
        filename="百度信息科技有限公司",
        upload_url="https://edu-maxkb2.fit2cloud.cn",
        upload_headers="user-9a6b2d06ce88529f33172aafef189b2f"

    )

    print(result)