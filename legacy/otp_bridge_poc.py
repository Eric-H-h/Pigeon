from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import subprocess
import time

HOST = "0.0.0.0"
PORT = 8765

# 本地 PoC 占位值。公开版本会在首次启动时随机生成并持久化 Token。
TOKEN = "replace-before-running"

PATTERNS = [
    re.compile(
        r"(?:验证码|校验码|动态码|短信码|OTP|verification\s*code|code)"
        r"\D{0,20}(\d{4,8})",
        re.IGNORECASE
    ),
    re.compile(
        r"(\d{4,8})\D{0,20}"
        r"(?:验证码|校验码|动态码|短信码|OTP|code)",
        re.IGNORECASE
    ),
]


def extract_otp(text):
    # 优先寻找“验证码 123456”这种形式
    for pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)

    # 兜底：
    # 如果整条短信中只有一个 4~8 位连续数字，就把它当验证码
    candidates = re.findall(r"(?<!\d)\d{4,8}(?!\d)", text)

    if len(candidates) == 1:
        return candidates[0]

    return None


def copy_to_clipboard(text):
    # Windows 自带 clip.exe，不需要安装额外 Python 库
    subprocess.run(
        ["clip.exe"],
        input=text,
        text=True,
        check=True
    )


class Handler(BaseHTTPRequestHandler):

    def send_text(self, status, text):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_text(200, "OTP Bridge OK")
        else:
            self.send_text(404, "Not Found")

    def do_POST(self):
        if self.path != "/otp":
            self.send_text(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))

            if body.get("token") != TOKEN:
                self.send_text(403, "Invalid token")
                return

            text = str(body.get("text", ""))

            otp = extract_otp(text)

            if not otp:
                print(
                    time.strftime("%H:%M:%S"),
                    "收到短信，但没有找到唯一验证码"
                )
                self.send_text(422, "OTP not found")
                return

            copy_to_clipboard(otp)

            masked = otp[0] + "*" * (len(otp) - 2) + otp[-1]

            print(
                time.strftime("%H:%M:%S"),
                f"验证码已复制到剪贴板: {masked}"
            )

            self.send_text(200, "OK")

        except Exception as e:
            print("Error:", e)
            self.send_text(500, "Error")

    # 不打印默认 HTTP 请求日志
    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)

    print(f"OTP Bridge running on port {PORT}")
    print("等待 iPhone...")
    print("Ctrl+C 退出")

    server.serve_forever()
