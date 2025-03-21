


import os
try:
    import uuid
    from bidi.algorithm import get_display
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    import secrets
    import arabic_reshaper
    import base64
    from concurrent.futures import ThreadPoolExecutor
    import subprocess
    import sys
    import tempfile
    import importlib
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    import urllib.request as url
    import requests
    import threading
    import datetime
    import pytz
    import argparse
    import json
    import locale
    import threading
    import re
    import shlex
    import random
    import string
    from collections import OrderedDict
    from urllib.parse import unquote, urlparse
    import pyperclip
    from rich.console import Console
    from rich.syntax import Syntax
    from PIL import Image
    from fake_useragent import UserAgent
    from colorama import init, Fore, Back, Style
    from asciimatics.renderers import ImageFile
    import dotenv
except:
    os.system("pip install argparse")
    os.system("pip install datetime")
    os.system("pip install pytz")
    os.system("pip install json")
    os.system("pip install locale")
    os.system("pip install re")
    os.system("pip install shlex")
    os.system("pip install collections")
    os.system("pip install urllib")
    os.system("pip install pyperclip")
    os.system("pip install rich")
    os.system("pip install Pillow")
    os.system("pip install OneClick")
    os.system("pip install fake-useragent")
    os.system("pip install halo")
    os.system("pip install python-cfonts")
    os.system("pip install pyTelegramBotAPI")
    os.system("pip install colorama")
    os.system("pip install requests")
    os.system("pip install threading")
    os.system("pip install random")
    os.system("pip install time")
    os.system("pip install asciimatics")
    os.system("pip install base64")
    os.system("pip install arabic-reshaper")
    os.system("pip install python-bidi")
    os.system("pip install dotenv")
    os.system("pip install threading")


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #



#لوكو
def logo():
    o = "\u001b[38;5;208m"  # برتقالي
    e = "\u001b[38;5;242m"  # رمادي داكن
    logo=f"""
\033[1;97m        
\u001b[38;5;242m
    
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣦⣤⣤⣀⡀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄⡀⠀        
            ⠀⠀⠀⠀⣠⣾⣿⡿⠟⠛⠉⠁⠀⠀⡀⠀⠀⢀⡈⠉⠛⠻⠿⣿⣿⣿⣦⣉⣽⣿⣿⣿⣿⣿⣿⣆        
            ⠀⠀⠀⣼⣿⠟⠁⢀⣠⠔⢀⣴⡾⠋⣠⣾⣿⣿⣿⣿⣿⣶⣄⠀⠙⠛⠿⠿⠿⠟⠛⠛⢿⣿⣿⠛        
            ⠀⠀⣼⡟⠁⢀⣴⣿⠃⢰⣿⣿⡇⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⣀⣀⣀⠀⠀⢀⡾⡿⠏⠀        
            ⠀⠀⡿⠀⣰⣿⣿⡏⠀⢸⣿⣿⣇⠀⠹⣿⣿⣿⣿⣿⣿⣿⡏⢿⣿⣏⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀        
            ⠀⢸⠃⢰⣿⣿⣿⣿⡀⠘⢿⣿⣿⣧⣀⠀⠙⠿⣿⣿⣿⣿⡇⠈⢻⣿⣇⢀⣄⡄⠀⠀⠀⠀⠀⠀        
            ⠀⠈⠀⢸⣿⣿⣿⣿⣷⣄⠈⠻⢿⣿⣿⣷⣦⣀⠈⠙⢿⣿⣿⡄⠀⠙⠻⠿⠿⠁⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣷⣄⠀⠙⠻⢿⣿⣿⣿⣦⡀⠹⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀            
            ⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣦⣄⠀⠙⠻⣿⣿⣿⢀⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⠀⠙⣿⣾⣿⣿⣿⡿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠈⢿⣿⣿⣿⣿⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⣿⣿⣿⣿⣿⣿⣷⠘⣿⣿⣿⣿⡿⣿⣇⠀⠀⠀⠀⠀⠀⠀            
            ⠀⠀⠀⠀⠀⠀⠀ ⠀ ⠀⠀⠀{o}⣶⣶{e}⠀⠈⠙⠿⣿⣿⣿⡿⣸⣿⣿⣿⣿⣿⣶⣍⡀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  {o}⣶⣿⣿⣶{e}⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⢿⡇⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⣀⣀⠀⠀⢀⣀⡀⠉⣉⣉⠉⣀⣀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣷⣦⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⣿⣿⠀⠀⢸⣿⡇⠐⣿⣿⠀⣿⣿⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣝⠏⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⣿⣿⣶⣶⣾⣿⣷⣾⣿⣿⣶⣿⣿⠀⠀⠀⠀⠀⢠⠀⢻⣿⣿⣿⡿⣿⠇⠀⠀⠀⠀⠀⠀        
            ⠀⢀⣀⣿⣿⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⢀⣿⡇⢸⣿⣿⣿⣷⠌⠀⠀⠀⠀⠀⠀⠀        
            ⢠⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⡇⢸⣿⣿⡯⠁⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⢁⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠙⠲⣤⣤⣀⣀⣀⣀⣀⣠⣤⣴⣾⣿⣿⣿⣿⣿⠃⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        
            ⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⠿⠿⠿⠿⠿⠿⠟⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        
              
"""
    
    text2 = 50 * "_"
    terminal_size = os.get_terminal_size()
    max_width = terminal_size.columns - 1
    padding_width2 = (max_width - len(text2)) // 2
    centered_text2 = " " * padding_width2 + text2 + " " * padding_width2
    
    init(autoreset=True)
    custom_color = "\u001b[38;5;208m"
    
    def center_text(text):
        terminal_width = os.get_terminal_size().columns
        padding = (terminal_width - len(text)) // 2
        print(" " * padding, end='')
        for char in text:
            print(custom_color + Back.BLACK + Style.BRIGHT + char, end='', flush=True)
            time.sleep(0.02)

    print(logo)
    center_text("↝ Tele: b_azok | Insta: b_azok | tik: zquy ↜ ")
    print()
    print("\u001b[38;5;242m" + centered_text2)
    print("\u001b[38;5;15m")
    print(e)



#- - - - - - - - - - - - - - -- - - - - - -- - - - - #



#مهم
def love():
    print("- I love Mariam")





#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#دالة تلاشي النص
def tl(text=None, timg=None, center=None):
    if timg is None or center is None or text is None:
        raise ValueError("الرجاء تقديم نص ووقت وقيمة منطقية (True/False)")
    def b_azok_print(text):
        i = 232
        while i <= 255:
            b = f"\u001b[38;5;{i}m"
            p = '\x1b[1m'
            terminal_size = os.get_terminal_size()
            max_width = terminal_size.columns - 1
            if center:
                padding_width = (max_width - len(text)) // 2
                centered_text = " " * padding_width + text + " " * padding_width
            else:
                centered_text = text
            print(p + b + centered_text, end='\r')
            time.sleep(timg)
            i += 1
    b_azok_print(text)



#pazok.tl("hello",0.02,True)


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#انشاء يوزرات

def user_ran(pattern=None):
    pattern = str(pattern)  
    username = ''
    last_pazoo_2 = '' 
    for char in pattern:
        if char == '1':
            random_char = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            username += random_char
        elif char == '2':
            if not last_pazoo_2:
                last_pazoo_2 = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            username += last_pazoo_2
        elif char == '3':
            b_az_rand = random.choice(['.', '_'])
            username += b_az_rand
        elif char == '4':
            random_digit = random.choice('0123456789')
            username += random_digit
        elif char == '5':
            random_lower_char = random.choice('abcdefghijklmnopqrstuvwxyz')
            username += random_lower_char
        else:
            username += char
    return username.strip()

    
    
