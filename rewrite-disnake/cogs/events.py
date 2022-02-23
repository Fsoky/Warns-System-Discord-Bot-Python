import disnake
from disnake.ext import commands

from motor.motor_asyncio import AsyncIOClient


class Events(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.cluster = AsyncIOClient("LINK")
		self.collusers = self.cluster.DATABASE_NAME.COLLECTION_NAME
		self.collservers = self.cluster.DATABASE_NAME.COLLECTION_NAME

	@commands.Cog.listener()
	async def on_ready(self):
		for guild in self.bot.guilds:
			for member in guild.members:
				if await self.collusers.count_documents({"member_id": member.id, "guild_id": guild.id}) == 0:
					await self.collusers.insert_one(
						{
							"member_id": member.id,
							"guild_id": guild.id,
							"warns": 0,
							"reasons": []
						}
					)
				if await self.collservers.count_documents({"guild_id": guild.id}) == 0:
					await self.collservers.insert_one(
						{
							"guild_id": guild.id,
							"case": 0
						}
					)

	@commands.Cog.listener()
	async def on_member_join(member):
		if await self.collusers.count_documents({"member_id": member.id, "guild_id": member.guild.id}) == 0:
			await self.collusers.insert_one(
				{
					"member_id": member.id,
					"guild_id": member.guild.id,
					"warns": 0,
					"reasons": []
				}
			)

	@commands.Cog.listener()
	async def on_guild_join(guild):
		if await self.collservers.count_documents({"guild_id": guild.id}) == 0:
			await self.collservers.insert_one(
				{
					"guild_id": guild.id,
					"case": 0
				}
			)


def setup(bot):
	bot.add_cog(Events(bot))