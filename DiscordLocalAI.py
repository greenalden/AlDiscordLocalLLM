import discord
from datetime import datetime
import re
from discord.ext import commands
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
import os
import logging

DiscordBotToken = "" # Your Discord Bot Token Here
LLM_dir = r""  # Your model path
# Bot configuration
NAME = "" # Name of the bot
MAX_HISTORY_TURNS = 10  # Limit conversation history to this many turns (adjust based on your needs)
RESPONSE_TIMEOUT = 240  # Timeout for response generation in seconds




# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("bot_log.txt"), logging.StreamHandler()])
logger = logging.getLogger("TetraBot")



# Model paths
current_dir = os.path.dirname(__file__)

# Load the tokenizer
logger.info(f"Loading tokenizer from {LLM_dir}")
try:
    tokenizer = AutoTokenizer.from_pretrained(LLM_dir)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
except Exception as e:
    logger.error(f"Failed to load tokenizer: {e}")
    raise

# Load the model
logger.info(f"Loading model from {LLM_dir}")
try:
    model = AutoModelForCausalLM.from_pretrained(
        LLM_dir,
        torch_dtype=torch.float32,
        load_in_4bit=False,
        device_map="auto"
    )
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

# Initialize conversation history - using a dict to track per-channel histories
conversation_histories = {}

class StopOnTokens(StoppingCriteria):
    def __init__(self, stop_token_ids):
        self.stop_token_ids = stop_token_ids

    def __call__(self, input_ids, scores, **kwargs):
        for stop_ids in self.stop_token_ids:
            if torch.all(input_ids[0][-len(stop_ids):] == torch.tensor(stop_ids, device=input_ids.device)):
                return True
        return False

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
    
    # Tokenize with a reasonable max length
    # 4096 is a common context window size, adjust as needed for your model
    try:
        inputs = tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True, max_length=4096)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    except Exception as e:
        logger.error(f"Tokenization error: {e}")
        return "Sorry, I encountered an error processing your message."
    
    # Set up stopping criteria
    stop_token_ids = [
        tokenizer.encode("Human:", add_special_tokens=False),
        tokenizer.encode("Friend:", add_special_tokens=False)
    ]
    stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)])
    
    # Generate response
    try:
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=500,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                bos_token_id=tokenizer.bos_token_id,
                stopping_criteria=stopping_criteria,
            )
        
        # Decode the response
        response = tokenizer.decode(outputs[0, inputs['input_ids'].shape[-1]:], skip_special_tokens=True).strip()
        
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