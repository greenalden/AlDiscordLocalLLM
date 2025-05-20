# Discord Local AI Chatbot

A Discord chatbot powered by a local Large Language Model (LLM), specifically designed to work with Google's Gemma-3-4b-it.

## Features

- Run a local AI assistant through Discord
- Supports multiple concurrent conversations
- Maintains conversation history for context
- Shows typing indicator while processing responses
- Optimized to run on CPU for accessibility
- Ideal for direct messages (DMs)

## Prerequisites

- A Discord bot token (see [Discord Developer Portal](https://discord.com/developers/applications))
- Access to [Google's Gemma-3-4b-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf)

## Setup Instructions

### 1. Obtain Model Access

1. Request access to Google's Gemma-3-4b-it-qat-q4_0-gguf on [Hugging Face](https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf)
2. Clone or download the model to your local machine

### 2. Configure the Bot

Edit `DiscordLocalAI.py` and update the following variables:

```python
DiscordBotToken = ""  # Your Discord Bot Token Here
LLM_dir = r""         # Path to the Gemma model directory
NAME = ""             # Name for your bot
```

### 3. Installation

1. Run `Setup.bat` to install Python and required dependencies
2. Once setup is complete, run `Run.bat` to start the bot

## Usage

After starting the bot, it will automatically respond to any messages sent to it in Discord. The bot maintains conversation history for each channel to provide contextual responses.

## Customization

You can modify these parameters in `DiscordLocalAI.py` to adjust the bot's behavior:

- `MAX_HISTORY_TURNS`: Controls how many conversation turns to remember (default: 10)
- `RESPONSE_TIMEOUT`: Maximum time in seconds allowed for response generation (default: 240)
- Model generation parameters (temperature, top_p, etc.) can be tuned in the `generate_response` function

## Troubleshooting

- Check `bot_log.txt` for error messages and debugging information
- Ensure your Discord bot has the necessary permissions in your server
- Verify that the model path is correct and accessible

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

This software is provided "as is", without warranty of any kind. Use at your own risk.
