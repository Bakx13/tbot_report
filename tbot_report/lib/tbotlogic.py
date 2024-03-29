import logging
import sqlalchemy
import telegram
import sys

# подкючаем локальные библиотеки
import tbot_report.lib.loadconfig as MConfig
import tbot_report.localization.localization as localization
import tbot_report.lib.duckbot as duckbot
import tbot_report.lib.worker as worker


log = logging.getLogger(__name__)


class TBot(object):
    def initbot(user_cfg: MConfig):
       #инициализируем бота
        bot = duckbot.factory(user_cfg)
        log.debug("Testing bot token...")
        me = bot.get_me()
        if me is None:
            logging.fatal("The token you have entered in the config file is invalid. Fix it, then restart greed.")
            sys.exit(1)
        log.debug("Bot token is valid!")
        # Notify on the console that the bot is starting
        log.info(f"@{me.username} is starting!")
        return bot

    def run(user_cfg: MConfig, default_loc: localization.Localization, bot: duckbot, engine: sqlalchemy):
        """запускаем бесконечный цикл обработки бота"""
        # Current update offset; if None it will get the last 100 unparsed messages
        next_update = None

        # Create a dictionary linking the chat ids to the Worker objects
        # {"1234": <Worker>}
        chat_workers = {}
        while True:
            # Get a new batch of 100 updates and mark the last 100 parsed as read
            update_timeout = user_cfg.telegram["long_polling_timeout"]
            log.debug(f"Getting updates from Telegram with a timeout of {update_timeout} seconds")
            updates = bot.get_updates(offset=next_update, timeout=update_timeout)
            # Parse all the updates
            for update in updates:
                # If the update is a message...
                if update.message is not None:
                    # Ensure the message has been sent in a private chat
                    if update.message.chat.type != "private":
                        log.debug(f"Received a message from a non-private chat: {update.message.chat.id}")
                        # Notify the chat
                        #bot.send_message(update.message.chat.id, default_loc.get("error_nonprivate_chat"))
                        # Skip the update
                        continue
                    # If the message is a start command...
                    if isinstance(update.message.text, str) and update.message.text.startswith("/start"):
                        log.info(f"Received /start from: {update.message.chat.id}")
                        # Check if a worker already exists for that chat
                        old_worker = chat_workers.get(update.message.chat.id)
                        # If it exists, gracefully stop the worker
                        if old_worker:
                            log.debug(f"Received request to stop {old_worker.name}")
                            old_worker.stop("request")
                        # Initialize a new worker for the chat
                        new_worker = worker.Worker(bot=bot,
                                                   chat=update.message.chat,
                                                   telegram_user=update.message.from_user,
                                                   cfg=user_cfg,
                                                   engine=engine,
                                                   daemon=True)
                        # Start the worker
                        log.debug(f"Starting {new_worker.name}")
                        new_worker.start()
                        # Store the worker in the dictionary
                        chat_workers[update.message.chat.id] = new_worker
                        # Skip the update
                        continue
                    # Otherwise, forward the update to the corresponding worker
                    receiving_worker = chat_workers.get(update.message.chat.id)
                    # Ensure a worker exists for the chat and is alive
                    log.debug("init receiving_worker")
                    if receiving_worker is None:
                        log.debug(f"Received a message in a chat without worker: {update.message.chat.id}")
                        # Suggest that the user restarts the chat with /start
                        bot.send_message(update.message.chat.id, default_loc.get("error_no_worker_for_chat"),
                                         reply_markup=telegram.ReplyKeyboardRemove())
                        # Skip the update
                        continue
                    # If the worker is not ready...
                    if not receiving_worker.is_ready():
                        log.debug(f"Received a message in a chat where the worker wasn't ready yet: {update.message.chat.id}")
                        # Suggest that the user restarts the chat with /start
                        bot.send_message(update.message.chat.id, default_loc.get("error_worker_not_ready"),
                                         reply_markup=telegram.ReplyKeyboardRemove())
                        # Skip the update
                        continue
                    # If the message contains the "Cancel" string defined in the strings file...
                    #exit(254)
                    '''
                    if update.message.text == receiving_worker.loc.get("menu_all_cancel"):
                        log.debug(f"Forwarding CancelSignal to {receiving_worker}")
                        # Send a CancelSignal to the worker instead of the update
                        receiving_worker.queue.put(worker.CancelSignal())
                    else:
                        log.debug(f"Forwarding message to {receiving_worker}")
                        # Forward the update to the worker
                        receiving_worker.queue.put(update)
                    '''
                    log.debug(f"Forwarding message to {receiving_worker}")
                    # Forward the update to the worker
                    receiving_worker.queue.put(update)                # If the update is a inline keyboard press...
                if isinstance(update.callback_query, telegram.CallbackQuery):
                    # Forward the update to the corresponding worker
                    receiving_worker = chat_workers.get(update.callback_query.from_user.id)
                    # Ensure a worker exists for the chat
                    if receiving_worker is None:
                        log.debug(
                            f"Received a callback query in a chat without worker: {update.callback_query.from_user.id}")
                        # Suggest that the user restarts the chat with /start
                        bot.send_message(update.callback_query.from_user.id, default_loc.get("error_no_worker_for_chat"))
                        # Skip the update
                        continue
                    # Check if the pressed inline key is a cancel button
                    if update.callback_query.data == "cmd_cancel":
                        log.debug(f"Forwarding CancelSignal to {receiving_worker}")
                        # Forward a CancelSignal to the worker
                        receiving_worker.queue.put(worker.CancelSignal())
                        # Notify the Telegram client that the inline keyboard press has been received
                        bot.answer_callback_query(update.callback_query.id)
                    else:
                        log.debug(f"Forwarding callback query to {receiving_worker}")
                        # Forward the update to the worker
                        receiving_worker.queue.put(update)
                # If the update is a precheckoutquery, ensure it hasn't expired before forwarding it
                if isinstance(update.pre_checkout_query, telegram.PreCheckoutQuery):
                    # Forward the update to the corresponding worker
                    receiving_worker = chat_workers.get(update.pre_checkout_query.from_user.id)
                    # Check if it's the active invoice for this chat
                    if receiving_worker is None or \
                            update.pre_checkout_query.invoice_payload != receiving_worker.invoice_payload:
                        # Notify the user that the invoice has expired
                        log.debug(f"Received a pre-checkout query for an expired invoice in: {update.pre_checkout_query.from_user.id}")
                        try:
                            bot.answer_pre_checkout_query(update.pre_checkout_query.id,
                                                          ok=False,
                                                          error_message=default_loc.get("error_invoice_expired"))
                        except telegram.error.BadRequest:
                            log.error("pre-checkout query expired before an answer could be sent!")
                        # Go to the next update
                        continue
                    log.debug(f"Forwarding pre-checkout query to {receiving_worker}")
                    # Forward the update to the worker
                    receiving_worker.queue.put(update)
            # If there were any updates...
            if len(updates):
                # Mark them as read by increasing the update_offset
                next_update = updates[-1].update_id + 1
