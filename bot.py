"""Lotto8888: free everyday arithmetic; no user database."""
import json
import logging
import math
import os
import re
import signal
import threading
import urllib.error
import urllib.request
from decimal import Decimal

NAME = 'Lotto8888'
USERNAME = 'Lotto_8888_BOT'
BIO = 'Free number tools: calculate percentages, simplify fractions and view multiplication tables.'
DESCRIPTION = 'Lotto8888 provides free everyday maths tools. Calculate a percentage of a number, simplify a fraction or view a multiplication table. Tap Start and choose a tool. No registration or subscription required. This is a calculator, with no lottery draws, betting, predictions or prizes.'
WELCOME = 'Welcome to Lotto8888 — everyday number tools.\n\nChoose a tool below. Each tool includes an example and works directly in this chat. Free to use; no registration required.'
PROMPTS = {
    'percent': 'PERCENTAGE\nEnter a percentage and a number, separated by a space.\nExample: 15 200\nThis calculates 15% of 200.\nUse a decimal point or comma, without thousands separators.',
    'fraction': 'FRACTION\nEnter a numerator and denominator.\nExample: 18 24\nThis simplifies 18/24. The denominator must not be zero.',
    'table': 'TABLE\nEnter a whole number from -10000 to 10000.\nExample: 8\nThis shows its multiplication table from 1 to 12.',
}
HELP = 'Choose a button, then reply with the requested numbers.\n\nDirect commands:\n/percent 15 200\n/fraction 18 24\n/table 8\n/start — menu\n/privacy — data information\n\nThis service only performs arithmetic. It does not provide lottery results, number predictions or prizes.'
PRIVACY = 'This app does not save user records or message history and has no database or admin panel. Chat IDs and inputs are processed transiently to send replies. Operational logs exclude message text and bot tokens. Telegram may retain messages under its own policies. No personal information is needed.'
MENU = [('Percentage calculator', 'percent'), ('Simplify a fraction', 'fraction'), ('Multiplication table', 'table'), ('Examples and help', 'help'), ('Privacy', 'privacy')]


def parse(text, count, integer=False):
    parts = text.split()
    if len(parts) != count:
        raise ValueError(f'Enter exactly {count} number(s), separated by spaces.')
    pattern = r'-?\d{1,9}' if integer else r'-?\d{1,9}(?:[.,]\d{1,6})?'
    if not all(re.fullmatch(pattern, p) for p in parts):
        raise ValueError('Use numbers only, without thousands separators. Fractions and tables require whole numbers.')
    return [int(p) for p in parts] if integer else [Decimal(p.replace(',', '.')) for p in parts]


def fmt(value):
    result = format(value, 'f')
    return result.rstrip('0').rstrip('.') if '.' in result else result


def calculate(tool, text):
    if tool == 'percent':
        percent, base = parse(text, 2)
        answer = percent * base / 100
        return f'{fmt(percent)}% of {fmt(base)} = {fmt(answer)}\n\nMethod: percentage × number ÷ 100.'
    if tool == 'fraction':
        numerator, denominator = parse(text, 2, True)
        if denominator == 0:
            raise ValueError('The denominator cannot be zero.')
        factor = math.gcd(numerator, denominator)
        a, b = numerator // factor, denominator // factor
        if b < 0:
            a, b = -a, -b
        return f'{numerator}/{denominator} = {a}/{b}\n\nDivide both terms by their greatest common divisor: {factor}. The denominator is shown positive.'
    if tool == 'table':
        number, = parse(text, 1, True)
        if abs(number) > 10000:
            raise ValueError('Choose a whole number between -10000 and 10000.')
        return f'Multiplication table for {number}\n\n' + '\n'.join(f'{number} × {i} = {number*i}' for i in range(1, 13))
    raise ValueError('Choose a tool from /start.')


