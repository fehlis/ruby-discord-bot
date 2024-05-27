import asyncio
import datetime
import discord
from discord.ext import commands
import discord.ext.commands
import achievement_parser as aparser
import os

import discord.ext

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = 'current-achievement-hunt'
GUILD_ID = 1242214818883178638  # get this from your server

CACHE_TIMEOUT_SECONDS = 60
POLL_EXOPHASE_INTERVAL_SECONDS = 60 * 2 # 2 minutes

authorized_users = [ 500063988269449216 ]

# TODO List:
# - make the bot periodically check for changes:
#   - cache last dict to disk
#   - check for new achievements periodically
#   - if changes are detected, trigger /update to update pinned post
#   - OPTIONAL: post a message to the channel that an update was done
# - post a message to the channel when a game is finished
# - Implement simple caching to prevent excessive server polling
#   - remember "last update time"
#   - if query would be made within too short period, return cached data instead

intents = discord.Intents.default()
#intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='/')

@bot.event
async def on_ready():
    bot.last_update_message = ""
    bot.last_update = datetime.datetime.fromtimestamp(0)
    bot.last_completion_check = datetime.datetime.fromtimestamp(0)
    bot.cached_ruby_games = []
    
    print('Logged on as', bot.user)
    guild = bot.get_guild(GUILD_ID)
    if guild:
        # Find the channel by name
        bot.channel = discord.utils.get(guild.channels, name=CHANNEL_NAME)
        if bot.channel:
            # Print the channel ID
            print(f'Channel ID for {CHANNEL_NAME}: {bot.channel.id}')
            
    # check for a pinned message to use it for indicator for our last update
    pinned_messages = await bot.channel.pins()
    if pinned_messages:
        # Assume we want to edit the first pinned message
        pinned_message = pinned_messages[0]
        #TODO: might have to use created_at in case the pinned message was never edited
        #pinned_message.created_at
        bot.last_update_message = pinned_message.content
        bot.last_update = pinned_message.edited_at
        bot.last_completion_check = pinned_message.edited_at
                        
    bot.loop = asyncio.get_event_loop()
    bot.loop.create_task(periodic_update())                

@bot.event
async def on_message(message):
    # don't react to our own messages
    if message.author == bot.user:
        return
    print("The message's content was", message.content)
    await bot.process_commands(message)

@bot.command()
async def post(ctx, message=None):
    if not ctx.author.id in authorized_users :
        await ctx.send("You're not authorized to use this command.")
        return     
    ruby_games = update_games_cached()
    postmsg = aparser.generate_message(ruby_games)
    await bot.channel.send(postmsg)
    print(f'posted message')
    await ctx.channel.send('posted!')

@bot.command()
async def update(ctx, message=None):
    if ctx and ctx.author.id not in authorized_users :
        await ctx.send("You're not authorized to use this command.")
        return     
    ruby_games = update_games_cached()
    postmsg = aparser.generate_message(ruby_games)
    if postmsg.rstrip() == bot.last_update_message:
        print('no update needed.')
        if ctx:
            await ctx.send('no update needed.') 
        return
    
    bot.last_update_message = postmsg.rstrip()

    # Retrieve the list of pinned messages
    pinned_messages = await bot.channel.pins()
    if pinned_messages:
        # Assume we want to edit the first pinned message
        message_to_edit = pinned_messages[0]
        # Edit the message content
        await message_to_edit.edit(content=postmsg)
        print(f'Edited pinned message: {message_to_edit.id}')
        if ctx:
            await ctx.send('Updated!')                

async def periodic_update():
    while True:
        print("polling exophase for changes...")
        # TODO: figure out how to call update command from here
        command = bot.get_command('update')
        await command(None)
        #bot.get_command("/update")
        await asyncio.sleep(POLL_EXOPHASE_INTERVAL_SECONDS)

def update_games_cached() -> list: 
    now = datetime.datetime.now(datetime.UTC)
    if len(bot.cached_ruby_games) == 0 or abs(now - bot.last_update).total_seconds() > CACHE_TIMEOUT_SECONDS:
        bot.cached_ruby_games = aparser.parse_exophase()
        completed_games = aparser.get_completed(bot.cached_ruby_games, bot.last_completion_check)
        bot.last_update = now
    else:
        print("using cached results")
    return bot.cached_ruby_games

""" def check_for_new_games():
    now = datetime.datetime.now(datetime.UTC)
    ruby_games = update_games_cached()
    
    # Filter the list to include only items not older than 5 days
    recent_games = [item for item in games if item["last_played"] >= ]
 """    

bot.run(TOKEN)