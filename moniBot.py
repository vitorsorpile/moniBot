import discord
from discord.ext.commands import command
from decouple import config
from datetime import date
from pathlib import Path

class User():
	def __init__(self, discordUser = None, whereToSendAlerts = None):
		self.discordUser = discordUser
		self.whereToSendAlerts = whereToSendAlerts

	def __eq__(self, o: object):
		if type(o) == User:
			return self.discordUser.id == o.discordUser.id
		
		return self.discordUser.id == o

	def __hash__(self):
		return hash(self.discordUser.id)


class MoniBot(discord.Client):
	async def on_ready(self):
		self.guildsWatched = {}
		print(f'Logged in as {self.user}')
		
	
	async def on_voice_state_update(self, member, before, after):
		if after.channel and after.channel.guild.id in self.guildsWatched.keys():
			guild = after.channel.guild
			for guild in self.guildsWatched:
				if member in self.guildsWatched[guild]:
					return
		
			if before.channel != after.channel:
				print(f'{member} joined {after.channel}')
				for user in self.guildsWatched[after.channel.guild.id]:
					await user.whereToSendAlerts.send(f'{member} entrou no canal {after.channel}.')
	
	async def on_message(self, message):
		if(message.author.bot): 
			return

		#COMMAND -> !start
		if message.content.startswith(('!start', '!iniciar')):
			guild = message.guild.id
			user = None
			# whereToSendAlerts = None
			if message.raw_channel_mentions:
				channel = message.guild.get_channel(message.raw_channel_mentions[0])
				user = User(message.author, channel)
			else:
				user = User(message.author, message.author)

			if guild not in self.guildsWatched.keys():
				self.guildsWatched[guild] = set([user])
			
			elif user in self.guildsWatched[guild]:
				self.guildsWatched[guild].remove(message.author.id)

			self.guildsWatched[guild].add(user)

			print(f'Now watching {message.guild.name} for {message.author}')
			await user.whereToSendAlerts.send(f'Observando servidor {message.guild.name} para você!')
			await message.add_reaction('🤝') 
			return

		#COMMAND -> !stop
		if message.content.startswith(('!stop', '!encerrar')):
			guild = message.guild.id
			if guild in self.guildsWatched.keys():
				if message.author.id in self.guildsWatched[guild]:
					if len(self.guildsWatched[guild]) == 1:
						self.guildsWatched.pop(guild)
					else:
						self.guildsWatched[guild].remove(message.author.id)
					
					print(f'Stopped watching {message.guild.name} for {message.author}')
					await message.author.send(f'Parei de observar o servidor {message.guild.name} para você!')
					await message.add_reaction('👋')
			return

		 # matriculas_path = Path().joinpath('matriculas', f'{date.today().strftime("%d-%m-%y")}.txt')
		# if message.channel.type == discord.ChannelType.text and message.author == self.monitores[1] and message.channel.name == 'matriculas':
		
		# 	with matriculas_path.open('a+') as file:
		# 		file.write(message.content + '\n')

		# 	await message.add_reaction('👌')


if __name__ == '__main__':
	intents = discord.Intents.default()  
	intents.members = True

	client = MoniBot(intents=intents)
					
	client.run(config('BOT_TOKEN'))
