import discord
from decouple import config
from datetime import date
from pathlib import Path

class MoniBot(discord.Client):

	async def on_ready(self):
		self.guildsWatched = {}
		await self.change_presence(status=discord.Status.invisible)	
		print(f'Logged in as {self.user}')
		
	
	async def on_voice_state_update(self, member, before, after):
		if after.channel and after.channel.guild.id in self.guildsWatched.keys():
			guild = after.channel.guild
			for guild in self.guildsWatched:
				if member in self.guildsWatched[guild]:
					return
			
			if before.channel != after.channel:
				print(f'{member} joined {after.channel}')
				for monitor in self.guildsWatched[after.channel.guild.id]:
					await monitor.send(f'{member} entrou no canal {after.channel}.')


	async def on_message(self, message):
		if message.content.startswith('!start'):
			guild = message.guild.id
			if guild not in self.guildsWatched.keys():
				self.guildsWatched[guild] = [message.author]
			else:
				self.guildsWatched[guild].append(message.author)
			
			print(f'Now watching {message.guild.name} for {message.author}')
			await message.author.send(f'Observando servidor {message.guild.name} para você!')
			return
			
		if message.content.startswith('!stop'):
			guild = message.guild.id
			if guild in self.guildsWatched.keys():
				if message.author in self.guildsWatched[guild]:
					if len(self.guildsWatched[guild]) == 1:
						self.guildsWatched.pop(guild)
					else:
						self.guildsWatched[guild].remove(message.author)
						
					await message.author.send(f'Parei de observar o servidor {message.guild.name} para você!')
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
