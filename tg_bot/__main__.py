import importlib
import re
from typing import Optional, List
import html
import random
import time

from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram.ext.dispatcher import run_async, DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown

from tg_bot import dispatcher, updater, TOKEN, WEBHOOK, OWNER_ID, DONATION_LINK, CERT_PATH, PORT, URL, LOGGER, \
    ALLOW_EXCL, START_PHOTTO, OWNER_NAME, OWNER_USERNAME 
# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from tg_bot.modules import ALL_MODULES
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.misc import paginate_modules

PM_START_TEXT = """
Hello {},My Name is {} !. 

I'm Filter Manager Bot Maintained By [{}](https://t.me/{}). 
"""


DM_START_KEY = """
Hi {}, my name is {}! 
I am the group management bot of FOCUS MOVIES .. You guys can't use me or add me to groups.........
"""


HELP_STRINGS = """
Hello! my name is *{}*.

*Main Available Commands* are Below:

""".format(dispatcher.bot.first_name, "" if not ALLOW_EXCL else "\nഈ പറഞ്ഞിരിക്കുന്ന commandകൾ എല്ലാം  / അല്ലെങ്കിൽ ! വെച്ച് ഉപയോഗിക്കാവുന്നതാണ്...\n")

DONATE_STRING = """Heya, glad to hear you want to donate!
It took lots of work for [my creator](t.me/sonoflars) to get me to where I am now, and every donation helps \
motivate him to make me even better. All the donation money will go to a better VPS to host me, and/or beer \
(see his bio!). He's just a poor student, so every little helps!
There are two ways of paying him; [PayPal](paypal.me/PaulSonOfLars), or [Monzo](monzo.me/paulnionvestergaardlarsen)."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

DEVIL_IMG=START_PHOTTO
ERROR_PIC0 = "https://telegra.ph/file/359bae4c47748aa5c1e54.jpg"
ERROR_PIC1 = "https://telegra.ph/file/5676359ac1bfb83b9f43b.jpg"
ERROR_PIC2 = "https://telegra.ph/file/0d4de8335e7bfd3aaab26.jpg"
ERROR_PIC3 = "https://telegra.ph/file/73e6306b4ab797a193112.jpg"
ERROR_PIC4 = "https://telegra.ph/file/e05eac555667620c78c0a.jpg"
ERROR_PIC5 = "https://telegra.ph/file/fa5987927d2d39aac288e.jpg"
ERROR_PIC6 = "https://telegra.ph/file/ff1e6ce577cbc289fc321.jpg"
ERROR_PIC99 = "https://telegra.ph/file/4dac54cd8baa345e5edac.jpg"
ERROR_PIC7 = "https://telegra.ph/file/022c44496b56bce06e96f.jpg"
ERROR_PIC8 = "https://telegra.ph/file/b3f7639cef8e1ca84824b.jpg"

#sleep how many times after each edit in 'moonanimation' 
EDIT_SLEEP = .25
#edit how many times in 'moonanimation' 
EDIT_TIMES = 32

#please_keep_the_credit
#@the_noob_hacker
moon_ani = [
            "HI bruh",
            "Starting.",    
            "Starting..",
            "Starting...",
            "Starting..",
            "Starting.",
            "Started 🙂",
            "🔛",
            "0️⃣",
            "1️⃣",    
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",    
            "🔟",
            "🔄",
            "😮",
            "😯",
            "😲",
            "😱",
            "🤯",
            "😢",    
            "😥",
            "😓",
            "😞",
            "😖",
            "🤤",
            "🌞"
 ]


SECRET_IMG =  "CAACAgEAAxkBAAIBHWBN67qbEnx7zqEAARP-uY6YBOi_CwACFwEAAk-acEaOOM7BkcVuZB4E"
NO_JOKE = "CAACAgEAAxkBAAIBJGBN8-9edCUFn9yiQb4hb3fyfWSfAALhAANPEHFGe_0ZvMy6OmAeBA"
FREE_FS = "https://telegra.ph/file/f8adb41930c2a396065a0.mp4"

RICK_JOHON = """
❇️Welcome To @Pruthvi_RJ_Group 

❇️The Rules @Pruthvi_RJ_Group  Given Below

Request Format #Request Movie_Name

Example #Request Kirik party

👆👆You Should Request Your Movies like this
 
🚫 don't Request Still Not Released Movies and Digitally Not Released Movies..

🚫 Don't Spam Here..

🚫 No forwarding files from other channels.

🚫 No Sharing Theater Print Files...

✅ only Kannada Movies Can Be Requested Here...

❌ Other Language Movies Not Allowed...

