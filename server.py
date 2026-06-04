#!/usr/bin/env python3
"""HTTP server with proper Range request support for video scrubbing."""
import http.server
import os
import re
import sys

class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            return super().send_head()

        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None

        file_len = os.fstat(f.fileno()).st_size
        ctype    = self.guess_type(path)
        range_hdr = self.headers.get('Range')

        if range_hdr:
            m = re.fullmatch(r'bytes=(\d+)-(\d*)', range_hdr.strip())
            if m:
                start = int(m.group(1))
                end   = int(m.group(2)) if m.group(2) else file_len - 1
                end   = min(end, file_len - 1)
                length = end - start + 1

                self.send_response(206)
                self.send_header('Content-Type', ctype)
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Range', f'bytes {start}-{end}/{file_len}')
                self.send_header('Content-Length', str(length))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                f.seek(start)
                return f

        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(file_len))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        return f

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.chdir(directory)
    port = 8000
    server = http.server.HTTPServer(('', port), RangeHandler)
    print(f"Serving {os.path.abspath(directory)} at http://localhost:{port}")
    print("Press Ctrl+C to stop.\n")
    server.serve_forever()
