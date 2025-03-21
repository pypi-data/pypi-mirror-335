import inspect

from discord.ext.commands import Context


class MessageUtils:
    @staticmethod
    def is_typing(func):
        signature = inspect.signature(func)
        params = list(signature.parameters.values())
        if not params:
            raise ValueError("The function must have at least one parameter.")
        if params[0].annotation is not Context:
            raise ValueError(f"The first parameter must be of type {Context}.")

        async def wrapper(ctx: Context, *args, **kwargs):
            interaction = ctx.interaction
            if interaction:
                await interaction.response.defer()
                return await func(ctx, *args, **kwargs)
            else:
                async with ctx.typing():
                    return await func(ctx, *args, **kwargs)

        return wrapper
