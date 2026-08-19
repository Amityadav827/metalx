#!/usr/bin/env python3

import os
import json
import shutil
import threading
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import tkinter as tk
from tkinter import filedialog, messagebox

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".heic", ".heif", ".bmp", ".tiff", ".tif"
}

# -----------------------------
# Choose source folder
# -----------------------------

root = tk.Tk()
root.withdraw()

SOURCE = filedialog.askdirectory(
    title="Select the folder containing your images"
)

if not SOURCE:
    raise SystemExit("No folder selected.")

SOURCE = Path(SOURCE).resolve()
DEST = (SOURCE / "Material Done").resolve()

if not DEST.exists():
    messagebox.showerror(
        "Error",
        f"'Material Done' folder nahi mila:\n\n{DEST}"
    )
    raise SystemExit(1)

if not DEST.is_dir():
    messagebox.showerror(
        "Error",
        f"'Material Done' ek folder nahi hai:\n\n{DEST}"
    )
    raise SystemExit(1)


def get_images():
    """Get images directly inside source folder."""
    images = []

    for p in SOURCE.iterdir():
        if (
            p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
        ):
            images.append(p.name)

    return sorted(images, key=str.lower)


def safe_source_path(filename):
    """Prevent path traversal."""
    path = (SOURCE / filename).resolve()

    if path.parent != SOURCE:
        raise ValueError("Invalid path")

    return path


def safe_dest_path(filename):
    path = (DEST / filename).resolve()

    if path.parent != DEST:
        raise ValueError("Invalid path")

    return path


# -----------------------------
# Browser UI
# -----------------------------

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Image Sorter</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #111;
    color: #eee;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    overflow: hidden;
}

#topbar {
    height: 58px;
    background: #1c1c1e;
    display: flex;
    align-items: center;
    padding: 0 18px;
    gap: 15px;
    border-bottom: 1px solid #333;
}

#filename {
    font-size: 15px;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

#counter {
    color: #aaa;
    font-size: 14px;
}

button {
    border: 0;
    border-radius: 8px;
    padding: 9px 15px;
    color: white;
    background: #333;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background: #444;
}

#doneBtn {
    background: #0a8f3d;
    font-weight: 600;
}

#doneBtn:hover {
    background: #0cad4b;
}

#viewer {
    height: calc(100vh - 145px);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #080808;
}

#image {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    user-select: none;
    -webkit-user-drag: none;
    cursor: grab;
    transform-origin: center center;
}

#image.dragging {
    cursor: grabbing;
}

#hint {
    position: absolute;
    bottom: 15px;
    left: 50%;
    transform: translateX(-50%);
    color: #777;
    font-size: 12px;
    pointer-events: none;
}

#bottom {
    height: 87px;
    background: #1c1c1e;
    border-top: 1px solid #333;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 15px;
    overflow-x: auto;
}

.thumb {
    height: 68px;
    width: 82px;
    flex: 0 0 auto;
    object-fit: cover;
    border-radius: 5px;
    border: 2px solid transparent;
    cursor: pointer;
    background: #292929;
}

.thumb.active {
    border-color: #0a84ff;
}

#empty {
    text-align: center;
    color: #aaa;
}

#zoomLabel {
    min-width: 55px;
    text-align: center;
    color: #aaa;
}

.progress {
    position: absolute;
    top: 0;
    left: 0;
    height: 3px;
    background: #0a84ff;
    width: 0%;
    transition: width .15s;
}

#toast {
    position: fixed;
    left: 50%;
    top: 75px;
    transform: translateX(-50%);
    background: rgba(0,0,0,.85);
    padding: 10px 18px;
    border-radius: 8px;
    display: none;
    z-index: 10;
}
</style>
</head>

<body>

<div id="topbar">
    <button onclick="previousImage()">← Previous</button>

    <div id="filename">Loading...</div>

    <div id="counter"></div>

    <button onclick="resetZoom()">Reset Zoom</button>
    <div id="zoomLabel">100%</div>

    <button id="doneBtn" onclick="moveCurrent()">
        ✓ Material Done
    </button>

    <button onclick="nextImage()">Next →</button>
