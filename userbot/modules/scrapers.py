# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# thanks to the owner of X-tra-Telegram for tts fix
#
""" Userbot module containing various scrapers. """

import os
import time
import asyncio
import shutil
import json
import requests
from os import popen
from userbot.utils import chrome, options
import urllib.parse
import logging
from bs4 import BeautifulSoup
import re
from re import match
import io
from random import choice
from humanize import naturalsize
import qrcode
import barcode
from barcode.writer import ImageWriter
import emoji
from googletrans import Translator
from time import sleep
from html import unescape
from re import findall
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus
from urllib.error import HTTPError
from telethon import events
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from urbandict import define
from requests import get
from requests import get, post, exceptions
from search_engine_parser import GoogleSearch
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from gtts import gTTS, gTTSError
from gtts.lang import tts_langs
from emoji import get_emoji_regexp
from telethon.tl.types import MessageMediaPhoto
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER, GOOGLE_CHROME_BIN, bot, REM_BG_API_KEY, TEMP_DOWNLOAD_DIRECTORY, OCR_SPACE_API_KEY, LOGS
from userbot.events import register
from telethon.tl.types import DocumentAttributeAudio
from userbot.utils import progress, humanbytes, time_formatter, chrome, googleimagesdownload
import subprocess
from datetime import datetime
import asyncurban


CARBONLANG = "auto"
TTS_LANG = "en"
TRT_LANG = "en"
TEMP_DOWNLOAD_DIRECTORY = "/root/userbot/.bin"

async def ocr_space_file(filename,
                         overlay=False,
                         api_key=OCR_SPACE_API_KEY,
                         language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
    }
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data=payload,
        )
    return r.json()

DOGBIN_URL = "https://del.dog/"    

@register(outgoing=True, pattern="^.crblang (.*)")
async def setlang(prog):
    global CARBONLANG
    CARBONLANG = prog.pattern_match.group(1)
    await prog.edit(f"Language for carbon.now.sh set to {CARBONLANG}")

@register(outgoing=True, pattern="^.carbon")
async def carbon_api(e):
    """ A Wrapper for carbon.now.sh """
    await e.edit("`Processing..`")
    CARBON = 'https://carbon.now.sh/?l={lang}&code={code}'
    global CARBONLANG
    textx = await e.get_reply_message()
    pcode = e.text
    if pcode[8:]:
        pcode = str(pcode[8:])
    elif textx:
        pcode = str(textx.message)  # Importing message to module
    code = quote_plus(pcode)  # Converting to urlencoded
    await e.edit("`Processing..\n25%`")
    if os.path.isfile("/root/userbot/.bin/carbon.png"):
        os.remove("/root/userbot/.bin/carbon.png")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {'download.default_directory': '/root/userbot/.bin'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER,
                              options=chrome_options)
    driver.get(url)
    await e.edit("`Processing..\n50%`")
    download_path = '/root/userbot/.bin'
    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': download_path
        }
    }
    command_result = driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
   # driver.find_element_by_xpath("//button[contains(text(),'4x')]").click()
   # driver.find_element_by_xpath("//button[contains(text(),'PNG')]").click()
    await e.edit("`Processing..\n75%`")
    # Waiting for downloading
    while not os.path.isfile("/root/userbot/.bin/carbon.png"):
        await sleep(0.5)
    await e.edit("`Processing..\n100%`")
    file = '/root/userbot/.bin/carbon.png'
    await e.edit("`Uploading..`")
    await e.client.send_file(
        e.chat_id,
        file,
        caption="Made using [Carbon](https://carbon.now.sh/about/),\
        \na project by [Dawn Labs](https://dawnlabs.io/)",
        force_document=True,
        reply_to=e.message.reply_to_msg_id,
    )

    os.remove('/root/userbot/.bin/carbon.png')
    driver.quit()
    # Removing carbon.png after uploading
    await e.delete()  # Deleting msg
    
    
@register(outgoing=True, pattern="^.img (.*)")
async def img_sampler(event):
    """ For .img command, search and return images matching the query. """
    await event.edit("Processing...")
    query = event.pattern_match.group(1)
    lim = findall(r"lim=\d+", query)
    try:
        lim = lim[0]
        lim = lim.replace("lim=", "")
        query = query.replace("lim=" + lim[0], "")
    except IndexError:
        lim = 5
    response = googleimagesdownload()

    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg",
        "no_directory": "no_directory"
    }

    # passing the arguments to the function
    paths = response.download(arguments)
    lst = paths[0][query]
    await event.client.send_file(
        await event.client.get_input_entity(event.chat_id), lst)
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])))
    await event.delete()