✅ Share And Support us
"""

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("tg_bot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(chat_id=chat_id,
                                text=text,
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=keyboard)


@run_async
def test(bot: Bot, update: Update):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def rulez(bot: Bot, update: Update, args: List[str]):
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_sticker(SECRET_IMG)
            update.effective_message.reply_sticker(NO_JOKE, reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="Help", callback_data="ehelpbotton_")],  
                                                [InlineKeyboardButton(text="Creater",url="https://t.me/the_noobhacker")]]),disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    else:
         

        update.effective_message.reply_text("Heya, How can I help you? 🙂",reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="❓ Help", callback_data="ehelpbotton_")]]))
# for test purposes
def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(bot: Bot, update: Update):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    try:
        if mod_match:
            module = mod_match.group(1)
            text = "Here is the help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) \
                   + HELPABLE[module].__help__
            query.message.reply_text(text=text,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.reply_text(HELP_STRINGS,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.reply_text(HELP_STRINGS,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            query.message.reply_text(text=HELP_STRINGS,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def get_help(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        update.effective_message.reply_text("Contact me in PM to get the list of possible commands.",
                                            reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="Help", callback_data="ehelpbotton_")]]))
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = "Here is the available help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) \
               + HELPABLE[module].__help__
        send_help(chat.id, text, InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id)) for mod in USER_SETTINGS.values())
            dispatcher.bot.send_message(user_id, "These are your current settings:" + "\n\n" + settings,
                                        parse_mode=ParseMode.MARKDOWN)

        else:
            dispatcher.bot.send_message(user_id, "Seems like there aren't any user specific settings available :'(",
                                        parse_mode=ParseMode.MARKDOWN)

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(user_id,
                                        text="Which module would you like to check {}'s settings for?".format(
                                            chat_name),
                                        reply_markup=InlineKeyboardMarkup(
                                            paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)))
        else:
            dispatcher.bot.send_message(user_id, "Seems like there aren't any chat settings available :'(\nSend this "
                                                 "in a group chat you're admin in to find its current settings!",
                                        parse_mode=ParseMode.MARKDOWN)


@run_async
def settings_button(bot: Bot, update: Update):
    query = update.callback_query
    user = update.effective_user
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(escape_markdown(chat.title),
                                                                                     CHAT_SETTINGS[module].__mod_name__) + \
                   CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(text=text,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="Back",
                                                                callback_data="stngs_back({})".format(chat_id))]]))

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text("Hi there! There are quite a few settings for {} - go ahead and pick what "
                                     "you're interested in.".format(chat.title),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(curr_page - 1, CHAT_SETTINGS, "stngs",
                                                          chat=chat_id)))

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text("Hi there! There are quite a few settings for {} - go ahead and pick what "
                                     "you're interested in.".format(chat.title),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(next_page + 1, CHAT_SETTINGS, "stngs",
                                                          chat=chat_id)))

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                                          "you're interested in.".format(escape_markdown(chat.title)),
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(paginate_modules(0, CHAT_SETTINGS, "stngs",
                                                                                        chat=chat_id)))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = msg.text.split(None, 1)

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(text,
                           reply_markup=InlineKeyboardMarkup(
                               [[InlineKeyboardButton(text="Settings",
                                                      url="t.me/{}?start=stngs_{}".format(
                                                          bot.username, chat.id))]]))
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)

@run_async
def a(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(ERROR_PIC1, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def b(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(ERROR_PIC2, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def c(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(ERROR_PIC3, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def d(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(ERROR_PIC4, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def e(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(ERROR_PIC5, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def f(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_video(FREE_FS, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@run_async
def start(bot: Bot, update: Update):
    first_name = update.effective_user.first_name
    msg = update.effective_message.reply_text("cool")
    for x in range(EDIT_TIMES):
        msg.edit_text(moon_ani[x%32])
        time.sleep(EDIT_SLEEP)
    msg.edit_text(PM_START_TEXT.format(escape_markdown(first_name), escape_markdown(bot.first_name), OWNER_NAME, OWNER_USERNAME ),reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton(text="Help", callback_data="ehelpbotton_")],  
                                                [InlineKeyboardButton(text="⚜️ Add to your group ⚜️",url="http://t.me/anjiKicchaNewBot?startgroup=true")],
                                                [InlineKeyboardButton(text="My Owner🇮🇳",url="https://t.me/Akboy99"),InlineKeyboardButton(text="Creater",url="https://t.me/the_noobhacker")]]),disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
    

@run_async
def ehelpbotton_about_callback(update, context):
    query = update.callback_query
    if query.data == "ehelpbotton_":
        query.message.edit_text(
            text=""" Hi.. buddy 
                 \nyou just send */help* to the bot .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Go Back", callback_data="ehelpbotton_back")
                 ]
                ]
            ),
        )
    elif query.data == "ehelpbotton":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=True,
        )



@run_async
def ppchi(bot: Bot, update: Update):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]

    if chat.type == "private":
        update.effective_message.reply_photo(DEVIL_IMG, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        if OWNER_ID != 254318997 and DONATION_LINK:
            update.effective_message.reply_photo(DEVIL_IMG, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

                                            
    else:
        try:
            bot.send_message(user.id, DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

            update.effective_message.reply_text("I've PM'ed you about donating to my creator!")
        except Unauthorized:
            update.effective_message.reply_text("Contact me in PM first to get donation information.")


def migrate_chats(bot: Bot, update: Update):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    a_handler = CommandHandler("a", a)
    b_handler = CommandHandler("b", b)
    c_handler = CommandHandler("c", c)
    d_handler = CommandHandler("d", d)
    e_handler = CommandHandler("e", e)
    f_handler = CommandHandler("f", f)
    lolan_handler = CommandHandler("rulez",rulez)
    ehelpbotton_callback_handler = CallbackQueryHandler(ehelpbotton_about_callback, pattern=r"ehelpbotton_")


    ppchi_handler = CommandHandler("ppchi", ppchi)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(ehelpbotton_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(ppchi_handler)
    dispatcher.add_handler(a_handler)
    dispatcher.add_handler(b_handler)
    dispatcher.add_handler(c_handler)
    dispatcher.add_handler(d_handler)
    dispatcher.add_handler(e_handler)
    dispatcher.add_handler(f_handler)
    dispatcher.add_handler(lolan_handler)
    
    # dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN,
                                    certificate=open(CERT_PATH, 'rb'))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()
