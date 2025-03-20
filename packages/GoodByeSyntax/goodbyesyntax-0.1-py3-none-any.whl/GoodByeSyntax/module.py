"""
What Users Can Do:
1. **Use for Personal and Non-Commercial Purposes:**  
   Users can download and use the Software for personal projects, non-commercial projects, or educational purposes, as long as it's not for profit or commercial gain.

2. **Incorporate into Larger Projects:**  
   Users can include the Software in larger projects, either public or private, but **with proper attribution** (e.g., crediting the original author, "ByteLightDev").

3. **Modify for Personal Use:**  
   Users can modify the Software for their own use within a larger project, as long as any modifications are clearly documented (e.g., note which parts were changed).

4. **Publicly Distribute:**  
   Users can distribute their projects that use the Software publicly, but **U must provide proper attribution** to the original author and include the required notice ("This project includes software developed by [ByteLightDev], © 2025...").

---

### **What Users Can't Do:**
1. **Commercial Use Without Permission:**  
   Users cannot use the Software for commercial purposes (e.g., selling it, using it in a product sold for profit) without any **consent** from the Licensor.

2. **Resell or Sublicense the Software:**  
   Users cannot sell, lease, or sublicense the Software as a standalone product. The Software cannot be distributed as-is for a fee or bundled with another product for resale.

3. **Alter or Copy the Original Software (or parts of it) Without Permission:**  
   Users cannot modify the core form of the Software and then redistribute it as part of their project, unless U clearly state any changes made. Copying portions of the Software for redistribution or use in other projects **without the necessary modifications** is prohibited.

4. **Failing to Give Proper Attribution:**  
   If a user integrates the Software into any project that is shared or published, U must ensure the correct **attribution** notice is visible and readable, as specified in the agreement.

---

### **How U Can Use the Software:**
**1. Permission for Commercial Use or Profit**  
If you want to use the Software for **commercial purposes** (e.g., selling a product that includes it or using it in a business), you **must get permission** from the Licensor.  

Alternatively, you can use the Software commercially **without prior permission** if you **credit "ByteLightDev" properly** by:  
- Displaying the **ByteLightDev logo** in your commercial content.  
- Ensuring the logo appears **clearly** in the video for **at least 3 seconds** in **HD quality** and is **easily visible** (not hidden or covered).  

© 2025 [ByteLightDev]
"""




import pyautogui
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import logging
import socket
import http
import json
import io
import shutil
import subprocess
import os
import time
import random
import uuid
import inspect
import smtplib
from email.message import EmailMessage
import threading
import sys
import requests
import datetime
import re
import pyperclip
import tkinter as tk
import numpy as np
import sounddevice as sd
import string
import hashlib

def wait(key="s", num=1):
    if key.lower() == "s":
        time.sleep(num)
    elif key.lower() == "m":
        time.sleep(num * 60)
    elif key.lower() == "h":
        time.sleep(num * 3600)
    else:
        print("Error: Use 's' for seconds, 'm' for minutes, or 'h' for hours.")

def ifnull(_v, _d):
    return _d if _v is None or _v == "" else _v

def switch_case(_v, _c, d=None):
    action = _c.get(_v, d)
    return action() if callable(action) else action

def timer_function(func, seconds):
    time.sleep(seconds)
    func()

def iftrue(var, function):
    if var:
        function()

def iffalse(var, function):
    if not var:
        function()
        
def isequal(text,atext):
    if text.lower() == atext:return True
    else:return False

def until(function, whattodo):
    function()
    while True:
        whattodo()
        if function():break

def repeat(function, times):
    for _ in range(times):
        function()

def oncondit(condition, function_true, function_false):
    if condition:
        function_true()
    else:
        function_false()

def repeat_forever(function):
    while True:
        function()

def safe_run(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"Error occurred in function {func.__name__}: {e}")
        return None

def start_timer(seconds, callback):
    time.sleep(seconds)
    callback()

