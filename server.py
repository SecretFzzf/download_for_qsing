from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import re
import os
import io

app = Flask(__name__)
CORS(app)  # 启用CORS

@app.route('/api/download', methods=['POST', 'OPTIONS'])
def download():
    try:
        data = request.json
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()

        if not name or not url:
            return jsonify({'success': False, 'error': '歌曲名称和链接不能为空'}), 400

        # 获取页面HTML，像爬虫一样分析
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
        html = resp.text

        # 提取歌曲标题
        title_match = re.search(r'<h2[^>]*class="[^"]*play_name[^"]*"[^>]*>(.*?)</h2>', html)
        page_title = title_match.group(1).strip() if title_match else name

        # 提取音频URL：全民K歌页面通常直接包含 playurl
        media_url = None
        patterns = [
            r'"playurl"\s*:\s*"(https?://[^"]+)"',
            r'"playurl"\s*:\s*"(http[^"]+\.(?:m4a|mp3)[^"]*)"',
            r'(https?://[^\s"<>]+\.(?:m4a|mp3)[^\s"<>]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                media_url = match.group(1)
                break

        if not media_url:
            return jsonify({'success': False, 'error': f'未找到音频文件 (页面: {page_title})'}), 400

        # 下载音频
        audio_resp = requests.get(media_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': url
        })
        audio_resp.raise_for_status()

        if len(audio_resp.content) == 0:
            return jsonify({'success': False, 'error': '音频文件为空'}), 400

        # 确定文件扩展名
        ext = '.m4a' if 'm4a' in media_url else '.mp3'
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        filename = safe_name + ext

        # 直接返回文件，不使用hex转换
        return send_file(
            io.BytesIO(audio_resp.content),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': '网络请求超时'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': '无法连接到网络'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'下载失败: {str(e)}'}), 500

@app.route('/')
def index():
    # 提供HTML文件
    html_path = os.path.join(os.path.dirname(__file__), '歌曲下载器.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🎵 歌曲下载器服务器启动中...")
    print(f"请在浏览器中打开: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