@register(outgoing=True, pattern="^.currency (.*)")
async def moni(event):
    input_str = event.pattern_match.group(1)
    input_sgra = input_str.split(" ")
    if len(input_sgra) == 3:
        try:
            number = float(input_sgra[0])
            currency_from = input_sgra[1].upper()
            currency_to = input_sgra[2].upper()
            request_url = "https://api.exchangeratesapi.io/latest?base={}".format(
                currency_from)
            current_response = get(request_url).json()
            if currency_to in current_response["rates"]:
                current_rate = float(current_response["rates"][currency_to])
                rebmun = round(number * current_rate, 2)
                await event.edit("{} {} = {} {}".format(
                    number, currency_from, rebmun, currency_to))
            else:
                await event.edit(
                    "`This seems to be some alien currency, which I can't convert right now.`"
                )
        except Exception as e:
            await event.edit(str(e))
    else:
        await event.edit("`Invalid syntax.`")
        return


@register(outgoing=True, pattern=r"^.google (.*)")
async def gsearch(q_event):
    """ For .google command, do a Google search. """
    match = q_event.pattern_match.group(1)
    page = findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page))
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(10):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"[{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await q_event.edit("**Search Query:**\n`" + match + "`\n\n**Results:**\n" +
                       msg,
                       link_preview=False)

    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            "Google Search query `" + match + "` was executed successfully",
        )

@register(outgoing=True, pattern=r"^.google1 (.*)")
async def gsearch(q_event):
    """ For .google command, do a Google search. """
    match = q_event.pattern_match.group(1)
    page = findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
    except IndexError:
        page = 1
    search_args = (str(match), int(page))
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(1):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"[{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await q_event.edit("**Search Query:**\n`" + match + "`\n\n" +
                       msg,
                       link_preview=False)

    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            "Google Search query `" + match + "` was executed successfully",
        )


@register(outgoing=True, pattern=r"^.wiki (.*)")
async def wiki(wiki_q):
    """ For .wiki command, fetch content from Wikipedia. """
    match = wiki_q.pattern_match.group(1)
    try:
        summary(match)
    except DisambiguationError as error:
        await wiki_q.edit(f"Disambiguated page found.\n\n{error}")
        return
    except PageError as pageerror:
        await wiki_q.edit(f"Page not found.\n\n{pageerror}")
        return
    result = summary(match)
    if len(result) >= 4096:
        file = open("output.txt", "w+")
        file.write(result)
        file.close()
        await wiki_q.client.send_file(
            wiki_q.chat_id,
            "output.txt",
            reply_to=wiki_q.id,
            caption="`Output too large, sending as file`",
        )
        if os.path.exists("output.txt"):
            os.remove("output.txt")
        return
    await wiki_q.edit("**Search:**\n`" + match + "`\n\n**Result:**\n" + result)
    if BOTLOG:
        await wiki_q.client.send_message(
            BOTLOG_CHATID, f"Wiki query `{match}` was executed successfully")


@register(outgoing=True, pattern="^.ud (.*)")
async def _(event):
    if event.fwd_from:
        return
    await event.edit("processing...")
    word = event.pattern_match.group(1)
    urban = asyncurban.UrbanDictionary()
    try:
        mean = await urban.get_word(word)
        await event.edit("Text: **{}**\n\nMeaning: **{}**\n\nExample: __{}__".format(mean.word, mean.definition, mean.example))
    except asyncurban.WordNotFoundError:
        await event.edit("No result found for **" + word + "**")
       
               

