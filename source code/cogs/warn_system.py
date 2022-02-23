import discord
from discord.ext import commands
from pymongo import MongoClient


class WarnSystem(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.cluster = MongoClient("mongodb+srv://<user>:<password>@cluster0.5hnrh.mongodb.net/warnsdb?retryWrites=true&w=majority")
		self.collusers = self.cluster.warnsdb.collusers
		self.collservers = self.cluster.warnsdb.collservers


	@commands.command(name="warn")
	async def give_warn(self, ctx, member: discord.Member, *, reason="You violated the rules."):
		if self.collusers.find_one({"_id": member.id, "guild_id": ctx.guild.id})["warns"] >= 3:
			self.collusers.update_one(
				{
					"_id": member.id,
					"guild_id": ctx.guild.id
				},
				{
					"$set": {
						"warns": 0,
						"reasons": []
					}
				}
			)

			role = discord.utils.get(ctx.guild.roles, id=839052909714341918)
			await member.add_roles(role)
		else:
			self.collservers.update_one(
				{
					"_id": ctx.guild.id
				},
				{
					"$inc": {
						"case": 1
					}
				}
			)
			self.collusers.update_one(
				{
					"_id": member.id,
					"guild_id": ctx.guild.id
				},
				{
					"$inc": {
						"warns": 1
					},
					"$push": {
						"reasons": {
							"author_id": ctx.author.id,
							"case": self.collservers.find_one({"_id": ctx.guild.id})["case"],
							"reason": reason
						}
					}
				}
			)

			await ctx.send(f"{ctx.author} gave warn to {member} | case: {self.collservers.find_one({'_id': ctx.guild.id})['case']}")


	@commands.command(name="remwarn")
	async def remove_warn(self, ctx, case: int):
		if self.collusers.count_documents({"reasons.case": case, "guild_id": ctx.guild.id}) == 0:
			await ctx.send("This case doesn't exist")
		else:
			self.collusers.update_one(
				{
					"reasons.case": case,
					"guild_id": ctx.guild.id
				},
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

			await ctx.send("Success!")


	@commands.command(name="view")
	async def view_warns(self, ctx, member: discord.Member=None):
		usr = self.collusers.find_one({"_id": ctx.author.id, "guild_id": ctx.guild.id})
		if member is not None:
			usr = self.collusers.find_one({"_id": member.id, "guild_id": ctx.guild.id})

		embed = discord.Embed(title="Warns")
		for value in usr["reasons"]:
			embed.add_field(
				name=f"Author: {self.bot.get_user(value['author_id'])}",
				value=f"Case: {value['case']}\nReason: {value['reason']}",
				inline=False
			)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(WarnSystem(bot))