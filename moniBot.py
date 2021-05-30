import discord
from decouple import config
from datetime import date
from pathlib import Path

class AlertBot(discord.Client):

	async def on_ready(self):
		await self.change_presence(status=discord.Status.invisible)
	
		self.guild = discord.utils.get(self.guilds, name='Monitoria Prog 2')

		monitor_role = [role for role in self.guild.roles if role.name == 'Monitor'][0] 
		self.monitores = monitor_role.members
		self.monitores.sort (key = lambda x: x.nick)
		
		print(f'Logged in as {self.user}')
		
	
	async def on_voice_state_update(self, member, before, after):
		if member not in self.monitores and after.channel and after.channel.guild == self.guild and before.channel != after.channel:
			print(f'{member} joined {after.channel}')
			await self.monitores[1].send(f'{member} joined {after.channel}')

			
	async def on_message(self, message):
		matriculas_path = Path().joinpath('matriculas', f'{date.today().strftime("%d-%m-%y")}.txt')
		if message.channel.type == discord.ChannelType.text and message.author == self.monitores[1] and message.channel.name == 'matriculas':
		
			with matriculas_path.open('a+') as file:
				file.write(message.content + '\n')

			await message.add_reaction('👌')


if __name__ == '__main__':
	intents = discord.Intents.default()  
	intents.members = True

	client = AlertBot(intents=intents)
					
	client.run(config('BOT_TOKEN'))

