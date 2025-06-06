# Apple TV Keys Telegram Bot

A Telegram bot that automatically generates Apple TV subscription keys and manages them through a simple interface. The bot runs headless browsers in the background to generate keys from the Apple TV redemption service.

## Features

- Automatic key generation using multiple headless browsers
- Telegram bot interface for easy access to keys
- MongoDB database for key storage and management
- Docker support for easy deployment
- Background key generation to maintain stock
- Configurable generation settings

## Commands

- `/start` - Start the bot
- `/help` - Show available commands
- `/getkey` - Get a single Apple TV key
- `/getkeys <count>` - Get multiple keys (max 10)
- `/stock` - Check available keys in stock
- `/generate <count>` - Generate keys in background
- `/startgen` - Start automatic key generation
- `/stopgen` - Stop automatic key generation

## Requirements

- Python 3.9+
- MongoDB
- Chrome/Chromium browser
- Docker and Docker Compose (for containerized deployment)

## Installation

### Using Docker (Recommended for Ubuntu/AWS)

1. Clone the repository:
   ```
   git clone https://github.com/el4abdu/applekeytelegramtv.git
   cd applekeytelegramtv
   ```

2. Start the containers:
   ```
   docker-compose up -d
   ```

3. Check logs:
   ```
   docker logs -f apple_tv_keys_bot
   ```

### Manual Installation (Ubuntu)

1. Clone the repository:
   ```
   git clone https://github.com/el4abdu/applekeytelegramtv.git
   cd applekeytelegramtv
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Chrome:
   ```
   sudo apt-get update
   sudo apt-get install -y wget gnupg
   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

4. Install Xvfb for headless operation:
   ```
   sudo apt-get install -y xvfb
   ```

5. Start Xvfb:
   ```
   Xvfb :99 -screen 0 1280x1024x24 -ac &
   export DISPLAY=:99
   ```

6. Start MongoDB:
   ```
   sudo apt-get install -y mongodb
   sudo systemctl start mongodb
   ```

7. Run the bot:
   ```
   python app.py
   ```

## Configuration

Edit `config.py` to customize settings:

- `TELEGRAM_TOKEN` - Your Telegram bot token
- `MAX_BROWSERS` - Number of concurrent browser instances
- `HEADLESS` - Whether to run browsers in headless mode
- `DEFAULT_KEYS_TO_GENERATE` - Default number of keys to generate
- `KEY_GENERATION_INTERVAL` - Interval for scheduled key generation

## Deployment on AWS

1. Launch an Ubuntu EC2 instance
2. Install Docker and Docker Compose:
   ```
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ubuntu
   ```

3. Clone the repository and start the application:
   ```
   git clone https://github.com/el4abdu/applekeytelegramtv.git
   cd applekeytelegramtv
   docker-compose up -d
   ```

## License

This project is for educational purposes only. Use at your own risk. 