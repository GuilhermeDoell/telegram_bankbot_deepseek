# Telegram Banking Bot

A Telegram bot that simulates basic banking operations with MongoDB data persistence.

## Features

### Check Balance
- Shows current account balance
- Displays last transaction details (type, amount, and timestamp)
- Accessible via inline button in the main menu
- After showing the balance, presents inline options for “Deposit” and “Withdraw”, allowing you to quickly proceed with your desired action

### Deposit
- Implements a multi-step deposit process.
- Validates that the deposit amount is a positive integer.
- Guides you to select an existing payment method or add a new one using an inline keyboard.
- Includes a final confirmation step before processing the deposit.
- Updates your account balance and transaction history upon completion.

### Withdraw 
- Implements a multi-step withdrawal process.
- Validates that the withdrawal amount is positive and does not exceed your current balance.
- Allows you to select or add a new payment method via an inline keyboard.
- Provides a final confirmation step before processing the withdrawal.
- Updates your account balance and transaction history upon successful withdrawal.

## Requirements

- Python 3.8+
- MongoDB 4.0+
- Required Python packages:
certifi==2025.1.31
charset-normalizer==3.4.1
dnspython==2.7.0
environs==14.1.1
idna==3.10
marshmallow==3.26.1
packaging==24.2
pymongo==4.11.1
pyTelegramBotAPI==4.26.0
python-dotenv==1.0.1
requests==2.32.3
typing_extensions==4.12.2
urllib3==2.3.0

## Installation
1. Clone the repository:
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration
1. Create a `.env` file in the root directory with the following variables:
2. Add your Telegram bot token:

```bash
BOT_TOKEN = "your_bot_token_here"
```

## Database Setup
1. Install MongoDB
2. Start MongoDB service
3. The bot will automatically create required collections:
- users: Stores user balances and information
- transactions: Stores transaction history

## Running the Bot
1. Ensure MongoDB is running
2. Start the bot:

```bash
python main.py
```

## Usage
1. Start a chat with your bot on Telegram
2. Send /start to get the main menu
3. Use the inline buttons to:
- Check your balance
- Make deposits
- Make withdrawals