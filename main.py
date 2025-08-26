from flask import Flask, request, jsonify, redirect, url_for, render_template_string
import threading, time, requests, os

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Memory store
tasks = {}    # {task_key: True/False}
logs = {}     # {task_key: [log_lines]}
owner_logged_in = False
OWNER_PASSWORD = "rowedyking"

# ==================== HTML ====================
HTML_PAGE = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Multi-Token Auto Poster</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Rajdhani:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0d0d12;
            --bg-darker: #07070a;
            --accent: #ff2a6d;
            --accent-dark: #d1004d;
            --text: #e0e0e8;
            --text-dim: #a0a0b0;
            --card-bg: #151520;
            --card-border: #252535;
            --input-bg: #1a1a2a;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background-color: var(--bg-dark);
            background-image:
                radial-gradient(circle at 15% 50%, rgba(120, 20, 80, 0.2) 0%, transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(80, 20, 120, 0.2) 0%, transparent 25%),
                radial-gradient(circle at 50% 80%, rgba(160, 30, 90, 0.2) 0%, transparent 25%);
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            position: relative;
        }
        .header h1 {
            color: var(--accent);
            margin: 0;
            font-size: 3rem;
            letter-spacing: 3px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            text-shadow: 0 0 15px var(--accent);
            position: relative;
            display: inline-block;
            padding: 0 20px;
        }
        .header h1::before,
        .header h1::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 30px;
            height: 3px;
            background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
        }
        .header h1::before { left: -40px; }
        .header h1::after { right: -40px; }
        .header p {
            color: var(--text-dim);
            margin: 10px 0 0;
            font-size: 1.2rem;
            letter-spacing: 2px;
            font-weight: 500;
        }
        .panel {
            background-color: rgba(21, 21, 32, 0.9);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(255, 42, 109, 0.15);
            backdrop-filter: blur(5px);
            position: relative;
            overflow: hidden;
        }
        .panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(to right, transparent, var(--accent), transparent);
            box-shadow: 0 0 15px var(--accent);
        }
        .panel-title {
            color: var(--accent);
            margin-top: 0;
            margin-bottom: 25px;
            padding-bottom: 15px;
            font-size: 1.8rem;
            text-shadow: 0 0 5px var(--accent);
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            text-align: center;
            border-bottom: 1px solid var(--card-border);
            position: relative;
        }
        .panel-title::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            color: var(--text-dim);
            font-weight: 600;
            font-size: 1.1rem;
            letter-spacing: 0.5px;
        }
        input[type="text"],
        input[type="number"],
        input[type="file"],
        input[type="password"],
        select {
            width: 100%;
            padding: 14px 16px;
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.1rem;
            font-weight: 500;
            border-radius: 6px;
            transition: all 0.3s;
        }
        input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(255, 42, 109, 0.3);
        }
        button, input[type="submit"] {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark));
            color: white;
            border: none;
            padding: 16px 24px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 1.2rem;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px rgba(255, 42, 109, 0.3);
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }
        button::before, input[type="submit"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: all 0.5s;
            z-index: -1;
        }
        button:hover, input[type="submit"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 25px rgba(255, 42, 109, 0.5);
        }
        button:hover::before, input[type="submit"]:hover::before {
            left: 100%;
        }
        .threads-btn {
            background: linear-gradient(135deg, #252540, #151530);
        }
        .threads-btn:hover {
            background: linear-gradient(135deg, #353550, #252540);
        }
        .glow {
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 5px var(--accent); }
            to { text-shadow: 0 0 15px var(--accent), 0 0 25px var(--accent-dark); }
        }
        .file-input-container {
            position: relative;
        }
        .file-input-container::after {
            content: 'Choose File';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--accent);
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
            pointer-events: none;
        }
        input[type="file"] {
            padding-right: 100px;
        }
        #console-box {
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            border-radius: 6px;
            padding: 15px;
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1rem;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2.2rem; }
            .header h1::before, .header h1::after { display: none; }
            .panel { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="glow">🩷 OWNER ROWEDY KIING 🩷</h1>
            <p>Facebook Multi-Token Auto Poster</p>
        </div>

        {% if not owner %}
        <div class="panel">
            <h2 class="panel-title">Owner Login</h2>
            <form method="post" action="/">
                <div class="form-group">
                    <label>Enter Owner Password:</label>
                    <input type="password" name="owner_password" required placeholder="Enter password">
                </div>
                <input type="submit" value="Enter">
            </form>
        </div>
        {% endif %}

        {% if owner %}
        <div class="panel">
            <h2 class="panel-title">🩷 OWNER KIING PANEL 🩷</h2>
            <p>Active tasks: {{ tasks|length }}</p>
            <form method="get" action="/logout">
                <input type="submit" value="Logout" class="threads-btn">
            </form>
        </div>
        {% endif %}

        <div class="panel">
            <h2 class="panel-title">Auto Poster Controls</h2>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Facebook Token (single) or leave empty for file:</label>
                    <input type="text" name="token" placeholder="Enter single token">
                </div>
                <div class="form-group">
                    <label>Upload Token File (.txt, one per line):</label>
                    <div class="file-input-container">
                        <input type="file" name="token_file" accept=".txt">
                    </div>
                </div>
                <div class="form-group">
                    <label>Delay between posts (seconds):</label>
                    <input type="number" name="delay" value="60" min="1" required placeholder="Enter delay in seconds">
                </div>
                <div class="form-group">
                    <label>Upload Messages File (.txt, one per line):</label>
                    <div class="file-input-container">
                        <input type="file" name="post_file" accept=".txt" required>
                    </div>
                </div>
                <input type="submit" name="start_posting" value="Start Posting">
            </form>
        </div>

        <div class="panel">
            <h2 class="panel-title">Stop Posting</h2>
            <form method="post">
                <div class="form-group">
                    <label>Enter Stop Key:</label>
                    <input type="text" name="stop_key_input" required placeholder="Enter task key">
                </div>
                <input type="submit" name="stop_posting" value="Stop Posting">
            </form>
        </div>

        <div class="panel">
            <h2 class="panel-title">Logs</h2>
            <div class="form-group">
                <select id="task-select" onchange="changeTaskKey()">
                    <option value="" disabled selected>Select Task</option>
                    {% for k in tasks.keys() %}
                    <option value="{{k}}">{{k}}</option>
                    {% endfor %}
                </select>
            </div>
            <div id="console-box">No logs yet...</div>
        </div>
    </div>

    <script>
        let currentTaskKey = '';
        function changeTaskKey() {
            const sel = document.getElementById('task-select');
            currentTaskKey = sel.value;
            fetchLogs();
        }
        async function fetchLogs() {
            if (!currentTaskKey) {
                document.getElementById('console-box').textContent = 'No task selected.';
                return;
            }
            try {
                const resp = await fetch('/logs?current_key=' + encodeURIComponent(currentTaskKey));
                const data = await resp.json();
                const box = document.getElementById('console-box');
                box.textContent = data.logs.join('\\n');
                box.scrollTop = box.scrollHeight;
            } catch (e) {
                console.error(e);
            }
        }
        setInterval(fetchLogs, 2000);

        // Add animation to inputs when focused
        document.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'translateY(-3px)';
                this.parentElement.style.transition = 'transform 0.3s';
            });
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'translateY(0)';
            });
        });
    </script>