#jj=pazok.user_ran("111_1")
#print(jj)
                                
                                
#- - - - - - - - - - - - - - - - - - - - -- - - - - #

def voice2text(file_path, lang_type = None):
    """
    func for convert voice any type to text 

    support arabic and english voice

    => return text

    lang_type= ar-SA 
    lang_type= en-US

    => usgse
    if you know the voice lang
        voice2text("my_voice_file_name", lang_type = "ar-SA ")

    if you know the voice lang  
        voice2text("my_voice_file_name")
    
    => return text
    """
    from dotenv import load_dotenv
    api = "http://108.181.171.179:5000/convert"
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"language": lang_type} if lang_type else None
            response = requests.post(api, files=files, data=data)
        return response.json()
    except Exception as e:
        return {"error": e}
#- - - - - - - - - - - - - - - - - - - - -- - - - - #
                                


#- - - - - - - - - - - - - - - - - - - - -- - - - - #

# دالة الخيوط
        
def sb(func, num_threads):
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(func) for _ in range(num_threads)]
        for future in futures:
            future.result()



#def txt():
    

#pazok.sb(اسم الداله, عدد الخيوط)


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#ارسال تلي حديث

def html_tx(md_text):
    md_text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', md_text)
    md_text = re.sub(r'_(.*?)_', r'<i>\1</i>', md_text)
    md_text = re.sub(r'~(.*?)~', r'<u>\1</u>', md_text)
    md_text = re.sub(r'-(.*?)-', r'<s>\1</s>', md_text)
    md_text = re.sub(r'`(.*?)`', r'<code>\1</code>', md_text)
    md_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', md_text)
    return md_text


