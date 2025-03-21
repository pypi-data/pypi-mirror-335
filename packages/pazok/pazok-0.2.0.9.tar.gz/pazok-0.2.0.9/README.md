___



# install: `pip install pazok`

___

# Let's start with the function tele_ms
### This function is designed to send messages to a specific Telegram user using the bot token and user's chat ID.
### The function supports sending formatted text using MarkdownV2. Here are
#### the supported formats:
```javascript
Bold text: *text*
Italic text: _text_
Strikethrough text: ~text~
Monospaced text: `text`
Text with a link: [text](url)
Spoiler text: ||text||
Code block: ```code```
```
### It also supports sending files and images via URL or file path. The function automatically detects whether the input is a path or URL and handles it accordingly. If the file or image includes text, it will be automatically added to the file or image description. Additionally, the function supports sending buttons of type types.InlineKeyboardButton, allowing multiple buttons in the same message or just one button. Let's start with examples.

```python
# Importing the library
import pazok

# Bot and user information
token = "token_bot"
id = "chat.id"

# Sending text only
text = "test" # Can be formatted with any supported telebot library format
pazok.tele_ms(token, id, txt=text)

# Sending text with a button
text = "test" # Can be formatted with any supported telebot library format
button = "name_button", "url_button"
# Sending multiple buttons in the same message
buttons = [
    "name_button1", "url_button1",
    "name_button2", "url_button2",
    "name_button3", "url_button3"
]
# Sending the button with text
pazok.tele_ms(token, id, txt=text, buttons=buttons)

# Sending a file or image using their path or URL with text and button
text = "text"
button = "name_button", "url_button"
file = "Link or path to the file"
image = "Link or image path"
pazok.tele_ms(token, id, txt=text, file=file, buttons=buttons)

# Note: It's possible to send either a file or an image in each message. It's not possible to send both an image and a file in the same message.

# Sending an image
pazok.tele_ms(token, id, txt=text, img=image, buttons=buttons)
```
___


# دالة دلول وظيفتها تبدل الكلمات المحظورة الى كلمات بريئة
### Convert bad words to good words
####طريقة الاستخدام
```python
import pazok
test = censor_text("اداة صيد حلوين البصرا")
print(test)
```



# Whats new function ? 
### We Create simple function to convert voice to text

    func for convert " voice any type " to text 

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


```python
from pazok.pazok import voice2text

text = voice2text("my_voice_file_name", lang_type = "ar-SA ")
print(text)

```

___




___


# Now we have some simple functions.
### The next function is to create a random user agent in this format:
`Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36`
### Here's an example:
```python
import pazok
pazok.agnt()
```

___


# The next function is to create an Instagram-specific user agent in this format:
`Instagram 136.0.0.34.124 Android (23/6.0.1; 640dpi; 1440x2560; samsung; SM-G935; hero2lte; samsungexynos8890; en_US; 208061712)`
### Here's an example:
```python
import pazok
pazok.agnt_in()
```

___


# The next function is to obtain some cookies from the Instagram API. The cookie names that can be obtained are csrftoken and mid.
### Here's an example:
```python
import pazok
cok = pazok.cook()
print(cok.csrftoken)
print(cok.mid)

# Or like this:

print(pazok.cook().csrftoken)
print(pazok.cook().mid)
```

___


# Now we have some functions for text decoration.
#### A function to display text with a fading effect. This function changes the text color from black to white through all shades of these colors to create a smooth fading effect. You can also set the duration of the effect and format the text alignment if you want it centered on the screen or in its natural form. Here's an example:
```python
import pazok

text = "test" # The text
time = 0.05 # Duration of the effect
align = True # If you want it continuously centered, write False

pazok.tl(text, time, align)
```

___

# The next function
### The next function is to decorate English letters with 8 types.
### We can display the types using the command
```python
import pazok
pazok.info_motifs()

# This command will return to us

# - 1 - 𝗛𝗲𝗹𝗹𝗼 𝗪𝗼𝗿𝗹𝗱 𝟭𝟮𝟯
# - 2 - 𝙷𝚎𝚕𝚕𝚘 𝚆𝚘𝚛𝚕𝚍 𝟷𝟸𝟹
# - 3 - 𝐇𝐞𝐥𝐥𝐨 𝐖𝐨𝐫𝐥𝐝 𝟏𝟐𝟑
# - 4 - ʜᥱᥣᥣ᥆ ᴡ᥆ᖇᥣძ 𝟙𝟚𝟛
# - 5 - ᕼᗴᒪᒪO ᗯOᖇᒪᗪ 123
# - 6 - 𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉 123
# - 7 - 𝓗𝓮𝓵𝓵𝓸 𝓦𝓸𝓻𝓵𝓭 123
# - 8 - ℍ𝕖𝕝𝕝𝕠 𝕎𝕠𝕣𝕝𝕕 𝟙𝟚𝟛

# Now we can use the decoration function like this

print(pazok.motifs("text", 1)) # Note that I chose pattern number 1. I can change this number to 2 or 3 to others
```
___

