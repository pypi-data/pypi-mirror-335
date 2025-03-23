from discord.abc import GuildChannel
from discord.ext.commands import Context


class ChannelUtils:
    @staticmethod
    def get_guild_channel(ctx: Context, channel_id: str) -> GuildChannel:
        if channel_id.isdigit():
            channel_id = int(channel_id)
        else:
            channel_id_str = channel_id.split("<#")[-1].split(">")[0]
            channel_id = int(channel_id_str)
        return ctx.guild.get_channel(channel_id)