def tele_ms(token, id, txt=None, file=None, img=None, buttons=None):
    if not token or not id or txt is None:
        raise ValueError("يرجى اضافة توكن وايدي ونص على الاقل")

    bot = telebot.TeleBot(token)
    keyboard = InlineKeyboardMarkup()

    if buttons:
        for i in range(0, len(buttons), 2):
            button_name = buttons[i]
            button_url = buttons[i + 1]
            button = InlineKeyboardButton(button_name, url=button_url)
            keyboard.add(button)

    def download_file_from_url(url):
        file_name = url.split('/')[-1]
        response = requests.get(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name

    if txt:
        txt = html_tx(txt)

    if file or img:
        if img:
            if img.startswith('http'):
                bot.send_photo(id, photo=img, caption=txt, parse_mode='HTML', reply_markup=keyboard)
            else:
                bot.send_photo(id, open(img, 'rb'), caption=txt, parse_mode='HTML', reply_markup=keyboard)
        
        if file:
            if file.startswith('http'):
                file_path = download_file_from_url(file)
                bot.send_document(id, open(file_path, 'rb'), caption=txt, parse_mode='HTML', reply_markup=keyboard)
                os.remove(file_path)
            else:
                bot.send_document(id, open(file, 'rb'), caption=txt, parse_mode='HTML', reply_markup=keyboard)

    elif txt:
        bot.send_message(id, txt, parse_mode='HTML', reply_markup=keyboard)


#توكن
#token=""
#ايدي
#id=""

#يستقبل جميع تنسيقات النص
#msg="hello"

#يستقبل رابط او مسار للملف
#fil=""

#يستقبل رابط او مسار للصوره
#imgs=""

#ازرار يستقبل مفرد وقائمة ازرار
#buttons="name button","URL button"

#لا تستقبل ارسال صوره وملف بنفس الوقت
#pazok.tele_ms(token,id,txt=msg,img=imgs,buttons=button)


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#دالة طلب توكن وايدي مره وحده

def info_bot():
    try:
        import time, os
        from colorama import init, Fore, Back, Style
        from cfonts import render
    except ImportError:
        os.system('pip install colorama')
        os.system('pip install cfonts')

    b = "\u001b[38;5;14m"  # سمائي
    m = "\u001b[38;5;15m"  # ابيض
    F = '\033[2;32m'  # أخضر
    Z = '\033[1;31m'  # أحمر
    ee = "\033[0;90m"  # رمادي الداكن
    C = "\033[1;97m"  # أبيض
    p = '\x1b[1m'  # عريض
    X = '\033[1;33m'  # أصفر
    B = '\033[2;36m'  # أزرق
    E = "\u001b[38;5;8m"  # رمادي فاتح
    o = "\u001b[38;5;208m"  # برتقالي
    p = '\x1b[1m'  # عريض

    sev_amg=f"""
        
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⣤⣤⣤⣼⣿⣿⣿⣿⣿⣿⣿⣧⣤⣤⣤⣤⣤⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡇⠀
        ⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡇⠀
        ⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡇⠀
        ⠀⢸⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡇⠀
        ⠀⢸⣿⣿⣿⣿⣿⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⡇⠀
        ⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
        ⠀⠀⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠁⠀
        
         
{E}             𝗜𝗙 𝗬𝗢𝗨 𝗧𝗬𝗣𝗘 𝗬, 𝗜𝗡𝗙𝗢 𝗦𝗔𝗩𝗘𝗗 𝗙𝗢𝗥 𝗡𝗘𝗫𝗧 𝗧𝗜𝗠𝗘

"""
    
    try:
        with open('.bot_info.txt', 'r') as file:
            lines = file.readlines()
            token = lines[0].strip()
            id = lines[1].strip()
    except FileNotFoundError:
        b_azokatext = """
\u001b[38;5;15m        
         ______   ___   __  _    ___  ____  
        |      | /   \ |  |/ ]  /  _]|    \ 
        |      ||     ||  ' /  /  [_ |  _  |
        |_|  |_||  O  ||    \ |    _]|  |  |
          |  |  |     ||     \|   [_ |  |  |
          |  |  |     ||  .  ||     ||  |  |
          |__|   \___/ |__|\_||_____||__|__|
          
                                                            
        """
        print(b_azokatext)
        token = input(f" - {b}Enter Token : {ee}")
        os.system('clear')

        
        b_azokatext ="""
\u001b[38;5;15m        
           _____ _           _     _____ _____  
          / ____| |         | |   |_   _|  __ \ 
         | |    | |__   __ _| |_    | | | |  | |
         | |    | '_ \ / _` | __|   | | | |  | |
         | |____| | | | (_| | |_   _| |_| |__| |
          \_____|_| |_|\__,_|\__| |_____|_____/ 
                                                
                                                
        
        """
        print(b_azokatext)
        id = input(f" - {b}Enter ID : {ee}")
        os.system('clear')

        print(sev_amg)
        save_data = input(f"{ee}-{o} 𝗗𝗢 𝗬𝗢𝗨 𝗪𝗜𝗦𝗛 𝗧𝗢 𝗦𝗔𝗩𝗘 𝗥𝗘𝗚𝗜𝗦𝗧𝗥𝗔𝗧𝗜𝗢𝗡 𝗜𝗡𝗙𝗢   {E} ({F}Y{ee}/{Z}N{E}){o}:{ee} ")
        if save_data.upper() == "Y":
            os.system('clear')
            with open('.bot_info.txt', 'w') as file:
                file.write(f"{token}\n{id}")
        elif save_data.upper() == "N":
            os.system('clear')
            pass
        else:
            exit(f"{Z}Invalid input. Please enter 'Y' or 'N'.")

    return token, id



#token, id = pazok.info_bot()


#حذف بيانات بوت
def info_bot_dlet():
    start_path = '/storage/emulated/0'
    for dirpath, dirnames, filenames in os.walk(start_path):
        if '.bot_info.txt' in filenames:
            file_path = os.path.join(dirpath, '.bot_info.txt')
            os.remove(file_path)
            
#pazok.info_bot_dlet()



#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#الطباعه مع اشكال مكتبة rich

import time
from rich.console import Console

def pazok_rich(text, spinner, duration):
    console = Console()
    spinner_instance = console.status(text, spinner=spinner)
    spinner_instance.start()
    time.sleep(duration)
    spinner_instance.stop()

#pazok.pazok_rich("النص المطلوب", "النمط", الوقت)


#اسماء الانماط
def name_rich():
    rich_list = [
        "arrow",
        "christmas",
        "circle",
        "clock",
        "hearts",
        "moon",
        "pong",
        "runner",
        "star",
        "weather"
    ]

    for index, pattern in enumerate(rich_list, start=1):
        print(f"{index}. {pattern}")
        
#print(pazok.name_rich())

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#الطباعه مع اشكال مكتبة halo

from halo import Halo
import time


def pazok_halo(text, spinner, duration):
    spinner_instance = Halo(text=text, spinner=spinner)
    spinner_instance.start()
    time.sleep(duration)
    spinner_instance.stop_and_persist(symbol='', text='')
    print(' ' * len(text), end='\r')
    return None

#pazok.pazok_halo("النص المطلوب", "النمط", الوقت)


#اسماء الانماط
def name_halo():
    halo_list = [
        "dots",
        "dots2",
        "dots3",
        "dots4",
        "dots5",
        "dots6",
        "dots7",
        "dots8",
        "dots9",
        "dots10",
        "dots11",
        "dots12",
        "line",
        "line2",
        "pipe",
        "simpleDots",
        "simpleDotsScrolling",
        "star",
        "star2",
        "flip",
        "hamburger",
        "growVertical",
        "growHorizontal",
        "balloon",
        "balloon2",
        "noise",
        "bounce",
        "boxBounce",
        "boxBounce2",
        "triangle",
        "arc",
        "circle",
        "square",
        "circleQuarters",
        "circleHalves",
        "squish",
        "toggle",
        "toggle2",
        "toggle3",
        "toggle4",
        "toggle5",
        "toggle6",
        "toggle7",
        "toggle8",
        "toggle9",
        "toggle10",
        "toggle11",
        "toggle12",
        "toggle13",
        "arrow",
        "arrow2",
        "arrow3",
        "bouncingBar",
        "bouncingBall",
        "smiley",
        "monkey",
        "hearts",
        "clock",
        "earth",
        "moon",
        "runner",
        "pong",
        "shark",
        "dqpb"
    ]

    for index, pattern in enumerate(halo_list, start=1):
        print(f"{index}. {pattern}")

#print(pazok.name_halo())


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#تخويل الصور الى نقاط

def picture(image_path, height=None, style=None):
    
    from PIL import Image, ImageOps
    from picharsso import new_drawer
    from asciimatics.renderers import ImageFile
    import io
    
    try:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        inverted_image = ImageOps.invert(image)
        
        if style == 1:
            drawer = new_drawer("braille", height=height)
            return drawer(inverted_image)
        
        elif style == 2:
            with io.BytesIO() as output:
                inverted_image.save(output, format="PNG")
                output.seek(0)
                renderer = ImageFile(output, height=height)
                ascii_art = str(renderer)
            return ascii_art    
        else:
            raise ValueError("النمط غير مدعوم. يرجى اختيار 1 أو 2.")   
    except FileNotFoundError:
        print("المسار غير صحيح:", image_path)
    except Exception as e:
        print("حدث خطأ:", e)


#x="/storage/emulated/0/DCIM/100PINT/المنشورات/dbb76dbc7436ebe6defa7cd206103780.jpg"
#z=30

#jj=pazok.picture(x,z)
#print(jj)


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#التحديث:

#يوزر ايجنت

def agnt():
    from fake_useragent import UserAgent
    ua = UserAgent()
    return str(ua.chrome)

#pazok.agnt()

#يوزر ايجنت انستا
def agnt_in():
    from OneClick import Hunter
    agent = Hunter.Services()
    return str(agent)


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#اللوان
colors = ['o', 'b', 'm', 'F', 'Z', 'e', 'C', 'p', 'X', 'j', 'E']
o = "\u001b[38;5;208m" 
b = "\u001b[38;5;14m"
m = "\u001b[38;5;15m"
F = '\033[2;32m'
Z = '\033[1;31m'
e = "\033[0;90m"
C = "\033[1;97m"
p = '\x1b[1m'
X = '\033[1;33m'
j= "\u001b[38;5;200m" 
E = "\u001b[38;5;8m"
__all__ = colors

#طباعة اسماء الاللوان
def name_clo():
    colors_text = """
    
o = برتقالي
b = أزرق
m = أبيض
F = أخضر غامق
Z = أحمر فاتح
e = رمادي غامق
C = أبيض قوي
p = خط عريض
X = أصفر
j = وردي
E = رمادي فاتح

"""
    return colors_text





#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#سليب
def sleep(seconds=None):
    import random
    if seconds is None:
        seconds = random.uniform(0.5, 1)
    time.sleep(seconds)
    return seconds

#pazok.sleep()


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#يوزرات من ملف


def user_file(file_name, tr_fa_paz):
    if not file_name:
        raise ValueError("يرجى تمرير اسم الملف أو مساره")
    
    file_path = os.path.join(os.getcwd(), file_name)
    try:
        if not os.path.exists(file_path):
            return "no file"

        if os.path.getsize(file_path) == 0:
            return 0
                
        with open(file_path, 'r+') as file:
            data = file.readlines()
            if not data:
                return 0  # تأكيد إضافي في حالة وجود سطور ولكنها فارغة

            first_line = data[0].strip()
            username = first_line  # الإبقاء على الدومين بدون تعديلات

            if tr_fa_paz:
                data = data[1:]
            else:
                data = data[1:]
                data.append(first_line + '\n')
            data = [line for line in data if line.strip()]

            file.seek(0)
            file.writelines(data)
            file.truncate()
            
            return username
    except Exception as e:
        print("حدث خطأ: ", e)
        return None
        

#pazok.user_file('bazok.txt', True)



#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#طباعة عدد سطور اللسته
def file_np(file_path):
    if not file_path:
        raise ValueError("يرجى تمرير اسم الملف او مساره")
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return len(lines)
    except FileNotFoundError:
        print("الملف غير موجود")
        return 0

#print(pazok.file_np("user.py"))



#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#كوكيز انستا
class InstagramSession:    
    def __init__(self, csrftoken, ds_user_id, rur, sessionid):
        self.csrftoken = csrftoken
        self.ds_user_id = ds_user_id
        self.rur = rur
        self.sessionid = sessionid

def log_in(username, password):
    if not username or not password:
        raise ValueError("يرجى تمرير قيم لاسم المستخدم وكلمة المرور")
        
    import requests
    from fake_useragent import UserAgent

    ua = UserAgent()
    agnt = str(ua.getChrome)

    url = 'https://www.instagram.com/accounts/login/ajax/'

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
        'content-length': '275',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'csrftoken=DqBQgbH1p7xEAaettRA0nmApvVJTi1mR; ig_did=C3F0FA00-E82D-41C4-99E9-19345C41EEF2; mid=X8DW0gALAAEmlgpqxmIc4sSTEXE3; ig_nrcb=1',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': agnt,
        'x-csrftoken': 'DqBQgbH1p7xEAaettRA0nmApvVJTi1mR',
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': '0',
        'x-instagram-ajax': 'bc3d5af829ea',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:1589682409:{password}',
        'queryParams': '{}',
        'optIntoOneTap': 'false'
    }

    response = requests.post(url, headers=headers, data=data)
    cookies = None
    if response.status_code == 200:
        cookies = response.cookies.get_dict()
        csrftoken = cookies.get("csrftoken")
        ds_user_id = cookies.get("ds_user_id")
        rur = cookies.get("rur")
        sessionid = cookies.get("sessionid")
        return InstagramSession(csrftoken, ds_user_id, rur, sessionid)
    else:
        return None

