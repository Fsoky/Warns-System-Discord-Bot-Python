import disnake
from disnake.ext import commands

from motor.motor_asyncio import AsyncIOMotorClient


class WarnsSystem(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.cluster = AsyncIOMotorClient("LINK")
		self.collusers = self.cluster.DATABASE_NAME.COLLECTION_NAME
		self.collservers = self.cluster.DATABASE_NAME.COLLECTION_NAME

	@commands.command(name="warn")
	async def give_warn(self, ctx, member: disnake.Member, *, reason="Вы нарушили правила"):
		if await self.collusers.find_one({"member_id": member.id, "guild_id": ctx.guild.id})["warns"] >= 3:
			await self.collusers.update_one(
				{
					"member_id": member.id,
					"guild_id": ctx.guild.id
				},
				{
					"$set": {
						"warns": 0,
						"reasons": []
					}
				}
			)

			role = disnake.utils.get(ctx.guild.roles, id=12345) # Pass role id here.
			await member.add_roles(role)
		else:
			await self.collservers.update_one(
				{
					"guild_id": ctx.guild.id
				},
				{
					"$inc": {
						"case": 1
					}
				}
			)
			await self.collusers.update_one(
				{
					"member_id": member.id,
					"guild_id": ctx.guild.id
				},
				{
					"$inc":	{
						"warns": 1
					},
					"$push": {
						"reasons": {
							"author_id": ctx.author.id,
							"case": await self.collservers.find_one({"guild_id": ctx.guild.id})["case"],
							"reason": reason
						}
					}
				}
			)

			await ctx.send(f"{ctx.author} выдал предупреждение {member} | Случай: {await self.collservers.find_one({'guild_id': ctx.guild.id}['case'])}")

	@commands.command(name="remwarn")
	async def remove_warn(self, ctx, case: int):
		values = {"reasons.case": case, "guild_id": ctx.guild.id}

		if await self.collusers.count_documents(values) == 0:
			await ctx.send("Такого случая не существует")
		else:
			await self.collusers.update_one(values,
				{
					"$inc": {
						"warns": -1
					},
					"$pull": {
						"reasons": {
							"case": case
						}
					}
				}
			)

		await ctx.message.add_reaction("💖")

	@commands.command(name="view")
	async def view_warns(self, ctx, member: disnake.Member=None):
		values = {"member_id": ctx.author.id, "guild_id": ctx.guild.id}
		if member is not None:
			values["member_id"] = member.id

		embed = disnake.Embed(title="Warns")
		usr = await self.collusers.find_one(values)

		for value in usr["reasons"]:
			embed.add_field(
				name=f"Author: {self.bot.get_user(value['author_id'])}",
				value=f"Case: {value['case']}\nReason: {value['reason']}",
				inline=False
			)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(WarnsSystem(bot))
