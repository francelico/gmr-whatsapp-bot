# gmr-whatsapp-bot
Low effort bot to remind your friends (and yourself) to submit a turn in civ games played asynchronously. The bot periodically scraps data from a specified game page on http://multiplayerrobot.com/ and will send reminders to a whatsapp group chat.

Install with
```bash
pip install -r requirements.txt
```

Run with
```bash
python main.py --whatsapp_group_id <group_id> --gmr_game_url <url> --remind_hours <hours>
```

I might integrate the ChatGPT API in at some point to make the messages more interesting, maybe.