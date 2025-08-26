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
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Facebook Multi-Token Auto Poster</title>
<style>
/* ---- full CSS paste karo yahan ---- */
body {margin:0;padding:0;background:#000;color:#eee;font-family:Arial,sans-serif;}
/* aur baaki CSS wahi jo pehle diya tha */
</style>
</head>
<body>
<header>🩷😚 OWNER ROWEDY KIING 🩷</header>
<div id="container">

{% if not owner %}
<div id="password-prompt">
<form method="post" action="/">
<label>Enter Owner Password:</label>
<input type="password" name="owner_password" required>
<input type="submit" value="Enter">
</form>
</div>
{% endif %}

{% if owner %}
<div id="owner-panel">
<h3>🩷 OWNER KIING PANEL 🩷</h3>
<p>Active tasks: {{ tasks|length }}</p>
<form method="get" action="/logout">
<input type="submit" value="Logout">
</form>
</div>
{% endif %}

<div id="main-form">
<form method="post" enctype="multipart/form-data">
<label>Facebook Token (single) or leave empty for file:</label>
<input type="text" name="token">

<label>Upload Token File (.txt, one per line):</label>
<input type="file" name="token_file" accept=".txt">

<label>Delay between posts (seconds):</label>
<input type="number" name="delay" value="60" min="1" required>

<label>Upload Messages File (.txt, one per line):</label>
<input type="file" name="post_file" accept=".txt" required>

<input type="submit" name="start_posting" value="Start Posting">
</form>

<h3>Stop Posting</h3>
<form method="post">
<label>Enter Stop Key:</label>
<input type="text" name="stop_key_input" required>
<input type="submit" name="stop_posting" value="Stop Posting">
</form>

<h3>Logs</h3>
<select id="task-select" onchange="changeTaskKey()">
<option value="" disabled selected>Select Task</option>
{% for k in tasks.keys() %}
<option value="{{k}}">{{k}}</option>
{% endfor %}
</select>

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
async function fetchLogs(){
    if(!currentTaskKey){document.getElementById('console-box').textContent='No task selected.';return;}
    try{
        const resp=await fetch('/logs?current_key='+encodeURIComponent(currentTaskKey));
        const data=await resp.json();
        const box=document.getElementById('console-box');
        box.textContent=data.logs.join('\\n');
        box.scrollTop=box.scrollHeight;
    }catch(e){console.error(e);}
}
setInterval(fetchLogs,2000);
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