#username = "jdjdjuuuudjjdk"
#password = "mmkkoopp"

#jj=pazok.log_in(username, password)
#print(jj.sessionid)
#print(jj.csrftoken)
#print(jj.rur)
#print(jj.ds_user_id)

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#تحويل الاستجابه الى جيسون

import json
def json_req(data, indent=0):
    formatted_string = ""
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_string += ' ' * indent + f"{key}:\n"
            formatted_string += json_req(value, indent + 2)
        else:
            formatted_string += ' ' * indent + f"{key}: {value}\n"
    return formatted_string



#print(pazok.json_req(rr))

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#تحويل امرcURL الى طلب

import argparse
import json
import locale
import re
import shlex
from collections import OrderedDict
from urllib.parse import unquote, urlparse
import pyperclip
from rich.console import Console
from rich.syntax import Syntax


def prettier_print(code: str):
    from os import get_terminal_size
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console = Console()
    console_width = int((get_terminal_size()[0] - 36) / 2)
    console.print("=" * console_width +
                  "[bold magenta] Python Requests Code Preview Start [/]" +
                  "=" * console_width,
                  justify='center')
    console.print(syntax)
    console.print("=" * console_width +
                  "[bold magenta]  Python Requests Code Preview End  [/]" +
                  "=" * console_width,
                  justify='center')


def parse_content_type(content_type: str):
    parts = content_type.split(';', 1)
    tuparts = parts[0].split('/', 1)
    if len(tuparts) != 2:
        return None
    dparts = OrderedDict()
    if len(parts) == 2:
        for i in parts[1].split(";"):
            c = i.split("=", 1)
            if len(c) == 2:
                dparts[c[0].strip()] = c[1].strip()
    return tuparts[0].lower(), tuparts[1].lower(), dparts


def format_multi(the_multi_list, indent=4):
    return 'MultipartEncoder(\n' + " " * indent + 'fields=[\n' + " " * indent * 2 + (
        ",\n" + " " * indent * 2).join(map(str, the_multi_list)) + '\n])'


def parse_multi(content_type, the_data):
    boundary = b''
    if content_type:
        ct = parse_content_type(content_type)
        if not ct:
            return [('no content-type')]
        try:
            boundary = ct[2]["boundary"].encode("ascii")
        except (KeyError, UnicodeError):
            return [('no boundary')]
    if boundary:
        result = []
        for i in the_data.split(b"--" + boundary):
            p = i.replace(b'\\x0d', b'\r')
            p = p.replace(b'\\x0a', b'\n')
            p = p.replace(b'\\n', b'\n')
            p = p.replace(b'\\r', b'\r')
            parts = p.splitlines()
            # print(parts)
            if len(parts) > 1 and parts[0][0:2] != b"--":
                if len(parts) > 4:
                    tmp_value = {}
                    key, tmp_value['filename'] = re.findall(
                        br'\bname="([^"]+)"[^"]*filename="([^"]*)"',
                        parts[1])[0]
                    tmp_value['content'] = b"".join(
                        parts[3 + parts[2:].index(b""):])
                    tmp_value['content_type'] = parts[2]
                    value = (tmp_value['filename'].decode(),
                             tmp_value['content'].decode(),
                             tmp_value['content_type'].decode())
                else:
                    key = re.findall(br'\bname="([^"]+)"', parts[1])[0]
                    value = (b"".join(parts[3 +
                                            parts[2:].index(b""):])).decode()
                result.append((key.decode(), value))
        return result


def parse_args(curl_cmd):
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('url')
    parser.add_argument('-d', '--data')
    parser.add_argument('-b', '--cookie', default=None)
    parser.add_argument('--data-binary',
                        '--data-raw',
                        '--data-ascii',
                        default=None)
    parser.add_argument('-X', default='')
    parser.add_argument('-F', '--form', default=None)
    parser.add_argument('-H', '--header', action='append', default=[])
    parser.add_argument('-A', '--user-agent', default='')
    parser.add_argument('--compressed', action='store_true')
    parser.add_argument('-k', '--insecure', action='store_true')
    parser.add_argument('-I', '--head', action='store_true')
    parser.add_argument('-G', '--get', action='store_true')
    parser.add_argument('--user', '-u', default=())
    parser.add_argument('-i', '--include', action='store_true')
    parser.add_argument('-s', '--silent', action='store_true')
    cmd_set = shlex.split(curl_cmd)
    arguments = parser.parse_args(cmd_set)
    return arguments


def prettier_dict(the_dict, indent=4):
    if not the_dict:
        return "{}"
    return ("\n" + " " * indent).join(
        json.dumps(the_dict,
                   ensure_ascii=False,
                   sort_keys=True,
                   indent=indent,
                   separators=(',', ': ')).splitlines())


def prettier_tuple(the_tuple, indent=4):
    if not the_tuple:
        return "()"
    return '(\n' + " " * indent + ("," + "\n" + " " * indent).join(
        str(i) for i in the_tuple) + ',\n)'


def quotestr(x):
    return f"'{x}'"


def prettier_dict_string(the_dict, indent=4):
    if not the_dict:
        return "{}"
    return '{\n' + " " * indent + ("," + "\n" + " " * indent).join(
        f"{quotestr(x) if isinstance(x,str) else str(x)}:{quotestr(y) if isinstance(y,str) else str(y)}"
        for x, y in the_dict.items()) + ',\n}'


def curl_replace(curl_cmd):
    curl_replace = [(r'\\\r|\\\n|\r|\n', ''), (' -XPOST', ' -X POST'),
                    (' -XGET', ' -X GET'), (' -XPUT', ' -X PUT'),
                    (' -XPATCH', ' -X PATCH'), (' -XDELETE', ' -X DELETE'),
                    (' -Xnull', ''), (' \$', ' ')]
    tmp_curl_cmd = curl_cmd
    for pattern in curl_replace:
        tmp_curl_cmd = re.sub(pattern[0], pattern[1], tmp_curl_cmd)
    return tmp_curl_cmd.strip()