</div>

<div id="viewer">
    <div class="progress" id="progress"></div>

    <img id="image" draggable="false">

    <div id="hint">
        Mouse wheel = Zoom &nbsp; • &nbsp;
        Drag = Pan &nbsp; • &nbsp;
        M = Material Done &nbsp; • &nbsp;
        ← → = Navigate
    </div>
</div>

<div id="bottom"></div>

<div id="toast"></div>

<script>

let images = [];
let current = 0;

let zoom = 1;
let panX = 0;
let panY = 0;

let dragging = false;
let dragStartX = 0;
let dragStartY = 0;

const img = document.getElementById("image");
const viewer = document.getElementById("viewer");


async function loadImages() {
    const response = await fetch("/api/list");
    images = await response.json();

    if (images.length === 0) {
        document.getElementById("filename").textContent =
            "No images found";
        return;
    }

    renderThumbnails();
    showImage(0);
}


function renderThumbnails() {
    const bottom = document.getElementById("bottom");
    bottom.innerHTML = "";

    images.forEach((name, index) => {
        const thumb = document.createElement("img");

        thumb.className = "thumb";
        thumb.src = "/image/" + encodeURIComponent(name);
        thumb.title = name;

        thumb.onclick = () => showImage(index);

        bottom.appendChild(thumb);
    });
}


function showImage(index) {
    if (!images.length) return;

    current = Math.max(0, Math.min(index, images.length - 1));

    const name = images[current];

    img.src = "/image/" + encodeURIComponent(name);

    document.getElementById("filename").textContent = name;

    document.getElementById("counter").textContent =
        `${current + 1} / ${images.length}`;

    resetZoom();

    document.querySelectorAll(".thumb").forEach((el, i) => {
        el.classList.toggle("active", i === current);
    });

    const percentage =
        ((current + 1) / images.length) * 100;

    document.getElementById("progress").style.width =
        percentage + "%";

    // Keep active thumbnail visible
    const active = document.querySelector(".thumb.active");

    if (active) {
        active.scrollIntoView({
            behavior: "smooth",
            inline: "center",
            block: "nearest"
        });
    }
}


function nextImage() {
    if (current < images.length - 1) {
        showImage(current + 1);
    }
}


function previousImage() {
    if (current > 0) {
        showImage(current - 1);
    }
}


function resetZoom() {
    zoom = 1;
    panX = 0;
    panY = 0;
    updateTransform();
}


function updateTransform() {
    img.style.transform =
        `translate(${panX}px, ${panY}px) scale(${zoom})`;

    document.getElementById("zoomLabel").textContent =
        Math.round(zoom * 100) + "%";
}


// Zoom with mouse wheel
viewer.addEventListener("wheel", function(e) {
    e.preventDefault();

    const oldZoom = zoom;

    if (e.deltaY < 0) {
        zoom *= 1.12;
    } else {
        zoom /= 1.12;
    }

    zoom = Math.max(.2, Math.min(8, zoom));

    // Small adjustment to make zoom feel natural
    if (zoom < 1) {
        panX *= zoom / oldZoom;
        panY *= zoom / oldZoom;
    }

    updateTransform();
}, { passive: false });


// Drag image
img.addEventListener("mousedown", function(e) {
    if (zoom <= 1) return;

    dragging = true;

    img.classList.add("dragging");

    dragStartX = e.clientX - panX;
    dragStartY = e.clientY - panY;
});

window.addEventListener("mousemove", function(e) {
    if (!dragging) return;

    panX = e.clientX - dragStartX;
    panY = e.clientY - dragStartY;

    updateTransform();
});

window.addEventListener("mouseup", function() {
    dragging = false;
    img.classList.remove("dragging");
});


// Keyboard shortcuts
document.addEventListener("keydown", function(e) {

    // Don't trigger shortcuts while typing
    if (e.target.tagName === "INPUT") return;

    if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        nextImage();
    }

    else if (e.key === "ArrowLeft") {
        e.preventDefault();
        previousImage();
    }

    else if (e.key.toLowerCase() === "m") {
        e.preventDefault();
        moveCurrent();
    }

    else if (e.key === "0") {
        resetZoom();
    }
});


