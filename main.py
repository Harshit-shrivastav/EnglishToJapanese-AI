import logging
from telethon import TelegramClient, events
from groq import Groq 
import re

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'
GROQ_API_KEY = 'YOUR_GROQ_API_KEY'

client = TelegramClient('translator_bot', api_id, api_hash).start(bot_token=bot_token)

def get_groq_response(user_prompt, system_prompt):
    client = groq.Client(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content
  
def clean_response(response):
    patterns_to_remove = [
        r"^(Here is the translation:|Translation:|Translated text:|The translation is as follows:|In Japanese:|Japanese translation:|The equivalent in Japanese is:|Here is the translated text:|The text in Japanese is:|Below is the translation:|Here's the Japanese version:|Here is the equivalent Japanese text:|The following is the translation:|The following is the text in Japanese:|Translation into Japanese:|This is the translation:|Here is how it translates:|The translated Japanese text:|The text translated to Japanese is:|Below is the text in Japanese:|Here is the content in Japanese:|The equivalent in Japanese:|Translated to Japanese:|Here is your translation:|Here is your text in Japanese:)",
        r"(Here is the translation:|Translation:|Translated text:|The translation is as follows:|In Japanese:|Japanese translation:|The equivalent in Japanese is:|Here is the translated text:|The text in Japanese is:|Below is the translation:|Here's the Japanese version:|Here is the equivalent Japanese text:|The following is the translation:|The following is the text in Japanese:|Translation into Japanese:|This is the translation:|Here is how it translates:|The translated Japanese text:|The text translated to Japanese is:|Below is the text in Japanese:|Here is the content in Japanese:|The equivalent in Japanese:|Translated to Japanese:|Here is your translation:|Here is your text in Japanese:)$"
    ]
    
    for pattern in patterns_to_remove:
        response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.MULTILINE).strip()
    
    response = response.strip()
    
    return response

system_prompt = """
You are a professional translator specializing in translating English paragraphs into Japanese. Please follow these guidelines strictly:

1. **Do not repeat any content unchanged.**
2. **Do not include any introductory or concluding phrases like "Here is the translation:", "Translated text:", "The equivalent in Japanese is:", etc.**
3. **Your only task is to translate the provided English text into Japanese.**
4. **There is no word limit for the translation. Provide an equivalent translation of the entire content.**
5. **Use appropriate Telegram markdowns for better formatting:**
    - **Bold**: **bold**
    - *Italic*: *italic*
    - `Monospace`: `monospace`
    - ~~Strikethrough~~: ~~strike~~
    - <u>Underline</u>: <u>underline</u>
    - <pre language="c++">Code block</pre>: <pre language="c++">code</pre>
6. **Provide translations in both Hiragana/Katakana and Romaji formats.**

**Examples:**
- Example 1:
**(Input) English sentence**: I love my translator bot it is very helpful.

**(Output 1) Japanese (Hiragana/Katakana)**: わたしはわたしのほんやくボットをあいしています。とてもやくにたちます。

**(Output 2) Japanese Romaji**: Watashi wa watashi no hon’yaku botto o aishiteimasu. Totemo yaku ni tachimasu.
- Example 2:
**(Input) English sentence**: I hope you understand what Japanese romanji is now and are not confused.

**(Output 1) Japanese Romaji**: Ima, anata ga nihongo no rōmaji ga nani ka rikai shite, konran shite inai koto o negatteimasu.

**(Output 2) Japanese (Hiragana)**: いま、あなたがにほんごのろーまじがなにかりかいして、こんらんしていないことをねがっています
- Example 3:
**(Input) English Sentence**: The house is yellow and the car is red.

**(Output 1) Japanese Romaji**: Ie wa kiiro de, kuruma wa aka desu.

**(Output 2) Japanese (Hiragana)**: いえはきいろで、くるまはあかです。

Be helpful and precise without directly copying content.
"""

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply('Welcome! Send me an English paragraph, and I will translate it to Japanese.')

@client.on(events.NewMessage)
async def handle_message(event):
    user_prompt = event.message.message
    translated_text = get_groq_response(user_prompt, system_prompt)
    cleaned_text = clean_response(translated_text)
    await event.reply(cleaned_text)

def main():
    logging.basicConfig(level=logging.INFO)
    client.connect() 
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
