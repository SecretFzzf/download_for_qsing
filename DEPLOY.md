# 🚀 部署指南

本项目需要后端服务器支持。有以下几种方式部署：

## 方案1：Railway 一键部署（推荐）

最简单，只需3分钟：

### 步骤1：Fork 本仓库
点击右上角 **Fork**

### 步骤2：连接Railway
1. 访问 [Railway.app](https://railway.app)
2. 用GitHub账户登录
3. 点击 **New Project** → **Deploy from GitHub repo**
4. 选择你Fork的仓库
5. 在 **Variables** 中可选配置，直接点 **Deploy**

### 步骤3：获取项目URL
部署完成后，Railway会给你一个URL，例如：
```
https://your-project.up.railway.app
```

在浏览器打开该URL即可使用！

---

## 方案2：Render 部署

1. 访问 [Render.com](https://render.com)
2. 用GitHub登录
3. 点击 **New** → **Web Service**
4. 选择你的GitHub仓库
5. 设置：
   - **Name**: 随意填
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
6. 点击 **Create Web Service**

等待部署完成，会给你一个可公开访问的URL。

---

## 方案3：本地运行（开发用）

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/find_my_song.git
cd find_my_song

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行服务器
python server.py

# 4. 打开浏览器
http://localhost:5000
```

---

## 方案4：PythonAnywhere 部署

1. 访问 [PythonAnywhere.com](https://www.pythonanywhere.com)
2. 免费注册账户
3. 上传本项目代码
4. 创建 Web 应用 → Flask
5. 修改 WSGI 配置指向 server.py

详细步骤见 PythonAnywhere 文档。

---

## 遇到问题？

| 错误 | 解决方案 |
|------|--------|
| ModuleNotFoundError | 确保 `pip install -r requirements.txt` |
| 连接被拒绝 | 确保 Flask 在正确的端口监听 |
| 无法获取页面 | 检查网络，某些链接可能失效 |

---

**推荐新手使用 Railway，最简单最快！**
