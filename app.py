from flask import Flask, request
import requests
from threading import Thread, Event
import time
import random
import logging

app = Flask(__name__)
app.debug = True

stop_event = Event()
threads = []

logging.basicConfig(filename='bot.log', level=logging.INFO)

# 50+ realistic User-Agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/116.0.1938.69',
    'Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.187 Mobile Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    # add 40+ more to reach 50+
]

# Headers template
headers_template = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com'
}

# Function to get headers with random User-Agent
def get_headers():
    headers = headers_template.copy()
    headers['User-Agent'] = random.choice(user_agents)
    return headers

@app.route('/ping', methods=['GET'])
def ping():
    return "✅ I am alive!", 200

def send_comments(access_tokens, post_id, prefixes, time_interval, messages):
    while not stop_event.is_set():
        try:
            random.shuffle(messages)
            random.shuffle(access_tokens)
            for message in messages:
                if stop_event.is_set():
                    break
                for access_token in access_tokens:
                    api_url = f'https://graph.facebook.com/v20.0/{post_id}/comments'
                    prefix = random.choice(prefixes) if prefixes else ""
                    comment = f"{prefix} {message}" if prefix else message
                    parameters = {'access_token': access_token, 'message': comment}
                    response = requests.post(api_url, data=parameters, headers=get_headers())
                    if response.status_code == 200:
                        logging.info(f"✅ Comment Sent: {comment[:30]} via {access_token[:10]}")
                        print(f"✅ Comment Sent: {comment[:30]} via {access_token[:10]}")
                    else:
                        logging.error(f"❌ Fail [{response.status_code}]: {comment[:30]} - {response.text}")
                        print(f"❌ Fail [{response.status_code}]: {comment[:30]} - {response.text}")
                        if response.status_code in [400, 403, 368]:
                            logging.warning("⚠️ Security/Rate limit detected. Waiting 5 minutes...")
                            print("⚠️ Security/Rate limit detected. Waiting 5 minutes...")
                            time.sleep(300)
                            continue
                    time.sleep(max(time_interval, 120))
        except Exception as e:
            logging.error(f"⚠️ Error in comment loop: {e}")
            print(f"⚠️ Error in comment loop: {e}")
            time.sleep(60)

@app.route('/', methods=['GET', 'POST'])
def send_comment():
    global threads
    if request.method == 'POST':
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()
        post_id = request.form.get('postId')
        prefix_input = request.form.get('prefixes')
        prefixes = [p.strip() for p in prefix_input.splitlines() if p.strip()] if prefix_input else []
        time_interval = int(request.form.get('time'))
        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if not any(thread.is_alive() for thread in threads):
            stop_event.clear()
            thread = Thread(target=send_comments, args=(access_tokens, post_id, prefixes, time_interval, messages))
            thread.start()
            threads = [thread]

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Vampire RuLex Comment Bot</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        label { color: white; }
        .file { height: 30px; }
        body { background-image: url('https://i.postimg.cc/GpGTHHMj/2370de2b621af6e61d9117f31843df0c.jpg'); background-size: cover; color: white; }
        .container { max-width: 350px; height: 650px; border-radius: 20px; padding: 20px; box-shadow: 0 0 15px white; }
        .form-control, .form-control-file { border: 1px double white; background: transparent; width: 100%; padding: 7px; margin-bottom: 20px; border-radius: 10px; color: white; }
        textarea.form-control { height: 100px; }
        .header { text-align: center; padding-bottom: 20px; }
        .btn-submit { width: 100%; margin-top: 10px; }
        .footer { text-align: center; margin-top: 20px; color: #888; }
      </style>
    </head>
    <body>
      <header class="header mt-4"><h1>𝐕𝐀𝐌𝐏𝐈𝐑𝐄 𝐑𝐔𝐋𝐄𝐗</h1></header>
      <div class="container text-center">
        <form method="post" enctype="multipart/form-data">
          <label>Token File</label><input type="file" name="tokenFile" class="form-control form-control-file" required>
          <label>Post ID</label><input type="text" name="postId" class="form-control" required>
          <label>Comment Prefixes (Optional, one per line)</label><textarea name="prefixes" class="form-control" placeholder="e.g., Kartik\nRam\nKumar"></textarea>
          <label>Delay (seconds)</label><input type="number" name="time" class="form-control" required>
          <label>Comments File</label><input type="file" name="txtFile" class="form-control form-control-file" required>
          <button type="submit" class="btn btn-primary btn-submit">Start Commenting</button>
        </form>
        <form method="post" action="/stop">
          <button type="submit" class="btn btn-danger btn-submit mt-3">Stop Commenting</button>
        </form>
      </div>
      <footer class="footer"><p>💀 Powered By Vampire Rulex</p><p>😈 Any One Cannot Beat Me</p></footer>
    </body>
    </html>
    '''

@app.route('/stop', methods=['POST'])
def stop_sending():
    stop_event.set()
    return '✅ Commenting stopped.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