async function moveCurrent() {
    if (!images.length) return;

    const name = images[current];

    if (!confirm(`"${name}" ko Material Done mein move karna hai?`)) {
        return;
    }

    const response = await fetch(
        "/api/move?name=" + encodeURIComponent(name),
        { method: "POST" }
    );

    const result = await response.json();

    if (!result.ok) {
        alert(result.error || "Move failed");
        return;
    }

    showToast("✓ Moved to Material Done");

    images.splice(current, 1);

    if (images.length === 0) {
        document.getElementById("filename").textContent =
            "🎉 All images processed!";
        document.getElementById("counter").textContent = "";
        img.style.display = "none";
        document.getElementById("bottom").innerHTML = "";
        return;
    }

    renderThumbnails();

    if (current >= images.length) {
        current = images.length - 1;
    }

    showImage(current);
}


function showToast(text) {
    const toast = document.getElementById("toast");

    toast.textContent = text;
    toast.style.display = "block";

    setTimeout(() => {
        toast.style.display = "none";
    }, 1000);
}


loadImages();

</script>

</body>
</html>
"""


# -----------------------------
# HTTP Server
# -----------------------------

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Keep terminal clean
        pass

    def send_json(self, data, status=200):
        raw = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()

        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            raw = HTML.encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(raw))
            )
            self.end_headers()

            self.wfile.write(raw)
            return

        if path == "/api/list":
            self.send_json(get_images())
            return

        if path.startswith("/image/"):
            from urllib.parse import unquote

            filename = unquote(path[len("/image/"):])

            try:
                file_path = safe_source_path(filename)

                if not file_path.exists() or not file_path.is_file():
                    self.send_error(404)
                    return

                data = file_path.read_bytes()

                ext = file_path.suffix.lower()

                mime = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                    ".bmp": "image/bmp",
                    ".tiff": "image/tiff",
                    ".tif": "image/tiff",
                    ".heic": "image/heic",
                    ".heif": "image/heif",
                }.get(ext, "application/octet-stream")

                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header(
                    "Content-Length",
                    str(len(data))
                )
                self.end_headers()

                self.wfile.write(data)

            except Exception as e:
                self.send_error(400, str(e))

            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path != "/api/move":
            self.send_error(404)
            return

        params = parse_qs(parsed.query)
        names = params.get("name")

        if not names:
            self.send_json({
                "ok": False,
                "error": "No filename"
            }, 400)
            return

        filename = names[0]

        try:
            source = safe_source_path(filename)
            destination = safe_dest_path(filename)

            if not source.exists():
                raise FileNotFoundError(
                    "Image source folder mein nahi mili."
                )

            # If same filename already exists in Material Done,
            # create a unique filename instead of overwriting.
            if destination.exists():
                stem = destination.stem
                suffix = destination.suffix

                counter = 1

                while True:
                    new_name = f"{stem} ({counter}){suffix}"
                    destination = safe_dest_path(new_name)

                    if not destination.exists():
                        break

                    counter += 1

            shutil.move(str(source), str(destination))

            self.send_json({
                "ok": True,
                "filename": destination.name
            })

        except Exception as e:
            self.send_json({
                "ok": False,
                "error": str(e)
            }, 400)


# -----------------------------
# Start server
# -----------------------------

server = ThreadingHTTPServer(
    ("127.0.0.1", 0),
    Handler
)

port = server.server_address[1]

url = f"http://127.0.0.1:{port}/"

print()
print("========================================")
print("       IMAGE SORTER RUNNING")
print("========================================")
print(f"Source: {SOURCE}")
print(f"Done:   {DEST}")
print(f"Browser: {url}")
print()
print("Browser band karne ke baad Terminal mein")
print("Ctrl+C press karke server stop kar sakte ho.")
print("========================================")
print()

thread = threading.Thread(
    target=server.serve_forever,
    daemon=True
)

thread.start()

webbrowser.open(url)

try:
    threading.Event().wait()
except KeyboardInterrupt:
    print("\nStopping...")
    server.shutdown()
    server.server_close()
