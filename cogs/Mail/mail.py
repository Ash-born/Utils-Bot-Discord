class Mail(commands.Cog) :
    @commands.command
    async def mail(self,ctx,*,args):
        ctx.channel.send("test")