def generate_random_string(length=15):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_'
    return ''.join(random.choices(characters, k=length))

def get_ip_address():
    return socket.gethostbyname(socket.gethostname())

def send_email(subject, body, to_email, mailname, mailpass):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = mailname
    msg["To"] = to_email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(mailname, mailpass)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_unique_id():
    return str(uuid.uuid4())

def start_background_task(backtask):
    thread = threading.Thread(target=backtask)
    thread.start()

def nocrash(func):
    def wrapper(*args, **kwargs):
        return safe_run(func, *args, **kwargs)
    return wrapper

def parallel(*functions):
    threads = []
    for func in functions:
        thread = threading.Thread(target=func)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def gs(func):
    return inspect.getsource(func)

def Jctb(input_string):
    def char_to_binary(c):
        if c == ' ':
            return '0000000001'
        elif c == '\n':
            return '0000000010'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        if c in alphabet_upper:
            return format(alphabet_upper.index(c), '010b')
        elif c in alphabet_lower:
            return format(alphabet_lower.index(c) + 26, '010b')
        return None

    binary_string = ''.join(char_to_binary(char) for char in input_string if char_to_binary(char))
    return binary_string


def Jbtc(binary_input):
    def binary_to_char(binary_vector):
        if binary_vector == '0000000001':
            return ' '
        elif binary_vector == '0000000010':
            return '\n'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        num = int(binary_vector, 2)
        if 0 <= num <= 25:
            return alphabet_upper[num]
        elif 26 <= num <= 51:
            return alphabet_lower[num - 26]
        return None

    char_list = [binary_to_char(binary_input[i:i+10]) for i in range(0, len(binary_input), 10)]
    return ''.join(char_list)

