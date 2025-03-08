"""Homw work 3"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime
from jinja2 import Template

STORAGE_PATH = "storage/data.json"

class JsonDataHandler:
    """Class for work with json as pickle"""

    def __init__(self, filepath):
        self.filepath = filepath

    def save_data(self, data) -> None:
        """Update and save data to json"""
        current_data = self.load_data()
        current_data.update(data)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(current_data, f)

    def load_data(self) -> dict:
        """Load data from json file"""
        with open(self.filepath, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        return loaded_data


class HttpHandler(BaseHTTPRequestHandler):
    """HttpHandler"""

    def do_GET(self):
        """Process GET requests"""
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_json(STORAGE_PATH)
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        """Process POST request"""
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = dict([el.split("=") for el in data_parse.split("&")])
        json_handler = JsonDataHandler(STORAGE_PATH)
        json_handler.save_data({str(datetime.now()): data_dict})
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        """Process html files"""
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        """Process static files"""
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_json(self, filename, status=200):
        """Process json files"""
        json_handler = JsonDataHandler(filename)
        data = json_handler.load_data()
        rows_tmp = Template(
            """
        <h1><a href="/">Home</a></h1>
        {% if data %}
            {% for timestamp, info in data.items() %}
            <li>{{ timestamp }}: {{info['username']}} {{info['message']}}</li>
            {% endfor %}
        {% else %}
        <h2>Not messages yet.</h2>
        {% endif %}
        """
        )
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        output = rows_tmp.render(
            data=data,
        )
        self.wfile.write(output.encode(encoding="utf-8"))


def run(server_class=HTTPServer, handler_class=HttpHandler):
    """Run server"""
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
