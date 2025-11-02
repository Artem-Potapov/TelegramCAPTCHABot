import datetime


import async_lru
import dotenv
import os
import telethon as tl
import asyncio
import logging
import captcha_stuff

from telethon.sync import TelegramClient, events
from telethon.tl import types, functions
from types import NoneType
from typing import Callable, Any

logging.basicConfig(format='[%(levelname) %(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

dotenv.load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

class PendingCaptcha:
    def __init__(self, user: tl.types.User, _timestamp: float, channel: tl.types.Channel, bot: TelegramClient):
        self.time_to_complete = 5*60
        self.completed = False
        self.user: tl.types.User = user
        self.beginning_time = datetime.datetime.fromtimestamp(_timestamp)
        self.channel = channel
        self.emoji = None
        self.answers = None
        self.failed_or_left = False
        self.captcha_handler: Callable|None = None
        self.welcome_message: tl.types.Message|None = None

    async def init_captcha(self, bot: TelegramClient):
        emoji, answers = captcha_stuff.generate_captcha()
        self.emoji = emoji
        self.answers = answers
        print(self.user.first_name, self.user.last_name)
        if self.user.last_name:
            name = self.user.first_name + " " + self.user.last_name
        else:
            name = self.user.first_name
        msg = f"""Для того чтобы начать общаться, пройдите **капчу**, [{name}](tg://user?id={self.user.id}).
Напишите название животного (одним словом без прилагательных и спецсимволов), изображённого на эмодзи: {self.emoji}.

Возникли проблемы? Напишите модераторам!
[Артём](https://t.me/Artem_Potap235)
[Тон](https://t.me/TONNY618)
[Хлебъ](https://t.me/Hleb_Zavod)"""
        self.welcome_message = await bot.send_message(self.channel, msg,
                               parse_mode = "markdown",
                               buttons=types.ReplyKeyboardForceReply(single_use=True, selective=True),
                               link_preview=False)

        captcha_handler = self.get_handler(bot)
        event = events.NewMessage(from_users=[self.user.id], chats=[self.channel.id])
        bot.add_event_handler(captcha_handler, event)
        asyncio.create_task(self.verify_captcha(bot))


    def get_handler(self, bot: TelegramClient) -> Callable[[events.NewMessage], None]:
        if self.captcha_handler is None:
            async def _captcha_handler(event: tl.custom.Message):
                text = event.text.lower()
                print(f"поймал капчу, текст: {text}")
                if captcha_stuff.distance(text, self.answers) <= 2:
                    print("Правда!")
                    self.completed = True
                    inp_cnl = await event.get_input_chat()
                    await bot.send_message(inp_cnl, f"Юзер [{self.user.username}](tg://user?id={self.user.id}) успешно выполнил капчу!")
                    bot.remove_event_handler(self.captcha_handler)
                else:
                    print("Неа")
                    try:
                        await event.delete()
                    except tl.errors.MessageDeleteForbiddenError:
                        await bot.send_message(self.channel,
                                               "Я не смог удалить сообщение. У бота точно есть права администратора?")
            self.captcha_handler = _captcha_handler
        return self.captcha_handler

    async def verify_captcha(self, bot: TelegramClient) -> int:
        print(f"Сплю {self.time_to_complete} секунд")
        await asyncio.sleep(self.time_to_complete)
        await bot.delete_messages(self.channel, [self.welcome_message.id], revoke=True)
        if self.failed_or_left:
            print("чета странное")
            bot.remove_event_handler(self.captcha_handler)
            del self
            return 0
        inp_cnl = tl.utils.get_input_channel(self.channel)
        if self.completed:
            print("выполнено!")
            del self
            return 1
        else:
            print("бан нахуй")
            usr = tl.utils.get_input_user(self.user)
            tm = self.beginning_time.__add__(datetime.timedelta(365*20))
            try:
                await bot.edit_permissions(inp_cnl, usr, tm,
                                           view_messages=False,
                                           send_messages=False,
                                           send_media=False,
                                           send_stickers=False,
                                           send_gifs=False,
                                           send_games=False,
                                           send_inline=False,
                                           embed_link_previews=False,
                                           send_polls=False,
                                           change_info=False,
                                           invite_users=False,
                                           pin_messages=False)
            except Exception as E:
                tmp = ""
                if isinstance(E, tl.errors.ChatAdminRequiredError):
                    tmp = "Кажется, что у бота нету прав банить юзеров!"
                await bot.send_message(inp_cnl, f"Произошла ошибка при попытке забанить юзера @{self.user.username} [ссылка](tg://user?id={self.user.id}) `{self.user.id}`!\n{tmp}")
            else:
                await bot.send_message(inp_cnl, f"Юзер @{self.user.username} [ссылка](tg://user?id={self.user.id} `{self.user.id}` Успешно забанен за невыполнение капчи!")
            bot.remove_event_handler(self.captcha_handler)
            del self
            return 2




with TelegramClient('CaptchaBOT', API_ID, API_HASH) as bot:
    bot: TelegramClient = bot.start(bot_token=BOT_TOKEN)

    @async_lru.alru_cache()
    async def getme() -> int:
        a = await bot.get_me()
        if isinstance(a, (types.InputUser, types.InputPeerUser)):
            return a.user_id
        else:
            return a.id

    @bot.on(events.Raw())
    async def uwu(event: events.Raw):
        print("Raw event:", event)


    @bot.on(event=events.Raw(tl.types.UpdateChannelParticipant))
    async def uwu2(event: tl.types.UpdateChannelParticipant):
        print("handler is here")
        if isinstance(event.new_participant, types.ChannelParticipantSelf):
            msg = """Чтобы бот заработал, ему необходимы права администратора и эти разрешения:
> Банить пользователей
> Удалять сообщения"""
            await bot.send_message(types.PeerChannel(event.channel_id), msg)
            raise events.StopPropagation
        elif isinstance(event.prev_participant, (NoneType, types.ChannelParticipant)) and \
                not isinstance(event.new_participant, (NoneType, types.ChannelParticipantBanned, types.ChannelParticipantAdmin)):
            print("handler ACTUALLY went through")

            # me = await getme()
            # if me == event.user_id:
            #     print("Это я! Летс брейк!")
            #     raise events.StopPropagation

            date = event.date.timestamp()
            channel_id = event.channel_id
            userid = event.user_id
            users: list[types.User] = await bot(tl.functions.users.GetUsersRequest(id=[userid]))
            usr = users[0]
            channels: types.messages.Chats = await bot(tl.functions.channels.GetChannelsRequest(id=[channel_id]))
            channel: types.Channel = channels.chats[0]
            print(channels)
            print("===")
            print(users)

            print(tl.utils.get_input_peer(users[0]))
            print("===")
            usarus = PendingCaptcha(user=usr, _timestamp=date, channel=channel, bot=bot)
            await usarus.init_captcha(bot=bot)


            #display_captcha

    # @bot.on(events.Raw(types.UpdateNewChannelMessage))
    # async def uwu31(event: types.UpdateNewChannelMessage):
    #     channel = event.message.peer_id
    #     await bot.send_message(channel, "uwu! @zopiXXX [uwu](tg://user?id=936637357)",
    #                            parse_mode="markdown",
    #                            buttons=types.ReplyKeyboardForceReply(single_use=True, selective=True))


    @bot.on(events.NewMessage(pattern='/stopitall'))
    async def eee(event: tl.custom.Message):
        await event.delete()
        bot.disconnect()
        raise KeyboardInterrupt


    try:
        bot.run_until_disconnected()
    except KeyboardInterrupt:
        print("pass")