class Bot:
    def __init__(self, token):
        self.token = token
    def api(self, method, **params):
        request = urllib.request.Request(f'https://api.telegram.org/bot{self.token}/{method}', data=json.dumps(params).encode(), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f'Telegram {method} HTTP {exc.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError(f'Telegram {method} network failure') from None
        if not result.get('ok'):
            raise RuntimeError(f'Telegram {method} failed')
        return result['result']

    def configure(self):
        me = self.api('getMe')
        if me.get('username', '').lower() != USERNAME.lower():
            raise RuntimeError('BOT_TOKEN must belong to @Lotto_8888_BOT')
        self.api('setMyName', name=NAME)
        for language in ('', 'en'):
            self.api('setMyShortDescription', short_description=BIO, language_code=language)
            self.api('setMyDescription', description=DESCRIPTION, language_code=language)
            self.api('setMyCommands', language_code=language, commands=[{'command': c, 'description': d} for c, d in [('start', 'Open tools'), ('percent', 'Calculate a percentage'), ('fraction', 'Simplify a fraction'), ('table', 'Multiplication table'), ('help', 'Examples and help'), ('privacy', 'Privacy information')]])

    def send(self, chat, text, prompt=False):
        keyboard = {'inline_keyboard': [[{'text': label, 'callback_data': data}] for label, data in MENU]}
        self.api('sendMessage', chat_id=chat, text=text, reply_markup={'force_reply': True, 'input_field_placeholder': 'Enter numbers as shown above'} if prompt else keyboard)

    def handle(self, update):
        callback = update.get('callback_query')
        message = callback.get('message', {}) if callback else update.get('message', {})
        if message.get('chat', {}).get('type') != 'private':
            return
        chat = message['chat']['id']
        if callback:
            self.api('answerCallbackQuery', callback_query_id=callback['id'])
            data = callback.get('data', '')
            if data in PROMPTS:
                self.send(chat, PROMPTS[data], True)
            else:
                self.send(chat, HELP if data == 'help' else PRIVACY if data == 'privacy' else WELCOME)
            return
        text = message.get('text', '').strip()
        if not text:
            self.send(chat, 'Please use text numbers or choose a tool below. Photos and documents are not needed.'); return
        parts = text.split(maxsplit=1)
        command = parts[0].split('@')[0].lower()
        arguments = parts[1] if len(parts) > 1 else ''
        if command in ('/start', '/help', '/privacy'):
            self.send(chat, {'/start': WELCOME, '/help': HELP, '/privacy': PRIVACY}[command]); return
        tool = command.removeprefix('/')
        if tool in PROMPTS and command.startswith('/'):
            if not arguments:
                self.send(chat, PROMPTS[tool], True); return
        else:
            prompt = message.get('reply_to_message', {}).get('text', '')
            tool = next((key for key, value in PROMPTS.items() if prompt.startswith(value.split('\n')[0] + '\n')), None)
            arguments = text
            if not tool:
                self.send(chat, 'Choose a tool below, or use /percent 15 200, /fraction 18 24 or /table 8.'); return
        try:
            self.send(chat, calculate(tool, arguments))
        except ValueError as exc:
            self.send(chat, str(exc) + '\n\n' + PROMPTS[tool], True)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    token = os.environ.get('BOT_TOKEN', '').strip()
    if not token:
        raise SystemExit('Set BOT_TOKEN in hosting environment. Never commit it.')
    bot = Bot(token)
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    bot.configure()
    bot.api('deleteWebhook', drop_pending_updates=False)
    logging.info('Profile configured; polling started')
    offset = 0
    while not stop.is_set():
        try:
            updates = bot.api('getUpdates', offset=offset, timeout=25, allowed_updates=['message', 'callback_query'])
            for update in updates:
                if stop.is_set():
                    break
                try:
                    bot.handle(update)
                except Exception:
                    logging.error('Update failed; user can retry with /start')
                offset = update['update_id'] + 1
        except RuntimeError:
            logging.warning('Polling unavailable; retrying')
            stop.wait(5)
    logging.info('Worker stopped')


if __name__ == '__main__':
    main()
