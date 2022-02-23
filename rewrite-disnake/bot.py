import os

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix=".", intents=disnake.Intents.all())


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
	bot.load_extension(f"cogs.{extension}")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
	bot.reload_extension(f"cogs.{extension}")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
	bot.unload_extension(f"cogs.{extension}")


for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("TOKEN")