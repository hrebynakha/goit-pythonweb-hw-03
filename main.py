"""Homw work 3"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

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


class HtmlTemplate:
    """Html template reneder using Jinja2"""

    def __init__(self, template_path):
        self.env = Environment(loader=FileSystemLoader("."))
        self.template = self.env.get_template(template_path)

    def render_bytes(self, **kwargs) -> bytes:
        """Return html template as encoded utf-8 bytes"""
        output = self.template.render(
            **kwargs,
        )
        return output.encode("utf-8")


class HttpHandler(BaseHTTPRequestHandler):
    """HttpHandler"""

    def do_GET(self):
        """Process GET requests"""
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read" and pr_url.query == "format=json":
            self.send_json(STORAGE_PATH)
        elif pr_url.path == "/read":
            self.send_template("output.html", filename=STORAGE_PATH)
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

    def send_static(
        self,
    ):
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
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_template(self, template_path, data=None, filename=None, status=200):
        """Send html file as Jinja2 template with data"""
        if not data:
            data = JsonDataHandler(filename).load_data()
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HtmlTemplate(template_path).render_bytes(data=data))


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
