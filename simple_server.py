#!/usr/bin/env python
"""Simple HTTP server for testing"""
import http.server
import socketserver
import os

os.chdir('C:/Users/1/WorkBuddy/2026-05-06-task-1')

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress log output

if __name__ == '__main__':
    with socketserver.TCPServer(("0.0.0.0", 5001), QuietHandler) as httpd:
        print("Serving on port 5001", flush=True)
        httpd.serve_forever()
