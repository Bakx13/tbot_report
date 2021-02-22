import logging
import sys
import time
import traceback

import telegram
import telegram.error
import telegram

import tbot_report.lib.loadconfig as MConfig

log = logging.getLogger(__name__)


def factory(cfg: MConfig):
    """Construct a DuckBot type based on the passed config."""

    def catch_telegram_errors(func):
        """Decorator, can be applied to any function to retry in case of Telegram errors."""

        def result_func(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                # Bot was blocked by the user
                except telegram.error.Unauthorized:
                    log.debug(f"Unauthorized to call {func.__name__}(), skipping.")
                    break
                # Telegram API didn't answer in time
                except telegram.error.TimedOut:
                    log.warning(f"Timed out while calling {func.__name__}(),"
                                f" retrying in {cfg['Telegram']['timed_out_pause']} secs...")
                    time.sleep(cfg.telegram["timed_out_pause"])
                # Telegram is not reachable
                except telegram.error.NetworkError as error:
                    log.error(f"Network error while calling {func.__name__}(),"
                              f" retrying in {cfg.telegram['error_pause']} secs...\n"
                              f"Full error: {error.message}")
                    time.sleep(cfg.telegram["error_pause"])
                # Unknown error
                except telegram.error.TelegramError as error:
                    if error.message.lower() in ["bad gateway", "invalid server response"]:
                        log.warning(f"Bad Gateway while calling {func.__name__}(),"
                                    f" retrying in {cfg.telegram['error_pause']} secs...")
                        time.sleep(cfg.telegram["error_pause"])
                    elif error.message.lower() == "timed out":
                        log.warning(f"Timed out while calling {func.__name__}(),"
                                    f" retrying in {cfg.telegram['timed_out_pause']} secs...")
                        time.sleep(cfg.telegram["timed_out_pause"])
                    else:
                        log.error(f"Telegram error while calling {func.__name__}(),"
                                  f" retrying in {cfg.telegram['error_pause']} secs...\n"
                                  f"Full error: {error.message}")
                        traceback.print_exception(*sys.exc_info())
                        time.sleep(cfg.telegram["error_pause"])

        return result_func

    class DuckBot:
        def __init__(self, *args, **kwargs):
            self.bot = telegram.Bot(token=cfg.telegram["token"], *args, **kwargs)
            self.last_message_inline_keyboard = telegram.Message
            self.last_message = telegram.Message
            self.last_message_keyboard = telegram.Message

        @catch_telegram_errors
        def send_message(self, *args, **kwargs):
            # All messages are sent in HTML parse mode
            # Добавляем в бота данные по последнему сообщению
            log.debug(f"send message as duckbot")
            rtn = None
            if 'reply_markup' in kwargs:
                log.debug(f"send reply_markup as duckbot")
                if isinstance(kwargs['reply_markup'], telegram.InlineKeyboardMarkup):
                    self.last_message_inline_keyboard = self.bot.send_message(parse_mode="HTML", *args, **kwargs)
                    rtn = self.last_message_inline_keyboard
                    self.last_message = rtn
                    log.debug(f"update last_message_inline_keyboard")
                elif isinstance(kwargs['reply_markup'], telegram.ReplyKeyboardMarkup):
                    self.last_message_keyboard = self.bot.send_message(parse_mode="HTML", *args, **kwargs)
                    rtn = self.last_message_keyboard
                    self.last_message = rtn
                    log.debug(f"update ReplyKeyboardMarkup")
            else:
                self.last_message = self.bot.send_message(parse_mode="HTML", *args, **kwargs)
                rtn = self.last_message
                log.debug(f"send last_message")
            return rtn

        @catch_telegram_errors
        def edit_message_text(self, *args, **kwargs):
            # All messages are sent in HTML parse mode
            return self.bot.edit_message_text(parse_mode="HTML", *args, **kwargs)

        @catch_telegram_errors
        def edit_message_caption(self, *args, **kwargs):
            # All messages are sent in HTML parse mode
            return self.bot.edit_message_caption(parse_mode="HTML", *args, **kwargs)

        @catch_telegram_errors
        def edit_message_reply_markup(self, *args, **kwargs):
            log.debug(f"edit reply_markup as duckbot")
            rtn = None
            if 'reply_markup' in kwargs:
                if isinstance(kwargs['reply_markup'], telegram.InlineKeyboardMarkup):
                    self.last_message_inline_keyboard = self.bot.edit_message_reply_markup(*args, **kwargs)
                    rtn = self.last_message_inline_keyboard
                    log.debug(f"edit last_message_inline_keyboard")
                elif isinstance(kwargs['reply_markup'], telegram.ReplyKeyboardMarkup):
                    self.last_message_keyboard = self.bot.edit_message_reply_markup(*args, **kwargs)
                    rtn = self.last_message_keyboard
                    log.debug(f"edit ReplyKeyboardMarkup")
            else: return None
            return rtn

        @catch_telegram_errors
        def get_updates(self, *args, **kwargs):
            return self.bot.get_updates(*args, **kwargs)

        @catch_telegram_errors
        def get_me(self, *args, **kwargs):
            return self.bot.get_me(*args, **kwargs)

        @catch_telegram_errors
        def answer_callback_query(self, *args, **kwargs):
            return self.bot.answer_callback_query(*args, **kwargs)

        @catch_telegram_errors
        def answer_pre_checkout_query(self, *args, **kwargs):
            return self.bot.answer_pre_checkout_query(*args, **kwargs)

        @catch_telegram_errors
        def send_invoice(self, *args, **kwargs):
            return self.bot.send_invoice(*args, **kwargs)

        @catch_telegram_errors
        def get_file(self, *args, **kwargs):
            return self.bot.get_file(*args, **kwargs)

        @catch_telegram_errors
        def send_chat_action(self, *args, **kwargs):
            return self.bot.send_chat_action(*args, **kwargs)

        @catch_telegram_errors
        def delete_message(self, *args, **kwargs):
            return self.bot.delete_message(*args, **kwargs)

        @catch_telegram_errors
        def send_document(self, *args, **kwargs):
            return self.bot.send_document(*args, **kwargs)

        # More methods can be added here

    return DuckBot()
