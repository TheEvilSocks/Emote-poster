from discord.ext.commands import command
import re
import time
import os


class Commands:
    def __init__(self, bot):
        self.bot = bot

    @command(name='emotes', pass_context=True)
    async def emotes(self, ctx, invite: str, twitch=None, submitter=None):
        """Post global emotes from a server
        twitch can be twitch link or the submitter id"""
        if os.path.exists('posted.txt'):
            with open('posted.txt') as f:
                posted = f.read().split('\n')
        else:
            posted = []

        await self.bot.delete_message(ctx.message)

        try:
            invite = await self.bot.get_invite(invite)
        except:
            with open('invalid.txt', 'a') as f:
                f.write(str(invite) + '\n')
            return

        server = self.bot.get_server(invite.server.id)
        if not server:
            return

        if server.id in posted:
            return print('Duplicate server %s' % str(invite))

        name = server.name
        emotes_ = list(filter(lambda e: e.managed and e.require_colons and not e.roles, server.emojis))
        if not emotes_:
            return

        emotes = ''
        for e in emotes_:
            emotes += str(e) + ' '

        emotes = emotes.strip()

        if twitch is not None:
            try:
                submitter = int(twitch)
                submitter = '<@!%s>' % submitter
                twitch = None
            except:
                try:
                    int(submitter)
                    submitter = '<@!%s>' % submitter
                except:
                    pass

        fmt = '----------\n{name}\nEmotes: {emotes}\n{invite}'

        if twitch:
            fmt += '\n<{twitch}>'

        if submitter:
            fmt += '\nSubmitted by: {submitter}'

        message = fmt.format(name=name, invite=invite, twitch=twitch,
                          emotes=emotes, submitter=submitter)

        for msg in split_string(message):
            await self.bot.say(msg)

        with open('posted.txt', 'a') as f:
            f.write(server.id + '\n')

    @command()
    async def get_all_invites(self, channel, limit=500):
        """Get all discord invites from a channel"""
        channel = self.bot.get_channel(channel)

        r = re.compile('(https:\/\/discord.gg\/[\d\w]+)')
        s = ''
        counter = 0
        async for message in self.bot.logs_from(channel, limit=limit):
            match = r.findall(message.content.replace('\n', ' '))
            counter += 1
            if match:
                s += match[0] + '\n'
            else:
                print('Failed:', message.content)

        print(counter, 'messages read')
        print(len(s.split('\n')), 'valid lines')
        with open('invites.txt', 'w') as f:
            f.write(s)

    @command()
    async def reload(self, *, name):
        """Reload an extension.
        Usage: reload commands"""
        t = time.time()
        try:
            self.bot.unload_extension(name)
            self.bot.load_extension(name)
        except Exception as e:
            print(e)
            return

        await self.bot.say('Reloaded {} in {:.0f}ms'.format(name, (time.time()-t)*1000))


def setup(bot):
    bot.add_cog(Commands(bot))


def split_string(to_split, maxlen=2000, splitter=' '):
    if len(to_split) < maxlen:
        return [to_split]

    to_split = [s + splitter for s in to_split.split(splitter)]
    to_split[-1] = to_split[-1][:-1]
    length = 0
    split = ''
    splits = []
    for s in to_split:
        l = len(s)
        if length + l > maxlen:
            splits += [split]
            split = s
            length = l
        else:
            split += s
            length += l

    splits.append(split)

    return splits