class parseCurlCommand:
    def __init__(self, curl_cmd):
        self.curl_cmd = curl_replace(curl_cmd)
        self.arguments = parse_args(self.curl_cmd)
        self.method = 'get'
        post_data = self.arguments.data or self.arguments.data_binary
        self.urlparse = urlparse(self.arguments.url)
        self.url = "{}://{}{}".format(self.urlparse.scheme,
                                      self.urlparse.netloc, self.urlparse.path)
        self.cookies = None
        if self.urlparse.query:
            self.params = tuple(
                re.findall(r'([^=&]*)=([^&]*)', unquote(self.urlparse.query)))
        else:
            self.params = ()
        headers = self.arguments.header
        cookie_string = ''
        content_type = ''
        if headers:
            self.headers = dict(
                [tuple(header.split(': ', 1)) for header in headers])
            cookie_string = self.headers.get('cookie') or self.headers.get(
                'Cookie')
            if 'cookie' in self.headers:
                self.headers.pop('cookie')
            if 'Cookie' in self.headers:
                self.headers.pop('Cookie')
            self.content_type = self.headers.get(
                'Content-Type') or self.headers.get(
                    'content-type') or self.headers.get('Content-type')
        else:
            self.headers = {}
        if self.arguments.cookie:
            cookie_string = self.arguments.cookie
        if post_data and not self.arguments.get:
            self.method = 'post'
            if "multipart/form-data" in self.content_type.lower():
                self.data = parse_multi(
                    self.content_type,
                    unquote(post_data.strip('$')).encode('raw_unicode_escape'))
            elif "application/json" in self.content_type.lower():
                self.data = json.loads(post_data)
            else:
                self.data = dict(
                    re.findall(r'([^=&]*)=([^&]*)', unquote(post_data)))
        elif post_data:
            self.params = tuple(
                re.findall(r'([^=&]*)=([^&]*)', unquote(post_data)))
            self.data = {}
        else:
            self.data = {}
        if self.arguments.X:
            self.method = self.arguments.X.lower()
        if cookie_string:
            self.cookies = {}
            for cookie in re.findall(r'([^=\s;]*)=([^;]*)', cookie_string):
                if cookie[0] not in self.cookies:
                    self.cookies[cookie[0]] = cookie[1]
        if self.arguments.insecure:
            self.insecure = True
        else:
            self.insecure = False

def cURL(filestring, b_azok_path=''):
    curl_cmd = parseCurlCommand(filestring)

    b_azok = '#https://t.me/b_azok\nimport requests\n\n'
    req = ['response = requests.{}("{}"'.format(curl_cmd.method, curl_cmd.url)]
    if curl_cmd.params:
        b_azok += "params = {}\n\n".format(prettier_tuple(curl_cmd.params))
        req.append('params=params')
    if curl_cmd.data:
        if isinstance(curl_cmd.data, dict):
            if 'application/json' in curl_cmd.content_type:
                b_azok += "data = json.dumps({})\n\n".format(
                    prettier_dict_string(curl_cmd.data))
            else:
                b_azok += "data = {}\n\n".format(prettier_dict(curl_cmd.data))
        else:
            b_azok = 'from requests_toolbelt import MultipartEncoder\n' + b_azok
            b_azok += "data = {}\n\n".format(format_multi(curl_cmd.data))
        req.append('data=data')
    if curl_cmd.headers:
        b_azok += "headers = {}\n\n".format(prettier_dict(curl_cmd.headers))
        req.append('headers=headers')
    if curl_cmd.cookies:
        b_azok += "cookies = {}\n\n".format(prettier_dict(curl_cmd.cookies))
        req.append('cookies=cookies')
    if curl_cmd.insecure:
        req.append('verify=False')
    b_azok += ', '.join(req) + ').text\n\n'
    b_azok += 'print(response)\n\n'
    return b_azok

#pazok.cURL()

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#cook.mid,cook.csrftoken
#تحديث دالةcook

def cook():
    class b_azok:
        def __init__(self):
            self.cookies = {}
            ss = requests.Session()
            url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={user_ran(1111)}'
            headers = {
                'X-Ig-App-Id': f'{user_ran(15 * "4")}',
            }

            response = ss.get(url, headers=headers).text
            csrf_token = response.split('"csrf_token":"')[1].split('"')[0] if '"csrf_token":"' in response else None

            if csrf_token:
                self.cookies['csrftoken'] = csrf_token
            else:
                self.cookies['csrftoken'] = ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=32))

            mid_cookie = ss.get('https://i.instagram.com/api/v1/si/fetch_headers/?challenge_type=signup&guid=' + str(uuid.uuid4())).cookies.get('mid')

            if mid_cookie:
                self.cookies['mid'] = mid_cookie
            else:
                self.cookies['mid'] = ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=28))

        @property
        def csrftoken(self):
            return self.cookies.get('csrftoken')

        @property
        def mid(self):
            return self.cookies.get('mid')

    return b_azok()



    
#co=pazok.cook()
#co.mid
#co.csrftoken


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#اشتراك اجباري

#def tele_check(token, user_id):
#    url = f"https://api.telegram.org/6237316132:AAHS21d_LCO08FKkVFVUu0NMgr9qBU/getchatmember?chat_id=@b_azok&user_id={user_id}"
#    response = requests.get(url).text
#    if "member" in response or "creator" in response or "administrator" in response:
#        return "✅"
#    else:
#        
#        msssg="*• عذرًا يجب الاشتراك في قناة المطور*\n*• اضغط على الزر ⬇️*"
#        pi="قناة المطور", "https://t.me/b_azok"
#        tele_ms(token,user_id,txt=msssg,button=pi)
#        print(f"{p}\nيرجى التحقق من رسائل بوتك")
#    
#        sys.exit()  
#        
#tele_check(,token, 790448681)





#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#زخرفه

