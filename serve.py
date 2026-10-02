"""Abre el portfolio en el navegador: python3 serve.py"""
import http.server, os, socketserver, subprocess, sys, webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))

# Compilar los archivos HTML más recientes antes de iniciar el servidor
subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True)

os.chdir(os.path.join(ROOT, "dist"))
URL = "http://localhost:8931/portfolio.html"
socketserver.TCPServer.allow_reuse_address = True

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

with socketserver.TCPServer(("127.0.0.1", 8931), NoCacheHTTPRequestHandler) as s:
    print("Portfolio en %s   (Ctrl+C para parar)" % URL)
    webbrowser.open(URL)
    s.serve_forever()

