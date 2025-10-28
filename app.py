from flask import Flask, request, render_template_string, send_file, redirect, url_for
import yt_dlp
import os
import uuid
import threading

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FB & IG Video Downloader - Gazy's Tek Solutions</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #f4f6f8, #e9efff);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            width: 100%;
            background: #3b5998;
            color: white;
            padding: 14px;
            text-align: center;
            font-weight: bold;
            font-size: 1.3rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .container {
            margin-top: 50px;
            max-width: 650px;
            width: 92%;
        }
        .card {
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            animation: fadeIn 0.7s ease-in-out;
            background: white;
        }
        h1 {
            font-size: 1.9rem;
            color: #3b5998;
            margin-bottom: 20px;
        }
        .btn-primary {
            background: linear-gradient(90deg, #3b5998, #4267b2);
            border: none;
            transition: all 0.3s ease;
        }
        .btn-primary:hover {
            transform: scale(1.03);
            background: linear-gradient(90deg, #2d4373, #365899);
        }
        video, img.thumbnail {
            width: 100%;
            max-height: 250px;
            object-fit: cover;
            border-radius: 12px;
            margin-top: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .meta {
            text-align: left;
            margin-top: 10px;
        }
        .meta h5 {
            font-size: 1rem;
            color: #222;
            margin-bottom: 0;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 0.9em;
            color: #555;
        }
        .footer a {
            color: #3b5998;
            margin: 0 8px;
            font-size: 1.4em;
            text-decoration: none;
            transition: 0.3s;
        }
        .footer a:hover {
            color: #2d4373;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="navbar">Gazy's Tech Solutions</div>

    <div class="container">
        <div class="card text-center">
            <h1>Facebook & Instagram Video Downloader</h1>

            {% if not video_preview %}
            <form method="post" id="downloadForm">
                <input type="url" name="link" placeholder="Paste video link here" class="form-control mb-3" required>
                <button type="submit" class="btn btn-primary w-100">Preview Video</button>
                <div id="loading" style="display:none;" class="mt-3">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-2">Fetching video info...</p>
                </div>
            </form>
            {% endif %}

            {% if thumbnail %}
                <img src="{{ thumbnail }}" alt="Video thumbnail" class="thumbnail">
                <div class="meta mt-2">
                    <h5>{{ title }}</h5>
                </div>
            {% endif %}

            {% if video_preview %}
                <video controls src="{{ video_preview }}"></video>
                <form method="post" action="{{ url_for('download_video') }}">
                    <input type="hidden" name="file" value="{{ filename }}">
                    <button type="submit" class="btn btn-primary w-100 mt-3">Download Video</button>
                </form>
                <a href="/" class="btn btn-outline-secondary w-100 mt-3">🔁 Download Another</a>
            {% endif %}

            {% if error %}
            <div class="alert alert-danger mt-3">{{ error }}</div>
            {% endif %}
        </div>
    </div>

    <div class="footer">
        <p>© 2025 Gazy's Tek Solutions | Connect with our team | Bring all your tech related problems to us</p>
        <p>You can report issues as well as suggestions to our team</p>
        <a href="https://wa.me/233538770364" target="_blank"><i class="fab fa-whatsapp"></i></a>
        <a href="https://m.me/StreetDebee" target="_blank"><i class="fab fa-facebook"></i></a>
    </div>

    <script>
        const form = document.getElementById("downloadForm");
        if (form) {
            form.addEventListener("submit", () => {
                document.getElementById("loading").style.display = "block";
            });
        }
    </script>
</body>
</html>
"""

def auto_delete(filename, delay=180):
    """Delete temp file after delay to free space"""
    def remove_file():
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass
    threading.Timer(delay, remove_file).start()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("link")
        if not video_url:
            return render_template_string(HTML_PAGE, error="Please enter a valid link!", video_preview=None)

        unique_id = uuid.uuid4().hex
        filename = f"temp_{unique_id}.mp4"

        ydl_opts = {
            "outtmpl": filename,
            "format": "bestvideo+bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "skip_download": True
        }

        try:
            # Extract info
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get("title", "Unknown Title")
                thumbnail = info.get("thumbnail", "")

            # Download video
            with yt_dlp.YoutubeDL({"outtmpl": filename, "quiet": True, "format": "bestvideo+bestaudio/best"}) as ydl:
                ydl.download([video_url])

            auto_delete(filename)  # delete after 3 minutes
            return render_template_string(HTML_PAGE, video_preview=filename, filename=filename, title=title, thumbnail=thumbnail)

        except Exception as e:
            return render_template_string(HTML_PAGE, error=f"Failed to fetch video info: {e}", video_preview=None)

    return render_template_string(HTML_PAGE, video_preview=None)

@app.route("/download", methods=["POST"])
def download_video():
    filename = request.form.get("file")
    if filename and os.path.exists(filename):
        response = send_file(filename, as_attachment=True)
        auto_delete(filename, delay=10)
        return response
    return redirect(url_for("index"))

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
