# Lotto8888 — @Lotto_8888_BOT

Free English everyday maths utility: percentages, fraction simplification, multiplication tables. User chooses a button, replies with numbers and receives a calculation with a short explanation. No database, saved users, admin panel, broadcasts, external redirects or forced joins.

## Launch

Python 3.12+. Build: `pip install -r requirements.txt`. Start: `python bot.py`.
Set `BOT_TOKEN` as a secret on your host, for @Lotto_8888_BOT. Run only one worker per token. No persistent disk or paid APIs needed. `.env.example` is documentation; this app reads actual environment variables, not .env files.

Startup verifies the token's username and sets the name, bio, pre-Start description and command menu. Profile changes happen only when the worker runs with the correct token. Add an original calculator-themed profile image through @BotFather. The source code alone does not deploy the bot.

Commands: `/start`, `/percent 15 200`, `/fraction 18 24`, `/table 8`, `/help`, `/privacy`. Decimal comma or point allowed for percentages; no thousands separators. Tables and fractions use integers. Input sizes are bounded. Calculations use Decimal/integer arithmetic, never evaluation of user code.

No user records are saved. Chat IDs and inputs are processed transiently to reply; operational logs omit content and tokens. Telegram may retain messages under its policies.

## Advertising and branding

The actual product is a maths calculator. It contains no lottery draws, betting, lucky number generator, predictions, odds, prizes, payments or gambling links. It must remain the same honest service for users and reviewers; never replace it with prohibited content after review.

The requested name Lotto8888 and its username can suggest a lottery. This is a branding ambiguity, not a verified rejection cause. A clear maths-oriented name/username would better describe this service. Adding a disclaimer does not override prohibited functionality or guarantee approval.

Ads and target placements should match this English calculator. Telegram decides approval after reviewing the live destination, profile and creative. Rules: https://ads.telegram.org/guidelines. Terms: https://ads.telegram.org/tos.

## Checks

`python -m unittest discover -s tests -v`

`python -m py_compile bot.py`

Tests cover arithmetic, invalid inputs, interactive flows and profile limits. Live messaging/profile updates require the real token and running host and have not been tested here.
