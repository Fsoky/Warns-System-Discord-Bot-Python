import discord
from discord.ext import commands
from pymongo import MongoClient
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
cluster = MongoClient("mongodb+srv://<user>:<password>@cluster0.5hnrh.mongodb.net/warnsdb?retryWrites=true&w=majority")
collusers = cluster.warnsdb.collusers
collservers = cluster.warnsdb.collservers


@bot.event
async def on_ready():
	for guild in bot.guilds:
		for member in guild.members:
			values = {
				"_id": member.id,
				"guild_id": guild.id,
				"warns": 0,
				"reasons": []
			}
			server_values = {
				"_id": guild.id,
				"case": 0
			}

			if collusers.count_documents({"_id": member.id, "guild_id": guild.id}) == 0:
				collusers.insert_one(values)
			if collservers.count_documents({"_id": guild.id}) == 0:
				collservers.insert_one(server_values)


@bot.event
async def on_member_join(member):
	values = {
		"_id": member.id,
		"guild_id": guild.id,
		"warns": 0,
		"reasons": []
	}

	if collusers.count_documents({"_id": member.id, "guild_id": guild.id}) == 0:
		collusers.insert_one(values)


@bot.event
async def on_guild_join(guild):
	server_values = {
		"_id": guild.id,
		"case": 0
	}
	
	if collservers.count_documents({"_id": guild.id}) == 0:
		collservers.insert_one(server_values)


for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")

bot.run("token")