@register(outgoing=True, pattern=r"^.tts(?: |$)([\s\S]*)")
async def text_to_speech(query):
#async def _(event):
    if query.fwd_from:
        return
    input_str = query.pattern_match.group(1)
    start = datetime.now()
    if query.reply_to_msg_id:
        previous_message = await query.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await query.edit("Invalid Syntax. Module stopping.")
        return
    text = text.strip()
    lan = lan.strip()
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    required_file_name = TEMP_DOWNLOAD_DIRECTORY + "voice.ogg"
    try:
        #https://github.com/SpEcHiDe/UniBorg/commit/17f8682d5d2df7f3921f50271b5b6722c80f4106
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        command_to_execute = [
            "ffmpeg",
            "-i",
             required_file_name,
             "-map",
             "0:a",
             "-codec:a",
             "libopus",
             "-b:a",
             "100k",
             "-vbr",
             "on",
             required_file_name + ".opus"
        ]
        try:
            t_response = subprocess.check_output(command_to_execute, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            await query.edit(str(exc))
            # continue sending required_file_name
        else:
            os.remove(required_file_name)
            required_file_name = required_file_name + ".opus"
        end = datetime.now()
        ms = (end - start).seconds
        await bot.send_file(
            query.chat_id,
            required_file_name,
            # caption="Processed {} ({}) in {} seconds!".format(text[0:97], lan, ms),
            reply_to=query.message.reply_to_msg_id,
            allow_cache=False,
            voice_note=True
        )
        os.remove(required_file_name)
        await query.edit("Processed {} ({}) in {} seconds!".format(text[0:97], lan, ms))
        await asyncio.sleep(5)
        await query.delete()
    except Exception as e:
        await query.edit(str(e))



@register(outgoing=True, pattern=r"^.trt(?: |$)([\s\S]*)")
async def translateme(trans):
    """ For .trt command, translate the given text using Google Translate. """
    translator = Translator()
    textx = await trans.get_reply_message()
    message = trans.pattern_match.group(1)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await trans.edit("`Give a text or reply to a message to translate!`")
        return

    try:
        reply_text = translator.translate(deEmojify(message), dest=TRT_LANG)
    except ValueError:
        await trans.edit("Invalid destination language.")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    reply_text = f"From **{source_lan.title()}**\nTo **{transl_lan.title()}:**\n\n{reply_text.text}"

    await trans.edit(reply_text)
    if BOTLOG:
        await trans.client.send_message(
            BOTLOG_CHATID,
            f"Translated some {source_lan.title()} stuff to {transl_lan.title()} just now.",
        )

@register(outgoing=True, pattern="^.tr(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    if "trim" in event.raw_text:
        # https://t.me/c/1220993104/192075
        return
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.edit("`.tr LanguageCode` as reply to a message")
        return
    text = emoji.demojize(text.strip())
    lan = lan.strip()
    translator = Translator()
    try:
        translated = translator.translate(text, dest=lan)
        after_tr_text = translated.text
        # TODO: emojify the :
        # either here, or before translation
        output_str = """**TRANSLATED** from {} to {}
{}""".format(
            translated.src,
            lan,
            after_tr_text
        )
        await event.edit(output_str)
    except Exception as exc:
        await event.edit(str(exc))


@register(pattern=".lang (trt|tts) (.*)", outgoing=True)
async def lang(value):
    """ For .lang command, change the default langauge of userbot scrapers. """
    util = value.pattern_match.group(1).lower()
    if util == "trt":
        scraper = "Translator"
        global TRT_LANG
        arg = value.pattern_match.group(2).lower()
        if arg in LANGUAGES:
            TRT_LANG = arg
            LANG = LANGUAGES[arg]
        else:
            await value.edit(
                f"`Invalid Language code !!`\n`Available language codes for TRT`:\n\n`{LANGUAGES}`"
            )
            return
    elif util == "tts":
        scraper = "Text to Speech"
        global TTS_LANG
        arg = value.pattern_match.group(2).lower()
        if arg in tts_langs():
            TTS_LANG = arg
            LANG = tts_langs()[arg]
        else:
            await value.edit(
                f"`Invalid Language code !!`\n`Available language codes for TTS`:\n\n`{tts_langs()}`"
            )
            return
    await value.edit(f"`Language for {scraper} changed to {LANG.title()}.`")
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID,
            f"`Language for {scraper} changed to {LANG.title()}.`")

@register(outgoing=True, pattern="^.yt (.*)")
async def yt_search(video_q):
    """ For .yt command, do a YouTube search from Telegram. """
    query = video_q.pattern_match.group(1)
    result = ''

    if not YOUTUBE_API_KEY:
        await video_q.edit(
            "`Error: YouTube API key missing! Add it to environment vars or config.env.`"
        )
        return

    await video_q.edit("```Processing...```")

    full_response = await youtube_search(query)
    videos_json = full_response[1]

    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        result += f"{title}\n{link}\n\n"

    reply_text = f"**Search Query:**\n`{query}`\n\n**Results:**\n\n{result}"

    await video_q.edit(reply_text)


async def youtube_search(query,
                         order="relevance",
                         token=None,
                         location=None,
                         location_radius=None):
    """ Do a YouTube search. """
    youtube = build('youtube',
                    'v3',
                    developerKey=YOUTUBE_API_KEY,
                    cache_discovery=False)
    search_response = youtube.search().list(
        q=query,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",
        maxResults=10,
        location=location,
        locationRadius=location_radius).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "KeyError, try again."
        return (nexttok, videos)


@register(outgoing=True, pattern=r".rip(audio|video) (.*)")
async def download_video(v_url):
    """ For .rip command, download media from YouTube and many other sites. """
    url = v_url.pattern_match.group(2)
    type = v_url.pattern_match.group(1).lower()

    await v_url.edit("`Preparing to download...`")

    if type == "audio":
        opts = {
            'format':
            'bestaudio',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'writethumbnail':
            True,
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl':
            '%(id)s.mp3',
            'quiet':
            True,
            'logtostderr':
            False
        }
        video = False
        song = True

    elif type == "video":
        opts = {
            'format':
            'best',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
            '%(id)s.mp4',
            'logtostderr':
            False,
            'quiet':
            True
        }
        song = False
        video = True

    try:
        await v_url.edit("`Fetching data, please wait..`")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        return await v_url.edit(f"`{str(DE)}`")
    except ContentTooShortError:
        return await v_url.edit("`The download content was too short.`")
    except GeoRestrictedError:
        return await v_url.edit(
            "`Video is not available from your geographic location "
            "due to geographic restrictions imposed by a website.`"
        )
    except MaxDownloadsReached:
        return await v_url.edit("`Max-downloads limit has been reached.`")
    except PostProcessingError:
        return await v_url.edit("`There was an error during post processing.`")
    except UnavailableVideoError:
        return await v_url.edit("`Media is not available in the requested format.`")
    except XAttrMetadataError as XAME:
        return await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        return await v_url.edit("`There was an error during info extraction.`")
    except Exception as e:
        return await v_url.edit(f"{str(type(e)): {str(e)}}")
    c_time = time.time()
    if song:
        await v_url.edit(
            f"`Preparing to upload song:`\n**{rip_data['title']}**")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp3",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(duration=int(rip_data['duration']),
                                       title=str(rip_data['title']),
                                       performer=str(rip_data['uploader']))
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{rip_data['title']}.mp3")))
        os.remove(f"{rip_data['id']}.mp3")
        await v_url.delete()
    elif video:
        await v_url.edit(
            f"`Preparing to upload video:`\n**{rip_data['title']}**")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp4",
            supports_streaming=True,
            caption=rip_data['title'],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Uploading..",
                         f"{rip_data['title']}.mp4")))
        os.remove(f"{rip_data['id']}.mp4")
        await v_url.delete()