</body>
</html>
"""

# ==================== AUTO POST FUNCTION ====================
def auto_post(task_key, tokens, messages, delay):
    logs[task_key] = []
    logs[task_key].append(f"[Task {task_key}] Started with {len(tokens)} tokens, {len(messages)} messages.")
    try:
        i = 0
        while task_key in tasks:
            token = tokens[i % len(tokens)]
            message = messages[i % len(messages)]

            url = f"https://graph.facebook.com/me/feed"
            params = {"message": message, "access_token": token}
            r = requests.post(url, data=params)
            if r.status_code == 200:
                logs[task_key].append(f"[OK] Posted: {message[:30]}...")
            else:
                logs[task_key].append(f"[ERR] {r.text}")

            i += 1
            time.sleep(delay)
    except Exception as e:
        logs[task_key].append(f"Exception: {e}")
    logs[task_key].append("Task stopped.")

# ==================== ROUTES ====================
@app.route("/", methods=["GET","POST"])
def index():
    global owner_logged_in
    if request.method=="POST":
        if "owner_password" in request.form:
            if request.form["owner_password"]==OWNER_PASSWORD:
                owner_logged_in=True
                return redirect(url_for("index"))
        if "start_posting" in request.form:
            tokens=[]
            if request.form.get("token"):
                tokens.append(request.form.get("token"))

            if "token_file" in request.files:
                f=request.files["token_file"]
                if f.filename:
                    tokens+=f.read().decode().splitlines()

            messages=[]
            if "post_file" in request.files:
                f=request.files["post_file"]
                if f.filename:
                    messages+=f.read().decode().splitlines()

            delay=int(request.form.get("delay",60))
            task_key=str(int(time.time()))
            tasks[task_key]=True
            threading.Thread(target=auto_post,args=(task_key,tokens,messages,delay),daemon=True).start()
            return redirect(url_for("index"))

        if "stop_posting" in request.form:
            stop_key=request.form["stop_key_input"]
            if stop_key in tasks:
                tasks.pop(stop_key)
                logs[stop_key].append("Task stopped manually.")
            return redirect(url_for("index"))

    return render_template_string(HTML_PAGE, tasks=tasks, owner=owner_logged_in)

@app.route("/logs")
def get_logs():
    key=request.args.get("current_key")
    return jsonify({"logs": logs.get(key,[])})

@app.route("/logout")
def logout():
    global owner_logged_in
    owner_logged_in=False
    return redirect(url_for("index"))

# ==================== RUN ====================
if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
