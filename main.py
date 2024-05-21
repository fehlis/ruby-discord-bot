import discord
import achievement_parser as aparser
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = 'current-achievement-hunt'
GUILD_ID = 1242214818883178638  # get this from your server

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        guild = self.get_guild(GUILD_ID)
        if guild:
            # Find the channel by name
            self.channel = discord.utils.get(guild.channels, name=CHANNEL_NAME)
            if self.channel:
                # Print the channel ID
                print(f'Channel ID for {CHANNEL_NAME}: {self.channel.id}')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == '/post':
            ruby_games = aparser.parse_exophase()
            postmsg = aparser.generate_message(ruby_games)
            await self.channel.send(postmsg)
            print(f'posted message')
            await message.channel.send('posted!')

        elif message.content == '/update':
            ruby_games = aparser.parse_exophase()
            postmsg = aparser.generate_message(ruby_games)
            
            # Retrieve the list of pinned messages
            pinned_messages = await self.channel.pins()
            if pinned_messages:
                # Assume we want to edit the first pinned message
                message_to_edit = pinned_messages[0]
                # Edit the message content
                await message_to_edit.edit(content=postmsg)
                print(f'Edited pinned message: {message_to_edit.id}')
                await message.channel.send('Updated!')
            
intents = discord.Intents.default()
#intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)
