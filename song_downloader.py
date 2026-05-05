import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import os
import threading

# Enable high-DPI awareness on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ── Color scheme ──────────────────────────────────────────
ACCENT   = "#4F6EF7"
ACCENT_H = "#3A54D4"
BG       = "#F0F2F5"
CARD_BG  = "#FFFFFF"
TEXT     = "#1A1A2E"
TEXT_SEC = "#6B7280"
SUCCESS  = "#10B981"
DANGER   = "#EF4444"
BORDER   = "#E5E7EB"


def download_song():
    name = name_entry.get().strip()
    url = url_entry.get().strip()

    if not name:
        messagebox.showwarning("提示", "请输入歌曲名称")
        return
    if not url:
        messagebox.showwarning("提示", "请输入歌曲链接")
        return

    download_btn.config(state="disabled")
    progress_bar.start()
    status_label.config(text="正在获取页面信息...", foreground=TEXT_SEC)

    def task():
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            resp.raise_for_status()

            title_match = re.search(
                r'<h2[^>]*class="[^"]*play_name[^"]*"[^>]*>(.*?)</h2>',
                resp.text
            )
            page_title = title_match.group(1).strip() if title_match else name

            media_url = None
            for pattern in [
                r'"playurl"\s*:\s*"(http[^"]+\.(?:m4a|mp3)[^"]*)"',
                r'(https?://[^"\s<>]+\.(?:m4a|mp3)[^"\s<>]*)',
            ]:
                match = re.search(pattern, resp.text)
                if match:
                    media_url = match.group(1)
                    break

            if not media_url:
                root.after(0, lambda: finish_op(
                    f"未找到音频文件 (页面: {page_title})", DANGER, True,
                    "未在页面中找到音频文件"
                ))
                return

            ext = ".m4a" if ".m4a" in media_url else ".mp3"
            invalid_chars = '<>:"/\\|?*'
            safe_name = name
            for ch in invalid_chars:
                safe_name = safe_name.replace(ch, "_")
            filename = safe_name + ext
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filepath = os.path.join(desktop, filename)

            root.after(0, lambda: status_label.config(
                text="正在下载音频...", foreground=TEXT_SEC))

            audio_resp = requests.get(media_url, timeout=120, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": url,
            })
            audio_resp.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(audio_resp.content)

            size_mb = len(audio_resp.content) / (1024 * 1024)
            root.after(0, lambda: finish_op(
                f"下载完成 - {filename} ({size_mb:.1f} MB)", SUCCESS, False,
                f"已保存: {filename}\n大小: {size_mb:.1f} MB", True
            ))

        except requests.exceptions.ConnectionError:
            root.after(0, lambda: finish_op(
                "无法连接，请检查网络或链接", DANGER, True,
                "无法连接到此链接，请检查网络或链接是否正确"
            ))
        except requests.exceptions.Timeout:
            root.after(0, lambda: finish_op(
                "请求超时，请重试", DANGER, True, "请求超时，请重试"))
        except requests.exceptions.HTTPError as e:
            root.after(0, lambda: finish_op(
                f"链接返回错误", DANGER, True, f"链接返回错误: {e}"))
        except Exception as e:
            root.after(0, lambda: finish_op(
                f"下载失败", DANGER, True, f"下载失败: {e}"))

    def finish_op(status_text, color, is_error, popup_msg, is_success=False):
        progress_bar.stop()
        status_label.config(text=status_text, foreground=color)
        download_btn.config(state="normal")
        if is_error:
            messagebox.showerror("错误", popup_msg)
        elif is_success:
            messagebox.showinfo("下载完成", popup_msg)

    threading.Thread(target=task, daemon=True).start()


# ── Window ────────────────────────────────────────────────
root = tk.Tk()
root.title("歌曲下载器")
W, H = 560, 370
root.geometry(f"{W}x{H}")
root.resizable(False, False)
root.configure(bg=BG)

root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
x = (sw - W) // 2
y = (sh - H) // 2
root.geometry(f"{W}x{H}+{x}+{y}")

# ── Style ─────────────────────────────────────────────────
style = ttk.Style()
style.theme_use("clam")

style.configure("Title.TLabel",
    font=("Segoe UI", 16, "bold"),
    foreground=ACCENT,
    background=BG,
    padding=(0, 0, 0, 6))

style.configure("Subtitle.TLabel",
    font=("Segoe UI", 9),
    foreground=TEXT_SEC,
    background=BG,
    padding=(0, 0, 0, 14))

style.configure("InputLabel.TLabel",
    font=("Segoe UI", 10, "bold"),
    foreground=TEXT,
    background=CARD_BG,
    padding=(0, 0, 0, 3))

style.configure("Card.TFrame",
    background=CARD_BG,
    relief="solid",
    borderwidth=1)

style.configure("TEntry",
    font=("Segoe UI", 10),
    fieldbackground=CARD_BG,
    borderwidth=1,
    relief="solid",
    padding=8)

style.configure("Accent.TButton",
    font=("Segoe UI", 10, "bold"),
    background=ACCENT,
    foreground="#FFFFFF",
    borderwidth=0,
    relief="flat",
    padding=(24, 8))

style.map("Accent.TButton",
    background=[("disabled", "#A5B4FC"), ("active", ACCENT_H)],
    foreground=[("disabled", "#E0E7FF")])

style.configure("TProgressbar",
    thickness=4,
    background=ACCENT,
    troughcolor=BORDER)

# ── Layout ────────────────────────────────────────────────
# Header
ttk.Label(root, text="歌曲下载器", style="Title.TLabel").pack(pady=(22, 0))
ttk.Label(root, text="输入歌曲名称和链接，一键下载到本地", style="Subtitle.TLabel").pack()

# Card frame
card = ttk.Frame(root, style="Card.TFrame")
card.pack(fill="both", padx=30, pady=(4, 12), expand=True)

# Canvas hack for card background
card_inner = tk.Frame(card, bg=CARD_BG, padx=20, pady=14)
card_inner.pack(fill="both", expand=True)

# Song name
ttk.Label(card_inner, text="歌曲名称", style="InputLabel.TLabel").pack(anchor="w")
name_entry = ttk.Entry(card_inner, font=("Segoe UI", 10))
name_entry.pack(fill="x", pady=(2, 12))

# Song URL
ttk.Label(card_inner, text="歌曲链接", style="InputLabel.TLabel").pack(anchor="w")
url_entry = ttk.Entry(card_inner, font=("Segoe UI", 10))
url_entry.pack(fill="x", pady=(2, 14))

# Progress bar
progress_bar = ttk.Progressbar(card_inner, mode="indeterminate", style="TProgressbar")
progress_bar.pack(fill="x", pady=(0, 10))

# Download button (full width)
download_btn = ttk.Button(card_inner, text="下  载", style="Accent.TButton",
                          command=download_song)
download_btn.pack(fill="x", pady=(0, 6))

# Status label
status_label = tk.Label(
    card_inner, text="", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_SEC,
    anchor="center")
status_label.pack(fill="x")

root.mainloop()
