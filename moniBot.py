import discord
from discord.ext import commands
from decouple import config
from discord_slash import SlashCommand, SlashContext, cog_ext


DEVELOPING = False


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


   @cog_ext.cog_slash(name='start', 
                     description='Inicia o bot para avisá-lo sempre que alguém se conectar a um canal de voz.',
                     options=[
                        {
                           'name': 'canal',
                           'description': 'Canal de texto em que serão enviados os alertas.',
                           'type':  7,
                           'required': 'false',
                           'channel_types': [0] 
                        }
                     ],
                     # guild_ids=[848213949102424065]
                     )
   async def _start(self, ctx : SlashContext, canal = None):
      '''
         -> Inicia o bot para avisá-lo sempre que alguém se conectar a um canal de voz. Por padrão, os alertas serão
         enviados por mensagem privada, mas pode ser passado um canal de texto no formato !start #canal-de-texto para 
         que os alertas sejam enviados nesse canal.
      '''

      # Check if author has the needed permissions
      ACCEPTED_ROLES = ['monitor', 'monitores']
      authorRoles = [role.name.lower() for role in ctx.author.roles]
      
      if (not any(role in authorRoles for role in ACCEPTED_ROLES)):
         await ctx.send('ERRO: Você nem permissão para executar esse comando.', hidden=True)
         return

      guild = ctx.guild_id
      user = None
      if canal:
         user = User(ctx.author, canal)
      else:
         user = User(ctx.author, ctx.author)

      if guild not in self.bot.guildsWatched.keys():
         self.bot.guildsWatched[guild] = set([user])
      
      elif user in self.bot.guildsWatched[guild]:
         self.bot.guildsWatched[guild].remove(ctx.author.id)

      self.bot.guildsWatched[guild].add(user)

      print(f'Now watching {ctx.guild.name} for {ctx.author}')
      await ctx.send(f'Observando o servidor {ctx.guild.name} para você!', hidden=True)


   @cog_ext.cog_slash(name='stop', 
                     description='O bot para de avisá-lo quando alguém se conectar a um canal de voz.',
                     # guild_ids=[848213949102424065]
                     )
   async def _stop(self, ctx: SlashContext):
      '''
         -> O bot para de avisá-lo quando alguém se conectar a um canal de voz.
      '''

      # Check if author has the needed permissions
      ACCEPTED_ROLES = ['monitor', 'monitores']
      authorRoles = [role.name.lower() for role in ctx.author.roles]
      
      if (not any(role in authorRoles for role in ACCEPTED_ROLES)):
         await ctx.send('ERRO: Você nem permissão para executar esse comando.', hidden=True)
         return

      guild = ctx.guild.id
      if guild in self.bot.guildsWatched.keys():
         if ctx.author.id in self.bot.guildsWatched[guild]:
            if len(self.bot.guildsWatched[guild]) == 1:
               self.bot.guildsWatched.pop(guild)
            else:
               self.bot.guildsWatched[guild].remove(ctx.author.id)
            
            print(f'Stopped watching {ctx.guild.name} for {ctx.author}')
            # await ctx.add_reaction('👋')
            await ctx.send(f'Parei de observar o servidor {ctx.guild.name} para você. 👋', hidden=True)
            return
      
      await ctx.send('Parece que eu não estava observando nenhum servidor para você.', hidden=True)


class MoniBot(commands.Bot):
   async def on_ready(self):
      self.guildsWatched = {}
      if DEVELOPING:
         await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Em manutenção...'), 
                                    status=discord.Status.idle)
      else:
         await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='/start | !help'))
      print(f'Logged in as {self.user}')
      print("------")
      
   async def on_voice_state_update(self, member, before, after):
      if after.channel and not before.channel and after.channel.guild.id in self.guildsWatched.keys():

         ROLES = ['monitor', 'monitores']
         memberRoles = [role.name.lower() for role in member.roles]      
         if (any(role in memberRoles for role in ROLES)):
            return
      
         if before.channel != after.channel:
            print(f'{member} joined {after.channel}')
            for user in self.guildsWatched[after.channel.guild.id]:
               await user.whereToSendAlerts.send(f'{member} entrou no canal {after.channel}.')


if __name__ == '__main__':
   intents = discord.Intents.default()  
   intents.members = True

   bot = MoniBot(intents=intents, command_prefix='!', case_insensitive=True)
   slash = SlashCommand(bot, sync_commands=True, override_type=True)

   bot.add_cog(Alerts(bot))
   

   bot.description = '''
   O Moni Bot foi desenvolvido com o intuito de auxiliar os(as) monitores(as) que fazem seus atendimentos via Discord.
   O código pode ser acessado em: https://github.com/vitorsorpile/moniBot 
   Qualquer dúvida/sugestão por favor entre em contato em vitorsorpile@gmail.com ou pelo Discord Vitor#9289'''

   bot.run(config('BOT_TOKEN'))

# https://discord.com/api/oauth2/authorize?client_id=759093939427999764&permissions=277025582160&scope=applications.commands%20bot