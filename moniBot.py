import discord
from discord.ext import commands
from decouple import config


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


class Alerts(commands.Cog):
   def __init__(self, bot):
      super().__init__()
      self.bot = bot

   @commands.command(name='start', aliases=['iniciar'])
   @commands.has_any_role('Monitor', 'Monitores')
   async def _start(self, ctx):
      '''
         -> Inicia o bot para avisá-lo sempre que alguém se conectar a um canal de voz. Por padrão, os alertas serão
         enviados por mensagem privada, mas pode ser passado um canal de texto no formato !start #canal-de-texto para 
         que os alertas sejam enviados nesse canal.
      '''
      message = ctx.message
      guild = message.guild.id
      user = None
      if message.raw_channel_mentions:
         channel = message.guild.get_channel(message.raw_channel_mentions[0])
         user = User(message.author, channel)
      else:
         user = User(message.author, message.author)

      if guild not in self.bot.guildsWatched.keys():
         self.bot.guildsWatched[guild] = set([user])
      
      elif user in self.bot.guildsWatched[guild]:
         self.bot.guildsWatched[guild].remove(message.author.id)

      self.bot.guildsWatched[guild].add(user)

      print(f'Now watching {message.guild.name} for {message.author}')
      await message.add_reaction('🤝') 


   @commands.command(name='stop', aliases=['encerrar'])
   @commands.has_any_role('Monitor', 'Monitores')
   async def _stop(self, ctx):
      '''
         -> O bot para de avisá-lo quando alguém se conectar a um canal de voz.
      '''
      message = ctx.message
      guild = message.guild.id
      if guild in self.bot.guildsWatched.keys():
         if message.author.id in self.bot.guildsWatched[guild]:
            if len(self.bot.guildsWatched[guild]) == 1:
               self.bot.guildsWatched.pop(guild)
            else:
               self.bot.guildsWatched[guild].remove(message.author.id)
            
            print(f'Stopped watching {message.guild.name} for {message.author}')
            await message.add_reaction('👋')


class MoniBot(commands.Bot):
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


if __name__ == '__main__':
   intents = discord.Intents.default()  
   intents.members = True
   
   bot = MoniBot(intents=intents, command_prefix='!', case_insensitive=True)
   bot.add_cog(Alerts(bot))

   bot.description = '''
   O Moni Bot foi desenvolvido com o intuito de auxiliar os(as) monitores(as) que fazem seus atendimentos via Discord.
   O código pode ser acessado em: https://github.com/vitorsorpile/moniBot 
   Qualquer dúvida/sugestão por favor entre em contato em vitorsorpile@gmail.com ou pelo Discord Vitor#9289'''

   bot.run(config('BOT_TOKEN'))
