import os
import yaml
import telegram
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram_bot.util import build_menu, states_map
from telegram_bot.ocr_functions import run_scraper

STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'states.yaml')
with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

SENTINEL = dict()

def entry(bot, update):
    logging.info('entry')
    # Is this a reply to something?
    if update.callback_query:
        logging.info('callback query')
        # if this is a reply to the `/start` message, it should contain a state code
        if update.callback_query.message.reply_to_message.text == '/start':
            state_code = update.callback_query.data.lower()
            SENTINEL['state_code'] = state_code

            # TODO - check what type of input is required for this state (from yaml file)
            url_type = states_all[state_code]['type']
            logging.info(url_type)

            if url_type == 'html':
                logging.info('running_scraper')
                # run directly
                run_scraper(bot, update.callback_query.message.chat.id, SENTINEL['state_code'], url_type, states_all[state_code]['url'])
            else:
                # reply back asking for file
                bot.send_message(
                    chat_id=update.callback_query.message.reply_to_message.chat.id,
                    text=f"Upload {states_all[state_code]['type']} for {states_all[state_code]['name']}\
                    from the following sources {states_all[state_code]['url_sources']}"
                )

    # Is this a direct message?
    if update.message:
        logging.info('message')
        # If the direct message is `/start`
        if update.message.text and update.message.text.startswith("/start"):
            bot.send_chat_action(
                chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING
            )
            button_list = []
            for st_name in states_map.keys():
                button_list.append(
                    InlineKeyboardButton(
                        st_name, callback_data=states_map[st_name]
                    )
                )
            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Which state do you want to fetch data for?",
                reply_to_message_id=update.message.message_id,
                reply_markup=reply_markup,
            )
            return

        # If the direct message is `/test`
        elif update.message.text and update.message.text.startswith("/test"):
            bot.send_chat_action(
                chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING
            )
            update.message.reply_text("200 OK!", parse_mode=telegram.ParseMode.MARKDOWN)
            return

        # If the direct message is `/help`
        elif update.message.text and update.message.text.startswith("/help"):
            help_text = f"""
            \n*Steps to run bot*
            1. Run /start
            2. Select state for which you want to extract data
            3. Once you select the state, the bot will ask you to upload either an image or a pdf
            4. Upload the image or PDF and ensure it is the correct one to extract COVID case details for that state
            5. Copy & paste the response into the google sheet

            \n\n_Send `/test` for checking if the bot is online_

            \n\n_Send `/start` to start the extraction process"""

            update.message.reply_text(
                str(help_text), parse_mode=telegram.ParseMode.MARKDOWN
            )
            return

        # If the direct message is file type of PDF
        elif update.message.document and update.message.document.mime_type == 'application/pdf':
            bot.send_chat_action(
                chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING
            )
            # TODO - save datetime stamp with the state_code as file name
            pdf_path = '/tmp/{}.pdf'.format(SENTINEL['state_code'].lower())
            pdf_file = update.message.document.get_file()
            pdf_file.download(pdf_path)
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Extracting data from PDF",
                reply_to_message_id=update.message.message_id
            )
            run_scraper(bot, update.message.chat.id, SENTINEL['state_code'], 'pdf', pdf_path)

        # If the direct message is file type of image
        elif update.message.photo:
            bot.send_chat_action(
                chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING
            )
            print('this is a photo for', SENTINEL)
            photo = update.message.photo[-1]
            image_path = '/tmp/{}.jpg'.format(SENTINEL['state_code'].lower())
            image_file = bot.get_file(photo.file_id)
            image_file.download()
            bot.send_message(
                chat_id=update.message.chat.id,
                text="Extracting data from Image",
                reply_to_message_id=update.message.message_id
            )
            run_scraper(bot, update.message.chat.id, SENTINEL['state_code'], 'image', image_path)

        else:
            print('this is something else complletely')
