import discord
from datetime import datetime
import re
from discord.ext import commands
import asyncio
import os
import logging
from llama_cpp import Llama

DiscordBotToken = "" # Your Discord Bot Token Here
LLM_model_path = r""  # Path to GGUF model file gemma-3-4b-it-q4_0.gguf
# Bot configuration
NAME = "" # Name of the bot
MAX_HISTORY_TURNS = 10  # Limit conversation history to this many turns (adjust based on your needs)
RESPONSE_TIMEOUT = 240  # Timeout for response generation in seconds




# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()])
logger = logging.getLogger(NAME+"Bot")

# Load the model with llama.cpp
logger.info(f"Loading model from {LLM_model_path}")
try:
    # Adjust the n_threads to your CPU core count for optimal performance
    model = Llama(
        model_path=LLM_model_path,
        n_ctx=4096,         # Context window size
        n_threads=4,        # CPU threads - adjust based on your machine
        n_gpu_layers=0      # Set to 0 to use CPU only
    )
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

# Initialize conversation history - using a dict to track per-channel histories
conversation_histories = {}

def get_conversation_history(channel_id):
    """Get or create a conversation history for the specific channel"""
    if channel_id not in conversation_histories:
        conversation_histories[channel_id] = []
    return conversation_histories[channel_id]

def clean_response(response, messageAuthor, timestamp=None):
    """Clean up the model's response"""
    print(messageAuthor)

    # Remove any trailing human/friend markers
    response = re.split(r"\bHuman:|\bFriend:", response)[0].strip()
    
    # Remove timestamps
    if timestamp:
        response = response.replace(timestamp, '')
    
    # Remove day/date/time patterns
    response = re.sub(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}:', '', response)
    response = re.sub(r'\b\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}:', '', response)
    
    # Remove extra whitespace
    response = re.sub(r'\s{2,}', ' ', response)
    
    # Remove name prefixes
    response = response.removeprefix(f"{NAME}: ")
    response = response.removeprefix(f"{NAME} ")

    print(response)

    response = response.strip()
    try:
        response = response.removeprefix(messageAuthor + ": ")
    except:
        pass

    try:
        response = response.removeprefix(messageAuthor + "- ")
    except:
        pass

    try:
        response = response.removeprefix(messageAuthor)
    except:
        pass
    response = response.strip()
    
    return response.strip()

def generate_response(prompt, channel_id, messageAuthor):
    """Generate a response using the model with proper history management"""
    # Get the conversation history for this channel
    history = get_conversation_history(channel_id)
    
    # Add the new prompt to history
    history.append({"role": "human", "content": prompt})
    
    # Limit history size if needed
    if len(history) > MAX_HISTORY_TURNS * 2:  # *2 because each turn has human and AI message
        # Keep the most recent conversations
        history = history[-(MAX_HISTORY_TURNS * 2):]
        conversation_histories[channel_id] = history
    
    # Build the prompt with limited history
    full_prompt = f"Below is a conversation between a human and an Friend on Discord. The name of the friend is {NAME}. DO NOT INCLUDE {NAME} DISCORD NAME OR TIME INFORMATION IN THE RESPONSE. \n\n"
    
    for turn in history:
        if turn["role"] == "human":
            full_prompt += f"Human: {turn['content']}\n"
        else:
            full_prompt += f"Friend: {turn['content']}\n"
    
    full_prompt += "Friend:"
    
    # Log the size of the prompt for debugging
    logger.info(f"Prompt length: {len(full_prompt)} chars, {len(full_prompt.split())} words")
    
    try:
        # Generate response using llama.cpp
        output = model(
            full_prompt,
            max_tokens=500,
            stop=["Human:", "Friend:"],
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1
        )
        
        # Extract the generated text
        response = output["choices"][0]["text"].strip()
        
        # Clean up the response
        response = clean_response(response, messageAuthor)
        
        # Add to history
        history.append({"role": "friend", "content": response})
        
        return response
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "I'm having trouble thinking right now. Can you try again?"

async def async_generate_response(prompt, channel_id, messageAuthor):
    """Asynchronous wrapper for response generation with timeout"""
    try:
        # Run the CPU-intensive model inference in a thread with a timeout
        return await asyncio.wait_for(
            asyncio.to_thread(generate_response, prompt, channel_id, messageAuthor),
            timeout=RESPONSE_TIMEOUT
        )
    except asyncio.TimeoutError:
        logger.warning(f"Response generation timed out after {RESPONSE_TIMEOUT} seconds")
        return "I'm still thinking about that. Could you give me a moment and try again?"
    except Exception as e:
        logger.error(f"Error in async_generate_response: {e}")
        return "I encountered an unexpected error. Please try again."

# Set up Discord bot
intents = discord.Intents.all()
intents.messages = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Log incoming messages
    logger.info(f'Message from {message.author} in {message.channel.id}: {message.content}')
    
    # Use typing indicator during processing
    async with message.channel.typing():
        # Add timestamp to the message
        current_time = datetime.now().strftime("%A %m/%d/%Y %H:%M:%S") + ": "
        full_message = str(message.author) + "-" + current_time + message.content
        
        # Generate response
        response = await async_generate_response(full_message, str(message.channel.id), str(message.author))
    
    # Send the response
    logger.info(f"Sending response: {response}")
    await message.channel.send(response)

# Run the bot - store token in environment variable or config file for better security
TOKEN = DiscordBotToken  # Replace with your token or use os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)