def deEmojify(inputString):
    """ Remove emojis and other non-safe characters from string """
    return get_emoji_regexp().sub(u'', inputString)


CMD_HELP.update({
    'img':
    '.img <search_query>\
        \nUsage: Does an image search on Google and shows 5 images.'
})
CMD_HELP.update({
    'currency':
    '.currency <amount> <from> <to>\
        \nUsage: Converts various currencies for you.'
})
CMD_HELP.update({
    'carbon':
    '.carbon <text> [or reply]\
        \nUsage: Beautify your code using carbon.now.sh\nUse .crblang <text> to set language for your code.'
})
CMD_HELP.update(
    {'google': '.google <query>\
        \nUsage: Does a search on Google.also google1.'})
CMD_HELP.update(
    {'wiki': '.wiki <query>\
        \nUsage: Does a search on Wikipedia.'})
CMD_HELP.update(
    {'ud': '.ud <query>\
        \nUsage: Does a search on Urban Dictionary.'})
CMD_HELP.update({
    'tts':
    '.tts <text> [or reply]\
        \nUsage: Translates text to speech for the language which is set.\nUse .lang tts <language code> to set language for tts. (Default is English.).New one is tts1.'
})
CMD_HELP.update({
    'trt':
    '.trt <text> [or reply]\
        \nUsage: Translates text to the language which is set.\nUse .lang trt <language code> to set language for trt. (Default is English).also tr.'
})
CMD_HELP.update({'yt': '.yt <text>\
        \nUsage: Does a YouTube search.'})
CMD_HELP.update(
    {"imdb": ".imdb <movie-name>\nShows movie info and other stuff."})
CMD_HELP.update({
    'rip':
    '.ripaudio <url> or ripvideo <url>\
        \nUsage: Download videos and songs from YouTube (and [many other sites](https://ytdl-org.github.io/youtube-dl/supportedsites.html)).'
})