# The next function
### This function consists of ready-made colors in the library. Using this function is different from other functions in that we must call the library in this way
```python
import pazok
from pazok import *

# We can display color names through this command

print(pazok.name_clo())

# This command will print

# o = orange
# b = blue
# m = white
# F = dark green
# Z = light red
# e = dark gray
# C = strong white
# p = wide line
# X = yellow
# j = pink
# E = light gray

# Each letter represents its color
# For example, if we write
print(f"{e} TEST")
# The word will print in dark gray
# And so on the rest of the colors
```
___

# The next function
### We have two functions that do the same job almost
#### The function is to display text with a waiting form and a certain period
#### The first is:
```python
import pazok
text = "text" # The text
staliy = "name_staliy" # The pattern
time = 1 # Time

pazok.pazok_rich(text, staliy, time)

# We can display the names of the patterns using this command

pazok.name_rich()

# Will return
# 1. arrow
# 2. christmas
# 3. circle
# 4. clock
# 5. hearts
# 6. moon
# 7. pong
# 8. runner
# 9. star
# 10. weather
```
___

## The next is:
```python
import pazok
text = "text" # The text
staliy = "bounce" # The pattern
time = 1 # Time

pazok.pazok_halo(text, staliy, time)

# We can display their special styles with this command
pazok.name_halo()

# Will print

# 1. dots
# 2. dots2
# 3. dots3
# 4. dots4
# 5. dots5
# 6. dots6
# 7. dots7
# 8. dots8
# 9. dots9
# 10. dots10
# 11. dots11
# 12. dots12
# 13. line
# 14. line2
# 15. pipe
# 16. simpleDots
# 17. simpleDotsScrolling
# 18. star
# 19. star2
# 20. flip
# 21. hamburger
# 22. growVertical
# 23. growHorizontal
# 24. balloon
# 25. balloon2
# 26. noise
# 27. bounce
# 28. boxBounce
# 29. boxBounce2
# 30. triangle
# 31. arc
# 32. circle
# 33. square
# 34. circleQuarters
# 35. circleHalves
# 36. squish
# 37. toggle
# 38. toggle2
# 39. toggle3
# 40. toggle4
# 41. toggle5
# 42. toggle6
# 43. toggle7
# 44. toggle8
# 45. toggle9
# 46. toggle10
# 47. toggle11
# 48. toggle12
# 49. toggle13
# 50. arrow
# 51. arrow2
# 52. arrow3
# 53. bouncyBall
# 54. bouncyBall2
# 55. smiley
# 56. monkey
# 57. hearts
# 58. clock
# 59. earth
# 60. moon
# 61. runner
# 62. pong
# 63. shark
# 64. dqpb
# 65. weather
# 66. emoji
# 67. fire
# 68. lioud
# 69. magic
# 70. curses
# 71. chrome
# 72. windows
# 73. eyes
# 74. action
# 75. mr.robot
# 76. dvd
# 77. pacman
# 78. audi
# 79. bing
# 80. mobile
# 81. data
# 82. bit
# 83. mark
# 84. bit10
# 85. mew
# 86. fbi
# 87. all
# 88. food
# 89. ztang
```
___

## The following functions are used to organize data and execute functions using threads. I'll start with the explanation.

### The next function is designed to convert curl commands into requests using the requests library. Here's an example:

#### Assuming this is a curl command: `curl http://en.wikipedia.org/`
```python
# Usage:
import pazok

curl_command = "curl http://en.wikipedia.org/"
print(pazok.cURL(curl_command))

# It will print the response similar to:
# https://t.me/b_azok
import requests

response = requests.get("http://en.wikipedia.org/").text

print(response)
```
___

# The next function organizes JSON responses into a vertical format. 

### Assuming we have this response:
`{'message': 'The password you entered is incorrect. Please try again.', 'status': 'fail', 'error_type': 'bad_password'}`
```python
import pazok
# If we use the command:
pazok.json_req(response_variable)

# It will print:
# message: The password you entered is incorrect. Please try again.
# status: fail
# error_type: bad_password
```
___

# The next function's task is to execute functions with multiple threads, specifying the number of threads. Here's an example:
```python
import pazok
def test():
    print("xxxx")

number_of_threads = 5  # You can put any number you want
pazok.sb(test, number_of_threads)
```
___

