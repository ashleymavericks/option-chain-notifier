
<div align="center">
<h1 align="center">Option Chain Notifier</h1>
<img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"/><br><br>
An Option Chain Notifier service which provide relevant CE option chain data like Time Value, LTP, Strike % down from Nifty current price for current and upcoming weekly expiry. It also provides Alert notifications when Time Value for the ITM strikes go below a threshold amount. 

<br>
</div>

***
## Features
- [x] Notifies with Time Values of ITM strikes of Nifty CE options upto desired % down (default = 4%) from Nifty current price for current & upcoming weekly expiry.
- [x] Notifies with an Alert message when the Time Values for an ITM strike breach the pre-defined threshold amount.
- [ ] Fetch Open positions using Broker API to send relevant alerts, only for that particular strike price.

## Pushbullet Notifications
Currently, using Pushbullet API and Channels to broadcast the notifications, but integration with other platforms like Discord, Telegram is also possible supported.

Subscribe to the [#niftyoptions](https://www.pushbullet.com/channel?tag=niftyoptions) Pushbullet channel for notifications.

[![notion_habit_tracket](/assets/alert_notification_current_expiry.png)](https://www.pushbullet.com/channel?tag=niftyoptions)

## Script Usage
1. Clone the repo
```bash
git clone https://github.com/ashleymavericks/notion-habit-tracker.git
```
2. Create a .env file in the project folder and Add [Pushbullet](https://docs.pushbullet.com/) API key in the .env file
```bash
PUSHBULLET_API_KEY=PASTE_KEY_HERE
```
3. Install project dependencies
```bash
pipenv install
```
4. Run the Python script called `main.py`, it may take some time to complete, depending on Nifty API response
```bash
python3 main.py
```

## Contributing
Feel free to reach out, if you want to further improve the template.

## License
This project is licensed under the MIT license
