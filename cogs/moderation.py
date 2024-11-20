import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(help = "Kick members")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')

    @commands.command(help = "Ban members")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'{member.mention} has been banned.')

    @commands.command(help = "Unban members")
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, member: discord.User):
        try:
            await ctx.guild.unban(member)
            await ctx.send(f'{member.mention} has been unbanned.')
        except discord.NotFound:
            await ctx.send("User not found in the ban list.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to unban this user.")
        except discord.HTTPException:
            await ctx.send("Failed to unban the user.")

    @commands.command(help= "Adds a role to a user - example - !add_role @userName Role")
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, user: discord.Member, *, role_name: str):
        """Add a role to a user"""
        try:
            # Try to find the role by name
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            
            # If role wasn't found, check if it's an ID or mention
            if not role:
                try:
                    # Remove <@& and > from role mention or try to use as ID
                    role_id = role_name.strip('<@&>')
                    role = discord.utils.get(ctx.guild.roles, id=int(role_id))
                except ValueError:
                    pass

            if not role:
                await ctx.send(f"Could not find role: {role_name}")
                return

            # Check bot's role hierarchy
            if ctx.guild.me.top_role <= role:
                await ctx.send("I don't have permission to assign this role (my highest role must be above the role you're trying to assign).")
                return

            # Check user's role hierarchy
            if ctx.author.top_role <= role and ctx.author.id != ctx.guild.owner_id:
                await ctx.send("You can't assign a role that is higher than or equal to your highest role.")
                return

            if role in user.roles:
                await ctx.send(f'{user.mention} already has the role {role.name}')
                return

            await user.add_roles(role)
            await ctx.send(f'Added role {role.name} to {user.mention}')

        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while adding the role: {str(e)}")

    @commands.command(help= "Removes a role from a user - example - !remove_role @userName Role")
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, user: discord.Member, *, role_name: str):
        """Remove a role from a user"""
        try:
            # Try to find the role by name
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            
            # If role wasn't found, check if it's an ID or mention
            if not role:
                try:
                    # Remove <@& and > from role mention or try to use as ID
                    role_id = role_name.strip('<@&>')
                    role = discord.utils.get(ctx.guild.roles, id=int(role_id))
                except ValueError:
                    pass

            if not role:
                await ctx.send(f"Could not find role: {role_name}")
                return

            # Check bot's role hierarchy
            if ctx.guild.me.top_role <= role:
                await ctx.send("I don't have permission to remove this role (my highest role must be above the role you're trying to remove).")
                return

            # Check user's role hierarchy
            if ctx.author.top_role <= role and ctx.author.id != ctx.guild.owner_id:
                await ctx.send("You can't remove a role that is higher than or equal to your highest role.")
                return

            if role not in user.roles:
                await ctx.send(f'{user.mention} does not have the role {role.name}')
                return

            await user.remove_roles(role)
            await ctx.send(f'Removed role {role.name} from {user.mention}')

        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while removing the role: {str(e)}")
            
    @commands.command(help = "Display information about a role")
    @commands.has_permissions(manage_roles=True)
    async def roleinfo(self, ctx, *, role_name: str):
        """Display information about a role"""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Could not find role: {role_name}")
            return

        # Count members with this role
        member_count = len([m for m in ctx.guild.members if role in m.roles])
        
        # Create embed
        embed = discord.Embed(title=f"Role Information: {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Members", value=member_count, inline=True)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        
        # Add permissions
        perms = []
        for perm, value in role.permissions:
            if value:
                perms.append(perm.replace('_', ' ').title())
        if perms:
            embed.add_field(name="Key Permissions", value='\n'.join(perms[:10]), inline=False)

        await ctx.send(embed=embed)

    @commands.command(help ="List all members with a specific role")
    @commands.has_permissions(manage_roles=True)
    async def rolemembers(self, ctx, *, role_name: str):
        """List all members with a specific role"""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"Could not find role: {role_name}")
            return

        members = [m for m in ctx.guild.members if role in m.roles]
        if not members:
            await ctx.send(f"No members have the role {role.name}")
            return

        # Create embed with member list
        embed = discord.Embed(title=f"Members with role: {role.name}", 
                            color=role.color,
                            description=f"Total members: {len(members)}")

        # Split members into chunks if there are many
        chunks = [members[i:i + 20] for i in range(0, len(members), 20)]
        for i, chunk in enumerate(chunks):
            member_list = '\n'.join([f"{m.name}#{m.discriminator}" for m in chunk])
            embed.add_field(name=f"Members {i*20+1}-{i*20+len(chunk)}", 
                          value=member_list, 
                          inline=False)

        await ctx.send(embed=embed)
    
    @kick.error
    @ban.error
    @unban.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify all required arguments.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user specified.")

    @add_role.error
    @remove_role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify both a user and a role.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid user or role specified. Please check the syntax: `!add_role @user RoleName` or `!remove_role @user RoleName`")
        else:
            await ctx.send(f"An error occurred: {str(error)}")

async def setup(client):
    await client.add_cog(Moderation(client))