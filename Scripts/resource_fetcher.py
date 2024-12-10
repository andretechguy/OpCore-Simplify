import os
import json
import plistlib
import socket
import sys

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
else:
    import urllib2
    from urllib2 import urlopen, Request

class ResourceFetcher:
    def __init__(self, headers={}):
        self.request_headers = headers
        self.buffer_size = 16 * 1024

    def is_connected(self, timeout=5):
        socket.create_connection(("github.com", 443), timeout=timeout)

    def fetch_and_parse_content(self, resource_url, content_type=None):
        self.is_connected()

        with urlopen(resource_url) as response:
            content = response.read()
            if content_type == 'json':
                return json.loads(content)
            elif content_type == 'plist':
                return plistlib.loads(content)
            else:
                return content.decode('utf-8')

    def _download_with_progress(self, response, local_file):
        total_size = response.getheader('Content-Length')
        if total_size:
            total_size = int(total_size)
        bytes_downloaded = 0

        while True:
            chunk = response.read(self.buffer_size)
            if not chunk:
                break
            local_file.write(chunk)
            bytes_downloaded += len(chunk)

            if total_size:
                percent = int(bytes_downloaded / total_size * 100)
                progress = f"[{'=' * (percent // 2):50s}] {percent}%  {bytes_downloaded / (1024 * 1024):.2f}/{total_size / (1024 * 1024):.2f} MB"
            else:
                progress = f"Downloaded {bytes_downloaded / (1024 * 1024):.2f} MB"
            print(progress, end='\r')

        print()

    def download_and_save_file(self, resource_url, destination_path):
        self.is_connected()

        with urlopen(resource_url) as response, open(destination_path, 'wb') as local_file:
            print(f"Downloading from {resource_url}")
            self._download_with_progress(response, local_file)