def motifs(text, style):
    if style == 1:
        lest_1 = [
            '𝗮', '𝗯', '𝗰', '𝗱', '𝗲', '𝗳', '𝗴', '𝗵', '𝗶', '𝗷', '𝗸', '𝗹', '𝗺', 
            '𝗻', '𝗼', '𝗽', '𝗾', '𝗿', '𝘀', '𝘁', '𝘂', '𝘃', '𝘄', '𝘅', '𝘆', '𝘇'
        ]
        lest_2 = [
            '𝗔', '𝗕', '𝗖', '𝗗', '𝗘', '𝗙', '𝗚', '𝗛', '𝗜', '𝗝', '𝗞', '𝗟', '𝗠', 
            '𝗡', '𝗢', '𝗣', '𝗤', '𝗥', '𝗦', '𝗧', '𝗨', '𝗩', '𝗪', '𝗫', '𝗬', '𝗭'
        ]
        num_paz = [
            '𝟬', '𝟭', '𝟮', '𝟯', '𝟰', '𝟱', '𝟲', '𝟳', '𝟴', '𝟵'
        ]
    elif style == 2:
        lest_1 = [
            '𝚊', '𝚋', '𝚌', '𝚍', '𝚎', '𝚏', '𝚐', '𝚑', '𝚒', '𝚓', '𝚔', '𝚕', '𝚖', 
            '𝚗', '𝚘', '𝚙', '𝚚', '𝚛', '𝚜', '𝚝', '𝚞', '𝚟', '𝚠', '𝚡', '𝚢', '𝚣'
        ]
        lest_2 = [
            '𝙰', '𝙱', '𝙲', '𝙳', '𝙴', '𝙵', '𝙶', '𝙷', '𝙸', '𝙹', '𝙺', '𝙻', '𝙼', 
            '𝙽', '𝙾', '𝙿', '𝚀', '𝚁', '𝚂', '𝚃', '𝚄', '𝚅', '𝚆', '𝚇', '𝚈', '𝚉'
        ]
        num_paz = [
            '𝟶', '𝟷', '𝟸', '𝟹', '𝟺', '𝟻', '𝟼', '𝟽', '𝟾', '𝟿'
        ]
    elif style == 3:
        lest_1 = [
            '𝐚', '𝐛', '𝐜', '𝐝', '𝐞', '𝐟', '𝐠', '𝐡', '𝐢', '𝐣', '𝐤', '𝐥', '𝐦', 
            '𝐧', '𝐨', '𝐩', '𝐪', '𝐫', '𝐬', '𝐭', '𝐮', '𝐯', '𝐰', '𝐱', '𝐲', '𝐳'
        ]
        lest_2 = [
            '𝐀', '𝐁', '𝐂', '𝐃', '𝐄', '𝐅', '𝐆', '𝐇', '𝐈', '𝐉', '𝐊', '𝐋', '𝐌', 
            '𝐍', '𝐎', '𝐏', '𝐐', '𝐑', '𝐒', '𝐓', '𝐔', '𝐕', '𝐖', '𝐗', '𝐘', '𝐙'
        ]
        num_paz = [
            '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗'
        ]
    elif style == 4:
        lest_1 = [
            'ᥲ', 'ხ', 'ᥴ', 'ძ', 'ᥱ', 'ƒ', 'ᘜ', 'ɦ', 'Ꭵ', '᧒', 'ƙ', 'ᥣ', 'ꪔ', 
            'ꪀ', '᥆', 'ρ', 'ᑫ', 'ᖇ', '᥉', 'ƚ', 'ᥙ', '᥎', '᭙', 'ꪎ', 'ᥡ', 'ᤁ'
        ]
        lest_2 = [
            'ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 
            'ɴ', 'ᴏ', 'ᴘ', 'ǫ', 'ʀ', 'ꜱ', 'ᴛ', 'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ'
        ]
        num_paz = [
            '𝟘', '𝟙', '𝟚', '𝟛', '𝟜', '𝟝', '𝟞', '𝟟', '𝟠', '𝟡'
        ]
        
        
    elif style == 5:
        lest_1=[
    'ᗩ', 'ᗷ', 'ᑕ', 'ᗪ', 'ᗴ', 'ᖴ', 'ᘜ', 'ᕼ', 'I', 'ᒍ', 'K', 'ᒪ', 'ᗰ', 
    'ᑎ', 'O', 'ᑭ', 'ᑫ', 'ᖇ', 'Տ', 'T', 'ᑌ', 'ᐯ', 'ᗯ', '᙭', 'Y', 'ᘔ'
        ]
        lest_2=lest_1
        num_paz=[
            '0','1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]
        
        
    elif style == 6:
        lest_1=[
    '𝖆', '𝖇', '𝖈', '𝖉', '𝖊', '𝖋', '𝖌', '𝖍', '𝖎', '𝖏', '𝖐', '𝖑', '𝖒', '𝖓', '𝖔', '𝖕', '𝖖', '𝖗', '𝖘', '𝖙', '𝖚', '𝖛', '𝖜', '𝖝', '𝖞', '𝖟'
]
        lest_2=[
    '𝕬', '𝕭', '𝕮', '𝕯', '𝕰', '𝕱', '𝕲', '𝕳', '𝕴', '𝕵', '𝕶', '𝕷', '𝕸', '𝕹', '𝕺', '𝕻', '𝕼', '𝕽', '𝕾', '𝕿', '𝖀', '𝖁', '𝖂', '𝖃', '𝖄', '𝖅'
]
        num_paz=[
            '0','1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]
        
    elif style == 7:
        lest_1=[
    '𝓪', '𝓫', '𝓬', '𝓭', '𝓮', '𝓯', '𝓰', '𝓱', '𝓲', '𝓳', '𝓴', '𝓵', '𝓶', 
    '𝓷', '𝓸', '𝓹', '𝓺', '𝓻', '𝓼', '𝓽', '𝓾', '𝓿', '𝔀', '𝔁', '𝔂', '𝔃'
]

        lest_2=[
    '𝓐', '𝓑', '𝓒', '𝓓', '𝓔', '𝓕', '𝓖', '𝓗', '𝓘', '𝓙', '𝓚', '𝓛', '𝓜', 
    '𝓝', '𝓞', '𝓟', '𝓠', '𝓡', '𝓢', '𝓣', '𝓤', '𝓥', '𝓦', '𝓧', '𝓨', '𝓩'
]

        num_paz=[
            '0','1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]
        
        
    elif style == 8:
        lest_1=[
    '𝕒', '𝕓', '𝕔', '𝕕', '𝕖', '𝕗', '𝕘', '𝕙', '𝕚', '𝕛', '𝕜', '𝕝', '𝕞', 
    '𝕟', '𝕠', '𝕡', '𝕢', '𝕣', '𝕤', '𝕥', '𝕦', '𝕧', '𝕨', '𝕩', '𝕪', '𝕫'
]
        lest_2=[
    '𝔸', '𝔹', 'ℂ', '𝔻', '𝔼', '𝔽', '𝔾', 'ℍ', '𝕀', '𝕁', '𝕂', '𝕃', '𝕄', 
    'ℕ', '𝕆', 'ℙ', 'ℚ', 'ℝ', '𝕊', '𝕋', '𝕌', '𝕍', '𝕎', '𝕏', 'Ý', 'ℤ'
]
        num_paz=[
        
    '𝟘', '𝟙', '𝟚', '𝟛', '𝟜', '𝟝', '𝟞', '𝟟', '𝟠', '𝟡'
]
        

        
    else:
        raise ValueError("يرجى تحديد نمط صحيح (1 أو 2 أو 3 أو 4)")

    text = str(text)
    result = []
    for char in text:
        if 'a' <= char <= 'z':
            index = ord(char) - ord('a')
            result.append(lest_1[index])
        elif 'A' <= char <= 'Z':
            index = ord(char) - ord('A')
            result.append(lest_2[index])
        elif '0' <= char <= '9':
            index = ord(char) - ord('0')
            result.append(num_paz[index])
        else:
            result.append(char)
    return ''.join(result)
    
    
    
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#معلومات الزخارف


def info_motifs():
    lest="""

 - 1 - 𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱 𝟭𝟮𝟯
 - 2 - 𝙷𝚎𝚕𝚕𝚘 𝚆𝚘𝚛𝚕𝚍 𝟷𝟸𝟹
 - 3 - 𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝 𝟏𝟐𝟑
 - 4 - ʜᥱᥣᥣ᥆ ᴡ᥆ᖇᥣძ 𝟙𝟚𝟛
 - 5 - ᕼᗴᒪᒪO ᗯOᖇᒪᗪ 123
 - 6 - 𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉 123
 - 7 - 𝓗𝓮𝓵𝓵𝓸 𝓦𝓸𝓻𝓵𝓭 123
 - 8 - ℍ𝕖𝕝𝕝𝕠 𝕎𝕠𝕣𝕝𝕕 𝟙𝟚𝟛
 
"""
    print(lest)
    
#    print(" - 1 - "+pazok.motifs("Hello World 123",1))
#    print(" - 2 - "+pazok.motifs("Hello World 123",2))
#    print(" - 3 - "+pazok.motifs("Hello World 123",3))
#    print(" - 4 - "+pazok.motifs("Hello World 123",4))
#    print(" - 5 - "+pazok.motifs("Hello World 123",5))
#    print(" - 6 - "+pazok.motifs("Hello World 123",6))
#    print(" - 7 - "+pazok.motifs("Hello World 123",7))
#    print(" - 8 - "+pazok.motifs("Hello World 123",8))
    
def Hussein():
    print("- I love Hussein 💗 ")

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#توقيت الادوات
def timeeg(snen, ashHr, ayam, sa3at=23, dqaeq=59, thoane=59):
    
    import requests
    from datetime import datetime
    import pytz
    
    response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Baghdad')
    data = response.json()
    datetime_str = data['datetime']
    baghdad_time = datetime.fromisoformat(datetime_str).replace(tzinfo=pytz.UTC)
    baghdad_tz = pytz.timezone('Asia/Baghdad')
    fixed_time = datetime(snen, ashHr, ayam, sa3at, dqaeq, thoane, tzinfo=baghdad_tz)
    return baghdad_time > fixed_time
#result = timeeg(2026,6,1)
#if result == True:
#    print("ننهت الصلاحيه")
#    exit()
#else:
#    pass

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
import requests
import uuid
import secrets
import re

class info_inst:
    def __init__(self, email):
        self.email = email
        self.username = None
        self.user_id = None
        self.name = None
        self.followers = None
        self.following = None
        self.bio = None
        self.img = None
        self.reset = None
        self.test_reset=None
        self.data = None
        self.fetch_info()

    def fetch_info(self):
        unid = uuid.uuid4()
        co = cook()
        cs = co.csrftoken
        mid = co.mid
        appid = user_ran(15 * "4")
        device_id = "android-" + secrets.token_hex(16 // 2)

        user = self.email.split("@")[0]

        # معلومات
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'mid={mid}; csrftoken={cs};',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': agnt(),
            'x-asbd-id': '198387',
            'x-csrftoken': cs,
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': 'hmac.AR0g7ECdkTdrXy37TE9AoSnMndccWbB1cqrccYOZSLfcb0pE',
            'x-instagram-ajax': '1006383249',
        }

        response = requests.get(
            f'https://www.instagram.com/api/v1/users/web_profile_info/?username={user}',
            headers=headers,
        ).json()

        self.username = response["data"]["user"]["username"]
        self.user_id = response["data"]["user"]["id"]
        self.name = response["data"]["user"]["full_name"]
        self.followers = response["data"]["user"]["edge_followed_by"]["count"]
        self.following = response["data"]["user"]["edge_follow"]["count"]
        self.bio = response["data"]["user"]["biography"]

        # صوره
        cookies = {'csrftoken': cs, 'mid': mid}
        headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'dpr': '2.19889',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/a_1_in/?igsh=czFtZ3o1aDhraG01',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-full-version-list': '"Not-A.Brand";v="99.0.0.0", "Chromium";v="124.0.6327.2"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Linux"',
            'sec-ch-ua-platform-version': '""',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': agnt(),
            'viewport-width': '891',
            'x-asbd-id': '129477',
            'x-csrftoken': cs,
            'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
            'x-fb-lsd': 'AVoRhvRPoRs',
            'x-ig-app-id': appid,
        }

        data = {
            'av': '0',
            '__d': 'www',
            '__user': '0',
            '__a': '1',
            '__req': '1',
            '__hs': '19820.HYP:instagram_web_pkg.2.1..0.0',
            'dpr': '2',
            '__ccg': 'UNKNOWN',
            '__rev': '1012604142',
            '__s': 'dmjo05:l5d6wo:20s0u7',
            '__hsi': '7355192092986103751',
            '__dyn': '7xeUjG1mxu1syUbFp40NonwgU29zEdF8aUco2qwJw5ux609vCwjE1xoswaq0yE7i0n24oaEd86a3a1YwBgao6C0Mo2swaO4U2zxe2GewGwso88cobEaU2eUlwhEe87q7U88138bpEbUGdwtU662O0Lo6-3u2WE5B0bK1Iwqo5q1IQp1yUoxe4UrAwCAxW6U',
            '__csr': 'gVb2snsIjkIQyjRmBaFGECih59Fb98nQBzbZ2IN8BqBGl7h9Am4ohAAD-vGBh4GizA-4aAiJ2vFDUR3qx596AhrBgzJlBKmu6VHiypryUkByrGiicgPAx6iUpGEOmqfykFA4801kXEkOwmU1Tqwvk8wCix64E0b_EaWdguwozat2F61-wiokxG0d9w2MFU5Kzo0k6wiU7Kut2F601_Ew1me',
            '__comet_req': '7',
            'lsd': 'AVoRhvRPoRs',
            'jazoest': '21036',
            '__spin_r': '1012604142',
            '__spin_b': 'trunk',
            '__spin_t': '1712514108',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'PolarisProfilePageContentQuery',
            'variables': f'{{"id":"{self.user_id}","relay_header":false,"render_surface":"PROFILE"}}',
            'server_timestamps': 'true',
            'doc_id': '7381344031985950',
        }

        response = requests.post(
            'https://www.instagram.com/api/graphql',
            cookies=cookies,
            headers=headers,
            data=data,
        ).json()
        try:
            self.img = response['data']['user']['hd_profile_pic_url_info']['url']
        except:
            self.img = "https://images.app.goo.gl/fRGBYvVcnrxWsS777"

        # ريست
        url = 'https://i.instagram.com/api/v1/accounts/send_password_reset/'
        head = {
            'Host': 'i.instagram.com',
            'Connection': 'Keep-Alive',
            'Cookie': f'mid={mid}; csrftoken={cs}',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-GB, en-US',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Capabilities': 'AQ==',
            'Accept-Encoding': 'gzip',
        }
        data = {
            "user_email": f"{user}",
            "device_id": f"{device_id}",
            "guid": f"{unid}",
            "_csrftoken": f"{cs}",
        }

        req = requests.post(url, headers=head, data=data).json()
        if "obfuscated_email" in req:
            self.reset = req['obfuscated_email']

        elif 'obfuscated_email' not in req:
            url = 'https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/'
            headers = {
                'X-Pigeon-Session-Id': '2b712457-ffad-4dba-9241-29ea2f472ac5',
                'X-Pigeon-Rawclienttime': '1707104597.347',
                'X-IG-Connection-Speed': '-1kbps',
                'X-IG-Bandwidth-Speed-KBPS': '-1.000',
                'X-IG-Bandwidth-TotalBytes-B': '0',
                'X-IG-Bandwidth-TotalTime-MS': '0',
                'X-IG-VP9-Capable': 'false',
                'X-Bloks-Version-Id': '009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
                'X-IG-Connection-Type': 'WIFI',
                'X-IG-Capabilities': '3brTvw==',
                'X-IG-App-ID': '567067343352427',
                'User-Agent': agnt_in(),
                'Accept-Language': 'ar-IQ, en-US',
                'Cookie': 'mid=Zbu4xQABAAE0k2Ok6rVxXpTD8PFQ; csrftoken=dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'i.instagram.com',
                'X-FB-HTTP-Engine': 'Liger',
                'Connection': 'keep-alive',
                'Content-Length': '364',
            }
            data = {
                'signed_body': 'ef02f559b04e8d7cbe15fb8cf18e2b48fb686dafd056b7c9298c08f3e2007d43.{"_csrftoken":"dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK","adid":"5e7df201-a1ff-45ec-8107-31b10944e25c","guid":"b0382b46-1663-43a7-ba90-3949c43fd808","device_id":"android-71a5d65f74b8fcbc","query":"'f'{user}''"}',
                'ig_sig_key_version': '4',
            }

            response = requests.post(url, headers=headers, data=data).json()
            if "email" in response:
                self.reset = response["email"]
            else:
                headers = {
                    'authority': 'www.instagram.com',
                    'accept': '*/*',
                    'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
                    'content-type': 'application/x-www-form-urlencoded',
                    'user-agent': agnt_in(),
                    'viewport-width': '384',
                    'x-asbd-id': '129477',
                    'x-csrftoken': cs,
                    'x-ig-app-id': user_ran(15 * "4"),
                    'x-ig-www-claim': '0',
                    'x-instagram-ajax': '1007832499',
                    'x-requested-with': 'XMLHttpRequest',
                }

                data = {
                    'email_or_username': f'{user}',
                    'flow': 'fxcal',
                    'recaptcha_challenge_field': '',
                }

                bzok = requests.post(
                    'https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/',
                    headers=headers,
                    data=data,
                ).json()
                restt = bzok["message"]
                pattern = r'\b\w+\*\*\*@\w+\.\w+\b'
                rosttt = re.search(pattern, restt)
                if rosttt:
                    self.reset = rosttt.group()
                else:
                    self.reset = "x***x"

        # فحص الريست
        try:
            email_parts = self.email.split('@')
            ree_parts = self.reset.split('@')
            if len(email_parts) == 2 and len(ree_parts) == 2:
                email_username, email_domain = email_parts
                ree_username, ree_domain = ree_parts
                ree_username = ree_username.replace('*', '')
                if email_username[0] == ree_username[0] and email_username[-1] == ree_username[-1] and email_domain == ree_domain:
                    self.test_reset = True
                else:
                    self.test_reset = False
        except:
            self.test_reset = "x***x"

        # تأريخ الانشاء
        try:
            url = f"https://o7aa.pythonanywhere.com/?id={self.user_id}"
            result = requests.get(url).json()
            self.data = result.get('date', '')
        except:
            try:
                self.data = requests.get(f'https://alany-2-41663a9bd041.herokuapp.com/?id={self.user_id}').json()['date']
            except:
                self.data = "xxxx"
              #oo=info_inst("user@gmail.com")
#print(oo.username)
#print(oo.user_id)
#print(oo.followers)
#print(oo.following)
#print(oo.bio)
#print(oo.data)
#print(oo.email)
#print(oo.reset)
#print(oo.test_reset)
#print(oo.img)
  
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #


#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#   تثبيت مكاتب  
import subprocess
import sys
import os
import tempfile
import importlib
import urllib.request as url
import json

def install(*pkgs):
    def _get_pip():
        fd, path = tempfile.mkstemp('_get-pip.py')
        url.urlretrieve("https://bootstrap.pypa.io/get-pip.py", path)
        subprocess.check_call([sys.executable, path])
        
    def _check_pip():
        try:
            with open(os.devnull, 'w') as DEVNULL:
                subprocess.check_call([sys.executable, '-m', 'pip'], stdout=DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_installed_version(pkg):
        try:
            output = subprocess.check_output([sys.executable, "-m", "pip", "show", pkg])
            package_info = output.decode('utf-8')
            package_info = dict(item.split(': ', 1) for item in package_info.strip().split('\n'))
            return package_info.get('Version')
        except Exception:
            return None

    if not _check_pip():
        _get_pip()

    for pkg in pkgs:
        try:
            importlib.import_module(pkg)
            continue
        except ModuleNotFoundError:
            pass
        except Exception:
            continue

        installed_version = _get_installed_version(pkg)
        if installed_version:
            pass
        else:
            cmd = [sys.executable, '-m', 'pip', 'install', pkg]
            subprocess.check_call(cmd)

#install("pazok")
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#حفظ البيانات
def save_data(file_name, data):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write('')
    data_str = str(data)
    with open(file_name, 'a') as f:
        f.write(data_str + '\n')
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#تحقق من اشتراك المستخدم بالقناة
def check_tele(token,user_channel,userid):
    
    if not user_channel.startswith('@'):
        user_channel = '@' + user_channel
    try:
        req = requests.get(f'https://api.telegram.org/bot{token}/getChatMember?chat_id={user_channel}&user_id={userid}').json()
        if req["result"]["status"] == "creator" or "administrator" or "member":
            return True
    except:
        try:
            if req["description"] =="Bad Request: member list is inaccessible":
                return "bot is not administrator"
            else:
                return False
        except:
            return False
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

#فن نصي عربي
def art_ar(text="b_azok", font_url=None,size=None,style=None):
    
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    width, height = 1080, 1080
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    if font_url:
        if font_url.startswith(('http://', 'https://')):
            font_response = requests.get(font_url)
            font_filename = "custom_font.ttf"
            with open(font_filename, 'wb') as f:
                f.write(font_response.content)
        else:
            font_filename = font_url
        if not os.path.exists(font_filename):
            raise FileNotFoundError(f"Font file '{font_filename}' not found.")
    else:
        font_url = "https://alfont.com/wp-content/fonts/thulth-arabic-fonts//alfont_com_HONORSansArabicUI-H.ttf"
        font_filename = ".b_azok.ttf"
        
        if not os.path.exists(font_filename):
            response = requests.get(font_url)
            with open(font_filename, 'wb') as f:
                f.write(response.content)
                
    max_font_size = 250
    font_size = max_font_size
    font = ImageFont.truetype(font_filename, font_size)
    text_bbox = draw.textbbox((0, 0), bidi_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    while text_width > width:
        font_size -= 1
        font = ImageFont.truetype(font_filename, font_size)
        text_bbox = draw.textbbox((0, 0), bidi_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), bidi_text, font=font, fill='black')
    current_directory = os.getcwd()
    save_path = os.path.join(current_directory, ".b_azok.png")
    image.save(save_path)
    
    if size == None:
        size=25
    if style == None:
        style=1
        
    return picture(save_path, size,style)
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #
#ستخراح النص من الصوره
def img_txt(pic=None):
    
    if pic is None:
        raise ValueError("يرجى تمرير مسار الصوره")
    with open(pic, 'rb') as file:
        img = base64.b64encode(file.read()).decode()
    
    headers = {
        'User-Agent': 'FirebaseML_[DEFAULT] Google-API-Java-Client Google-HTTP-Java-Client/1.26.0-SNAPSHOT (gzip)',
        'x-goog-api-client': 'java/0 http-google-zzjs/1.26.0 linux/4.14.186',
        'x-android-package': 'com.chat.gtp',
        'x-android-cert': 'CE03387FCD1382BD9207D06FAA52A8D5C90BD658',
        'Content-Type': 'application/json; charset=UTF-8',
        'Content-Encoding': 'gzip',
        'Host': 'vision.googleapis.com',
        'Connection': 'Keep-Alive',
    }
    
    params = {
        'key': 'AIzaSyA1uRNNKYPCMFU8dBKzecrK44v-EJPVi_A',
    }
    
    data = {
        'requests': [
            {
                'features': [{'model': 'builtin/stable', 'type': 'TEXT_DETECTION'}],
                'image': {'content': img},
                'imageContext': {},
            }
        ]
    }
    
    try:
        
        req = requests.post('https://vision.googleapis.com/v1/images:annotate', params=params, headers=headers, json=data).json()
        return req['responses'][0]['textAnnotations'][0]['description']
        
    except:
        return "❌"
#- - - - - - - - - - - - - - -- - - - - - -- - - - - #

