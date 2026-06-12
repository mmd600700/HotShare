from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import urllib.parse
from pathlib import Path
import os
import socket
import sys
import tkinter as tk
from tkinter import filedialog
from QR import generate_qr_code

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return "127.0.0.1"
    
def loadHTML(htpath: str):
    actual_path = resource_path(htpath)
    with open(actual_path, "r", encoding="utf-8") as f:
        htcontent = f.read()
    return htcontent

BUFFER_SIZE = 1024 * 1024 * 4
SAVE_PATH = Path.home() / "Downloads" / "HotShareFile"
IPPORT = f'{get_local_ip()}:8888/'
SELECTED_FILES = []
server = None
server_thread = None
canclearpostget = False 

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            html = loadHTML("index.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return
            
        if self.path == "/q":
            stop_server()
            return
            
        if self.path == "/downloadss":
            items = ""
            i = 0
            for p in SELECTED_FILES:
                name = p.name
                items += '<li><a href="/download/' + str(i) + '">'+ name +'</a></li><br>'
                i += 1
            html = loadHTML("down.html")
            html = html.replace("{{items}}", items)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        if self.path.startswith("/download/"):
            idx = int(self.path.split("/")[-1])
            if idx >= len(SELECTED_FILES):
                self.send_response(404)
                self.end_headers()
                return
            path = SELECTED_FILES[idx]
            filename = path.name
            total_size = os.path.getsize(path)

            f = open(path, "rb")
            filename = urllib.parse.quote(filename)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{filename}")
            self.send_header("Content-Length", str(total_size))
            self.end_headers()
            sent = 0
            lastPercent = -1
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                self.wfile.write(data)
                sent += len(data)
                percent = int(sent * 100 / total_size)
                if percent != lastPercent:
                    lastPercent = percent
                    update_file_progress(filename, percent, 1, f"{idx+1}/{len(SELECTED_FILES)}")
            f.close()
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/upload":
            name = self.headers.get("X-File-Name")
            FileIndex = self.headers.get("X-File-Index")
            name = urllib.parse.unquote(name)
            size = self.headers.get("X-File-Size")       
            length = int(self.headers.get("Content-Length", 0))
            os.makedirs(SAVE_PATH, exist_ok=True)
            filepath = os.path.join(SAVE_PATH, name)

            remaining = length
            received = 0
            lastPercent = -1
            
            with open(filepath, "wb") as f:
                while remaining > 0:
                    read_size = min(BUFFER_SIZE, remaining)
                    data = self.rfile.read(read_size)
                    if not data:
                        break
                    chunk_size = len(data)
                    f.write(data)
                    received += chunk_size
                    remaining -= len(data)
                    
                    percent = (received / length) * 100
                    if percent != lastPercent:
                        lastPercent = percent
                        update_file_progress(name, percent, 2, FileIndex)        
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            self.wfile.flush()

def start_server():
    global server
    try:
        server = ThreadingHTTPServer(("0.0.0.0", 8888), Handler)
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

def stop_server():
    global server, server_thread
    if server:
        try:
            server.shutdown()
            server.server_close()
        except Exception as e:
            print(f"Stop error: {e}")
        server = None
    if server_thread:
        server_thread.join(timeout=1)
        server_thread = None

file_index1 = {}
file_index2 = {}

def select_files():
    files = filedialog.askopenfilenames(title="Select files to share")
    if not files:
        return
    SELECTED_FILES.clear()
    file_index1.clear()
    for f in files:
        SELECTED_FILES.append(Path(f))
    i = 1    
    for f in SELECTED_FILES:
        update_file_progress(f.name, 0, 1, f"{i}/{len(SELECTED_FILES)}")
        i += 1
    if len(SELECTED_FILES) != 0:
        btn.config(text=f"selected {len(SELECTED_FILES)} File")    
    else:
        btn.config(text="Select File")

root = tk.Tk()
root.title("HotShareFile")
root.configure(bg="#1e1e1e")
root.geometry("700x600")

top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=10)

text_label = tk.Label(top_frame, text=IPPORT, fg="#ff1cb3", bg="#1e1e1e", font=("tahoma", 16, "italic"))
text_label.pack()

img = tk.PhotoImage(width=210, height=210)
img_label = tk.Label(top_frame, image=img, bg="#1e1e1e")
visible = True

def toggle():
    global IPPORT, visible
    IPPORT = f'{get_local_ip()}:8888/'
    if visible:
        text_label.pack_forget()
        img_label.pack()
        qr_matrix = generate_qr_code(210, "http://"+IPPORT)
        img_data = []
        for row in qr_matrix:
            row_colors = ["#000000" if pixel == 1 else "#FFFFFF" for pixel in row]
            img_data.append("{" + " ".join(row_colors) + "}")    
        img.put(" ".join(img_data))    
        visible = False
    else:
        img_label.pack_forget()
        text_label.pack()
        visible = True

text_label.bind("<Button-1>", lambda e: toggle())
img_label.bind("<Button-1>", lambda e: toggle())

btn = tk.Button(root, text="Select File", bg="#333333", fg="#ffffff", font=("tahoma", 13, "bold"), activebackground="#444444", activeforeground="#ffffff", command=select_files)
btn.pack(pady=15)

frame1 = tk.Frame(root, bg="#1e1e1e")
frame1.pack(fill="both", expand=True, padx=10, pady=5)

scroll1 = tk.Scrollbar(frame1)
scroll1.pack(side="right", fill="y")

text1 = tk.Listbox(frame1, height=8, bg="#121212", fg="#00ffaa", yscrollcommand=scroll1.set)
text1.pack(fill="both", expand=True)

scroll1.config(command=text1.yview)

frame2 = tk.Frame(root, bg="#1e1e1e")
frame2.pack(fill="both", expand=True, padx=10, pady=5)

scroll2 = tk.Scrollbar(frame2)
scroll2.pack(side="right", fill="y")

text2 = tk.Listbox(frame2, height=8, bg="#121212", fg="#ffaa00", yscrollcommand=scroll2.set)
text2.pack(fill="both", expand=True)
scroll2.config(command=text2.yview)

def update_file_progress(filename: str, percentage: int, target: int, indexs: str):
    global canclearpostget
    box = text1 if target == 1 else text2
    if target == 1:
        box = text1
        index_dict = file_index1
        if len(index_dict) == 0:
            box.delete(0, "end")
    else:
        box = text2
        index_dict = file_index2     
    
    if canclearpostget and target == 2:
        box.delete(0, "end")
        index_dict.clear()
        canclearpostget = False 

    partsIndex = indexs.split("/")
    if len(partsIndex) == 2 and partsIndex[0] == partsIndex[1] and percentage == 100 and target == 2:
        canclearpostget = True   

    bar_length = 20
    filled_length = int(bar_length * percentage // 100)
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    line_text = f"{filename} | [{bar}] {int(percentage)}%   {indexs}\n"
    if filename in index_dict:
        i = index_dict[filename]
        box.delete(i)
        box.insert(i, line_text)
    else:
        i = box.size()
        box.insert("end", line_text)
        index_dict[filename] = i
    box.see("end")

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

root.mainloop()