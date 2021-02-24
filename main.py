# bot.py
import os
import json
import requests
import io
import base64

import discord
from discord.ext import commands
from dotenv import load_dotenv

class Database:
  def __init__(self):
    with open("./logos.json", "r") as f:
      self.logos = json.loads(f.read())

  def getEmoji(self, authorID):
    return self.logos[str(authorID)]

  def addEmoji(self, authorID, emojiID):
    with open("./logos.json", "w") as f:
      self.logos[str(authorID)] = emojiID
      f.write(json.dumps(self.logos))

  def emojiExists(self, authorID):
    return str(authorID) in [*self.logos]

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix="!", intents=discord.Intents.default())
db = Database()

foughGuild = None


@client.event
async def on_ready():
  print("Running")

  for guild in client.guilds:
    if guild.name == GUILD:
      foughGuild = guild
  

@client.event
async def on_message(message):
  if len(message.content) > 250 or message.author.bot:
    return
  if message.guild:
    
    if db.emojiExists(message.author.id):
      for emoji in message.guild.emojis:
        if emoji.id == db.getEmoji(message.author.id):
          await message.add_reaction(emoji)

  if message.content.startswith("!crest"):
    try:
      image_formats = ("image/png", "image/jpeg", "image/gif")
      response = requests.get(message.content[7:].strip())

      if response.headers["content-type"] in image_formats:

        response = requests.get(message.content[7:].strip())
        image_bytes = io.BytesIO(response.content).getvalue()

        name = f'{message.author.name}crest'

        if db.emojiExists(message.author.id):
          for emoji in message.guild.emojis:
            if emoji.id == db.getEmoji(message.author.id):
              await emoji.delete()

        emoji = await message.guild.create_custom_emoji(name=name, image=image_bytes)
        db.addEmoji(message.author.id, emoji.id)

        await message.channel.send(f'<@{message.author.id}> Added crest')

      else:
        print("Image error: incorrect content type")
        await message.channel.send(f'<@{message.author.id}> Thats not a valid image URL, please try again')

    except Exception as e:
      print(e)

      if "File cannot be larger than 256.0 kb" in str(e):
        print("Image too big error")
        await message.channel.send(f'<@{message.author.id}> Thats image is too big! The maximum size is 256KB')

      else:
        print("Image response error")
        await message.channel.send(f'<@{message.author.id}> Thats not a valid image URL, please try again')

client.run(TOKEN)