import tkinter as tk
class Jwin:
    def __init__(self, layout, widgets_config, user_callbacks=None):
        self.root = tk.Tk()
        self.root.title("Dynamic Window")
        self.widgets = {}
        self.user_callbacks = user_callbacks or {}
        self.layout_lines = [line.strip() for line in layout.strip().split("\n") if line.strip()]
        self.num_rows = len(self.layout_lines)
        self.num_cols = max(len(line) for line in self.layout_lines)
        for r in range(self.num_rows):
            self.root.grid_rowconfigure(r, weight=1)
        for c in range(self.num_cols):
            self.root.grid_columnconfigure(c, weight=1)
        self._create_widgets(widgets_config)
        self._create_layout()

    def _create_widgets(self, widgets_config):
        for widget_config in widgets_config:
            row, col = widget_config['position']
            widget_type = widget_config['type']
            options = widget_config.get('options', {})
            widget = self._create_widget(widget_type, options)
            if widget:
                widget.grid(row=row, column=col, padx=5, pady=5)
                widget_id = options.get("id")
                if widget_id:
                    self.widgets[widget_id] = widget

    def _create_widget(self, widget_type, options):
        if widget_type == "button":
            return tk.Button(self.root, text=options.get("text", "Button"),
                             command=lambda: self._execute_callback(options.get("id")))
        elif widget_type == "label":
            return tk.Label(self.root, text=options.get("text", "Label"))
        elif widget_type == "input":
            return tk.Entry(self.root)
        elif widget_type == "password":
            return tk.Entry(self.root, show="*")
        elif widget_type == "checkbox":
            return tk.Checkbutton(self.root, text=options.get("text", "Checkbox"))
        elif widget_type == "textarea":
            return tk.Text(self.root, height=5, width=20)
        else:
            return tk.Label(self.root, text=f"Unsupported: {widget_type}")

    def _create_layout(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.layout_lines[r][c] == " ":
                    continue

    def _execute_callback(self, widget_id):
        if widget_id and widget_id in self.user_callbacks:
            callback = self.user_callbacks[widget_id]
            if callable(callback):
                callback()

    def run(self):
        self.root.mainloop()


    def show_error_messagebox(message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", message)

def encode_base64(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    binary_data = ''.join([f"{ord(c):08b}" for c in data])
    padding = len(binary_data) % 6
    if padding != 0:
        binary_data += '0' * (6 - padding)
    encoded = ''.join([base64_chars[int(binary_data[i:i+6], 2)] for i in range(0, len(binary_data), 6)])
    encoded += "=" * ((4 - len(encoded) % 4) % 4)
    return encoded

def decode_base64(encoded_data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    encoded_data = encoded_data.rstrip("=")
    binary_data = ''.join([f"{base64_chars.index(c):06b}" for c in encoded_data])
    decoded = ''.join([chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)])
    return decoded

def reverse_string(string):
    return string[::-1]

def calculate_factorial(number):
    if number == 0:
        return 1
    return number * calculate_factorial(number - 1)

def generate_random_string(length=15):
    charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_'
    random_string = ''
    for _ in range(length):
        random_string += charset[calculate_factorial(len(charset)) % len(charset)]
    return random_string

def swap_values(a, b):
    return b, a

def replace(string,replacement,replacment):return string.replace(replacement,replacment)

def find_maximum(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def find_minimum(numbers):
    min_val = numbers[0]
    for num in numbers:
        if num < min_val:
            min_val = num
    return min_val

def sum_list(lst):
    total = 0
    for num in lst:
        total += num
    return total

def reverse_list(lst):
    return lst[::-1]

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def split_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def unique_elements(lst):
    unique_lst = []
    for item in lst:
        if item not in unique_lst:
            unique_lst.append(item)
    return unique_lst

def calculate_average(numbers):
    if not numbers:
        return 0
    return sum_list(numbers) / len(numbers)

def calculate_median(numbers):
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    return sorted_numbers[mid]

def count_words(text):
    return len(text.split())

def count_sentences(text):
    sentences = text.split('.')
    return len([s for s in sentences if s.strip()])

def add_commas(input_string):
    return ','.join(input_string)

def remove_spaces(text):
    return ''.join([char for char in text if char != ' '])

def calculate_square_root(number):
    if number < 0:
        return None
    guess = number / 2.0
    for _ in range(20):
        guess = (guess + number / guess) / 2.0
    return guess

def find_files_by_extension(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def get_curr_dir():
    return os.getcwd()

def check_if_file_exists(file_path):
    return os.path.exists(file_path)

def monitor_new_files(directory, callback):
    known_files = set(os.listdir(directory))
    while True:
        current_files = set(os.listdir(directory))
        new_files = current_files - known_files
        if new_files:
            callback(new_files)
        known_files = current_files
        time.sleep(1)


def monitor_file_changes(file_path, callback):
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            callback()
        time.sleep(1)

def write_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def parse_json(json_string):
    return json.loads(json_string)

def create_file_if_not_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write('')

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_zip_file(source_dir, output_zip):
    shutil.make_archive(output_zip, 'zip', source_dir)

def extract_zip_file(zip_file, extract_dir):
    shutil.unpack_archive(zip_file, extract_dir)

def move_file(source, destination):
    shutil.move(source, destination)

def copy_file(source, destination):
    shutil.copy(source, destination)

def show_file_properties(file_path):
    stats = os.stat(file_path)
    return f"Size: {stats.st_size} bytes, Last Modified: {time.ctime(stats.st_mtime)}"


def start_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server started on {ip}:{port}")
    httpd.serve_forever()

def stop_http_server():
    print("Stopping server...")
    exit(0)

def get_server_status(url="http://localhost:8000"):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Server is up and running.")
        else:
            print(f"Server is down. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

def set_server_timeout(timeout=10):
    socket.setdefaulttimeout(timeout)
    print(f"Server connection timeout set to {timeout} seconds.")

def upload_file_to_server(file_path, url="http://localhost:8000/upload"):
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
        if response.status_code == 200:
            print(f"File successfully uploaded: {file_path}")
        else:
            print(f"File upload failed. Status Code: {response.status_code}")

def download_file_from_server(file_url, save_path):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded: {save_path}")
    else:
        print(f"File download failed. Status Code: {response.status_code}")

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Welcome! Server is running.")
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "online"}')
        else:
            self.send_response(404)
            self.end_headers()

def start_custom_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    print(f"Custom server started on {ip}:{port}")
    httpd.serve_forever()

def set_server_access_logs(log_file="server_access.log"):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    print(f"Access logs are being saved to {log_file}")

def get_server_logs(log_file="server_access.log"):
    try:
        with open(log_file, 'r') as log:
            logs = log.readlines()
            print("".join(logs))
    except FileNotFoundError:
        print(f"{log_file} not found.")

def restart_http_server():
    print("Restarting server...")
    os.execv(sys.executable, ['python'] + sys.argv)

def check_internet_connection():
    response = os.system("ping -c 1 google.com")
    return response == 0

def create_web_server(directory, port=8000):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving {directory} at http://localhost:{port}")
        httpd.serve_forever()

def create_custom_web_server(html, port=8000):
    html_content = html

    class CustomHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving custom HTML page at http://0.0.0.0:{port}")
        print("Anyone on the same network can access this. (if not work use this http://127.0.0.1:8000)")
        httpd.serve_forever()
def JynParser(rep):
    inj= """
    global main
    main = rep
    """
    exec()

def contains(input, str):
    return str in input

def Jusbcam(Device_Name):
    try:
        result = subprocess.run(
            ['wmic', 'path', 'Win32_PnPEntity', 'where', 'DeviceID like "USB%"', 'get', 'Name'],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if result.stdout:
            output = result.stdout.strip().split("\n")[1:]
            devices = [line.strip() for line in output if line.strip()]
            return contains(devices,Device_Name)
        else:
            return []
    except Exception as e:
        print(f"Error detecting devices: {e}")
        return []

def defseprator(option_count, *options):
    if len(options) != option_count:
        raise ValueError(f"Expected {option_count} options, but got {len(options)}.")
    result = [1 if option else 0 for option in options]
    return ",".join(map(str, result))


def claw(html_option, html, ip, port, subdomain_option, subdomain_count, subdomains, return_server_logs_option):
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        MAIN_HTML = "<h1>Default Page</h1>"
        SUBDOMAINS = {}
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(self.MAIN_HTML.encode("utf-8"))
            elif self.path in self.SUBDOMAINS:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(self.SUBDOMAINS[self.path].encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
            if self.server.log_requests:logging.info(f"Request: {self.command} {self.path} from {self.client_address}")
    if return_server_logs_option:logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    if html_option:CustomHandler.MAIN_HTML = html
    if subdomain_option:
        for i in range(1, subdomain_count + 1):
            sub_path = f"/sub{i}"
            CustomHandler.SUBDOMAINS[sub_path] = subdomains.get(sub_path, f"<h1>Subdomain {i}</h1>")
    server = socketserver.TCPServer((ip, port), CustomHandler)
    server.log_requests = return_server_logs_option
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Server started at http://{ip}:{port}")
    return server

class ConsoleCam:
    def __init__(self):
        self._original_stdout = sys.stdout
        self._buffer = io.StringIO()
        sys.stdout = self._buffer
    @classmethod
    def start(cls):
        instance = cls()
        instance._buffer.truncate(0)
        instance._buffer.seek(0)
        return instance
    def get_new(self):return self._buffer.getvalue()
    def stop(self):sys.stdout = self._original_stdout

def prn(str):print(str)

class Key:
    def __init__(self, key):
        self.key = key

    def press(self):
        pyautogui.keyDown(self.key)
        print(f"Key '{self.key}' pressed.")

    def release(self):
        pyautogui.keyUp(self.key)
        print(f"Key '{self.key}' released.")

def copy_to_clipboard(text):
    pyperclip.copy(text)

def count_occurrences(lst, element):return lst.count(element)

def get_curr_time():now = datetime.datetime.now();return now.strftime("%Y-%m-%d %H:%M:%S")

def is_palindrome(s):return s == s[::-1]

def get_min_max(list):return min(list),max(list)

def is_digits(input):return input.isdigit()

def create_dict(keys, values):return dict(zip(keys, values))

def square_number(input):return input ** 2

def get_file_size(file_path):return os.path.getsize(file_path)

def find_duplicates(lst):
    seen = set()
    duplicates = []
    for item in lst:
        if item in seen:duplicates.append(item)
        else:seen.add(item)
    return duplicates

def get_average(list):
    if not list:return 0
    return sum(list) / len(list)

def divide(a, b):
    if b == 0:return None
    return a / b

def extract_numbers(s):return [int(x) for x in re.findall(r'\d+', s)]

class BinTrig:
    @classmethod
    def exit(cls, winroot, trig):
        def close_and_destroy():
            trig()
            winroot.destroy()
        winroot.protocol("WM_DELETE_WINDOW", close_and_destroy)

    def mouse_in(self, winroot, trig):
        winroot.bind("<Enter>", trig)

    def mouse_out(self, winroot, trig):
        winroot.bind("<Leave>", trig)

    def fullscreen(self, winroot, trig):
        def check_fullscreen(event=None):
            screen_width = winroot.winfo_screenwidth()
            screen_height = winroot.winfo_screenheight()
            window_width = winroot.winfo_width()
            window_height = winroot.winfo_height()
            if window_width == screen_width and window_height == screen_height:
                trig(event)
        winroot.bind("<Configure>", check_fullscreen)

    def minimized(self, winroot, trig):
        def check_minimized(event=None):
            if winroot.state() in ['iconic', 'withdrawn']:
                trig(event)
        winroot.bind("<Visibility>", check_minimized)

    def width_height(self, winroot, widmin, heimin, trig):
        def check_size(event=None):
            width = winroot.winfo_width()
            height = winroot.winfo_height()
            if width > widmin or height > heimin:
                trig(event)
        winroot.bind("<Configure>", check_size)

    def key_press(self, winroot, key, trig):
        winroot.bind(f"<KeyPress-{key}>", trig)

    def focus_gain(self, winroot, trig):
        winroot.bind("<FocusIn>", trig)

    def focus_loss(self, winroot, trig):
        winroot.bind("<FocusOut>", trig)

    def window_move(self, winroot, trig):
        winroot.bind("<Configure>", trig)

    def resize(self, winroot, trig):
        winroot.bind("<Configure>", trig)

    def close_shortcut(self, winroot, trig):
        winroot.bind("<Alt-F4>", trig)

    def mouse_button_press(self, winroot, button, trig):
        winroot.bind(f"<Button-{button}>", trig)

    def mouse_button_release(self, winroot, button, trig):
        winroot.bind(f"<ButtonRelease-{button}>", trig)

    def double_click(self, winroot, trig):
        winroot.bind("<Double-1>", trig)

    def mouse_motion(self, winroot, trig):
        winroot.bind("<Motion>", trig)

    def window_minimized(self, winroot, trig):
        def check_minimized(event=None):
            if winroot.state() == 'iconic':
                trig(event)
        winroot.bind("<Unmap>", check_minimized)

    def window_maximized(self, winroot, trig):
        def check_maximized(event=None):
            winroot.update_idletasks()
            if winroot.state() == 'zoomed':
                trig(event)
        winroot.bind("<Map>", check_maximized)
        winroot.bind("<Configure>", check_maximized)

    def window_restored(self, winroot, trig):
        def check_restored(event=None):
            if winroot.state() == 'normal':
                trig(event)
        winroot.bind("<Configure>", check_restored)

    def mouse_wheel_scroll(self, winroot, trig):
        winroot.bind("<MouseWheel>", trig)

    def text_change(self, widget, trig):
        widget.bind("<KeyRelease>", trig)

    def focus_on_widget(self, widget, trig):
        widget.bind("<FocusIn>", trig)

    def focus_off_widget(self, widget, trig):
        widget.bind("<FocusOut>", trig)

class ByteJar:
    def __init__(self, host="127.0.0.1", port=8090):
        self.host = host
        self.port = port
        self.client_socket = None

    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            response = self.client_socket.recv(1024).decode().strip()
            print(f"DEBUG: Server response: {response}")  
            return response
        except Exception as e:
            return f"Error connecting to server: {e}"

    def stop(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            return "Connection closed."
        return "No active connection."

    def send_command(self, command):
        if not self.client_socket:
            return "Error: No active connection. Please start the connection first."

        try:
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode().strip()
            print(f"DEBUG: Server response: {response}")  
            return response
        except Exception as e:
            return f"Error while sending command: {e}"

def letterglue(str="", *substr, str2=""):return str + ''.join(substr) + str2

def letterglue_creator(word):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    original_vars = [(alphabet[i % 26] * ((i // 26) + 1), letter) for i, letter in enumerate(word)]
    shuffled_vars = original_vars[:]
    random.shuffle(shuffled_vars)
    defs_line = "; ".join([f'{var}="{ch}"' for var, ch in shuffled_vars]) + ";"
    glue_order = ", ".join([var for var, _ in original_vars])
    code = defs_line + "\n"
    code += "result = letterglue(" + glue_order + ")\n"
    code += "print(result)"
    return code

def Baudio(filename="audio_data", mode="Write", duration=5, Warn=True):
    def BprecAU(fname, Warn=Warn):
        if Warn:
            print("Playing audio...")
        samplerate = 44100
        with open(letterglue(fname, ".Bau"), 'rb') as f:
            audio_data = f.read()
        audio_data_np = np.frombuffer(audio_data, dtype='float32')
        sd.play(audio_data_np, samplerate=samplerate)
        sd.wait()
        if Warn:
            print(f"Audio playback from {fname}.Bau finished.")

    host = "127.0.0.1"
    port = 65432
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    client_socket.sendall("record".encode())
    client_socket.sendall(duration.to_bytes(4, 'big'))
    
    audio_length = int.from_bytes(client_socket.recv(4), 'big')
    audio_data = b""
    while len(audio_data) < audio_length:
        audio_data += client_socket.recv(1024)
    
    client_socket.close()
    
    if mode.lower() == "write":
        with open(letterglue(filename, ".Bau"), 'wb') as f:
            f.write(audio_data)
        if Warn:
            print(f"Audio recorded and saved to {filename}.Bau.")
            
    elif mode.lower() == "return":
        audio_np = np.frombuffer(audio_data, dtype='float32')
        if Warn:
            print("Audio recorded and returned as a numpy array.")
        return audio_np
    elif mode.lower() == "play":
        BprecAU(filename)
    else:
        raise ValueError("Invalid mode. Please use 'Write', 'Return' or 'Play'.")

class Btuple:
    @classmethod
    def count(cls, *words):
        return len(words)
    @classmethod
    def get(cls, index, *words):
        if 0 <= index < len(words):
            return words[index-1]
        return "Error: Please choose a number within range."
    @classmethod
    def exists(cls, item, *words):
        return item in words

    @classmethod
    def first(cls, *words):
        return words[0] if words else "Error: Tuple is empty."

    @classmethod
    def last(cls, *words):
        return words[-1] if words else "Error: Tuple is empty."

def isgreater(*nums):
    tc = Btuple.count(*nums)
    t1 = Btuple.get(*nums, 1)
    t2 = Btuple.get(*nums, 2)
    if tc != 2:
        print("There should be 2 numbers inputted!")
        return False
    elif tc == 0:
        print("Input can't be empty!")
        return False
    elif t1 > t2:return True
    else:return False

def runwfallback(func, fallback_func):
    try:return func()
    except Exception as e:return fallback_func()

def retry(func, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    print("All attempts failed.")
    return None

def fftime(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def debug(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

def paste_from_clipboard():return pyperclip.paste()

def watch_file(filepath, callback):
    last_modified = os.path.getmtime(filepath)
    while True:
        time.sleep(1)
        if os.path.getmtime(filepath) != last_modified:
            last_modified = os.path.getmtime(filepath)
            callback(filepath)

def is_website_online(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:return False

def shorten_url(long_url):
    response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
    return response.text

def celsius_to_fahrenheit(c):return (c * 9/5) + 32

def fahrenheit_to_celsius(f):return (f - 32) * 5/9

def efv(code: str):
    fc = code.replace(",", ";")
    local_vars = {}
    exec(fc, {}, local_vars)
    return local_vars

def Hpass(limit=30):
    def e(length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def d(word1, word2):
        current_time = str(int(time.time()))
        mixed = ''.join(random.sample(word1 + word2 + current_time, len(word1 + word2 + current_time)))
        return mixed
    def c(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    def a(hash_value):
        result = []
        for char in hash_value:
            byte_val = (ord(char) * 10) % 256
            result.append(chr(byte_val))
        return ''.join(result)
    lc=limit
    def b(word1, word2):
        mixed1 = d(word1, word2)
        hashed1 = c(mixed1)
        jcbt1 = a(hashed1)
        mixed2 = d(word1, word2 + jcbt1)
        hashed2 = c(mixed2)
        final_jcbt = a(hashed2)
        return final_jcbt
    def o(word1, word2):
        result1 = b(word1, word2)
        result2 = b(word1, word2)
        current_time = str(int(time.time()))
        final_result = result1 + result2 + current_time
        return final_result
    def c2n(input_string):
        result = []
        for char in input_string:result.append(str(ord(char)))
        return ''.join(result)
    def n2c(number):
        number_str = str(number)
        result = []
        for digit in number_str:
            char = chr(96 + int(digit))
            if random.choice([True, False]):char = char.upper()
            result.append(char)
        return ''.join(result)
    def ltc(imp,cc):return imp[:cc]
    word1 = e();word2 = e()
    N="w"; P="r"; H="o"; C="="; D=" "; F="("; A="o"; R="2"; L=","; K="1"; E="o"; Q="d"; M=" "; B="o"; S=")"; O="o"; I="r"; J="d"; G="w"
    result = letterglue(A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S)
    context = {'word1': word1, 'word2': word2, 'o': o}
    exec(result, globals(), context)
    crs=c2n(context.get("oo"))
    nms=n2c(crs)
    return ltc(replace(nms,"`",""),lc)

def l(input):return list(input)

def dl(input):return ''.join(input)

def mix(input):shuffled = l(input);random.shuffle(shuffled);return dl(shuffled)

def sugar(input):
    rn = random.randint(1, len(input))
    random_number_string = ''.join(random.choices("01243213132112576635439769813224562133489", k=5))
    length = len(input) - 1
    a = list(add_commas(input))
    random.shuffle(a)
    b = generate_random_string(length)
    c = letterglue(''.join(a), b)
    c_list = list(c)
    random.shuffle(c_list)
    c_shuffled = ''.join(c_list)
    d = c_shuffled.replace(",", "")
    d_list = list(d)
    random.shuffle(d_list)
    d_shuffled = ''.join(d_list)
    rn_str = add_commas(str(rn))
    rn_list = list(rn_str)
    random.shuffle(rn_list)
    rn_shuffled = ''.join(rn_list)
    combined = letterglue(random_number_string, rn_shuffled + d_shuffled)
    combined_list = list(combined)
    random.shuffle(combined_list)
    f1 = ''.join(combined_list)
    return replace(mix(f1), ",", "")