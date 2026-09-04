"""Abre el portfolio en el navegador: python3 serve.py"""
import http.server, os, socketserver, webbrowser

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist"))
URL = "http://localhost:8931/portfolio.html"
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8931), http.server.SimpleHTTPRequestHandler) as s:
    print("Portfolio en %s   (Ctrl+C para parar)" % URL)
    webbrowser.open(URL)
    s.serve_forever()