# The next function is designed to fetch session information for a specific Instagram account by logging in with a username and password. Here's an example:
```python
import pazok

username = "username"
password = "password"

test = pazok.log_in(username, password)
print(test.csrftoken)
print(test.sessionid)
print(test.ds_user_id)
print(test.rur)
```
___

### The first function for generating random data, but in a simple way. Essentially, the function replaces numbers with types of data. I'll clarify each number and its value. Number 1 and its random value between a-z and 0-9, for example, if I write 111, the result will be ks6. Number 2, its random value is the same as number 1, but with a slight difference when placing number 2 in different places within the function, the value will be the same in all places, for example, if I write 222, the random value will be hhh. Number 3, its random value is _ or . If I write 1313, this is an example of no more. The result will be h_i. Number 4, its random value is numbers only from 0 to 9. I think the command has become clear, now an example of using the function.
```python
import pazok
username = pazok.user_ran("2113244")
print(username)
```
___

## The next function to get data from my nickname file from the first row to the last row in the function are two options to delete the data that the user gets or any line you get to move to the last line in the file to create a loop or the user's opinion for example to use the function
```python
import pazok
data_file = pazok.user_file("name_file.txt", True)
print(data_file)
```
### I put True to activate the deletion mode from the file after obtaining it if I want to turn off the deletion mode, I put False
___

# The next function
### Now we have a function that stores the bot's code and the user's private chat ID and returns the data at the time of need, and if the data is not found in the hidden file, the function requests the data, and this helps us facilitate the use of our tools. Here's an example.
```python
import pazok
token, id = pazok.info_bot()
```
## If the user wants to delete his data from the hidden file, he can use a special function for example
```python
import pazok
pazok.info_bot_dlet()
```
### This function will search in all paths for user data and delete it
___

# The next function
### A simple and useful function designed to make the script sleep and there is a default time in the function or you can manually set the sleep time the default time is between 0.5 and 1 second, for example
```python
import pazok
pazok.sleep()  # Now in default mode
pazok.sleep(5)  # Now you have manually specified the value
```
___

# The next function
### A wonderful function for converting images to text in two styles. The first is dots like this⣿⣿⣿ and the second is random symbols. There is a small note you must have the background of the image white and the shape you want to convert to text in black to get the best result. Here's an example of using the function.
```python
import pazok
z = "image path"
x = image size in numbers
a = required pattern 1 for dots and 2 for symbols
print(pazok.picture(z, x, a))
```
___

# The next function
### A function designed to set a specific date and time and the function compares the current time with the specified time if it is less than the current time it returns false and if the current time is greater than or equal to the specified time it returns true. There is a default time in the function if the user wants to set a date only the default time is 23:59:59. Here's an example of using the function.
```python
import pazok
test = pazok.timeeg(2024, 7, 5)
if test == True:
    print("The validity period has ended")
```
___

# The next function
### It checks the existence of a specific library or a group of libraries, and if it is not installed, it automatically installs the libraries. Here's an example.
```python
import pazok
pazok.install("requests", "random", "threading")

# I can put any number of libraries
```
___


# Storing Data in a File using the `save_data` Function
## After storing any data in the file, the function will move to a new line to store the next data.
### Here is an example:
```python
import pazok

nesme_file = "text_file_name.txt"
data = "data to be saved in the file"

pazok.save_data(nesme_file, data)
```

___


# The `check_tele` Function
## This function checks if a user is subscribed to a specific Telegram channel using the channel's username.
### Note: You need to have a bot token, and the bot must be an administrator in the channel.
### To check a user's subscription, you need the Telegram user's chat ID.
### Here is an example:
```python
import pazok

token_bot = "0000"
channel_username = "@username"
chat_ID = "id_user"

test = pazok.check_tele(token_bot, channel_username, chat_ID)

print(test)
```

___


### The function will return `True` if the user is subscribed, `False` if not subscribed, and `bot is not administrator` if the bot is not an administrator in the channel.

# The `art_ar` Function
## This function converts Arabic text into beautiful art.
### The function supports any type of Arabic or English fonts.
### Here is an example:
```python
import pazok

text = "Arabic or English text"

line_path = "Set the line path"  # Enter the desired path or leave it empty to use the default font

size = 25  # Or leave it empty to use the default value

style = 1  # There are two styles, you can leave it empty or set it to 2

test=pazok.art_ar(text,line_path,size,style)
print(test)

```

___


# The `img_txt` Function
## This function extracts text from images supported by Google.
### The function needs the image path to extract the text from it.
### Here is an example:
```python
import pazok

image_path = "path to the image"
test = pazok.img_txt(image_path)
print(test)
```

