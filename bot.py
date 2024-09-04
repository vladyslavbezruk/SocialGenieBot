import replicate
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import Router
from dotenv import load_dotenv
import os
from collections import deque
from yt_dlp import YoutubeDL, DownloadError
from yt_dlp.extractor.instagram import InstagramIE, InstagramStoryIE

from helper import answer_delete, create_keyboard

load_dotenv()

rep_token = os.getenv("REPLICATE_API_TOKEN")
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
admins = os.getenv('ADMINS').split(',')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

message_history = deque(maxlen=6)

class Form(StatesGroup):
    state_general = State()
    state_grok = State()
    state_web = State()
    state_uncensored = State()
    state_coding = State()

    state_ttimage = State()
    state_ttvideo = State()
    state_face_trans = State()
    state_image_video = State()

    state_tt3d = State()
    state_image_3d = State()

    state_thumbnail = State()
    state_content_ideas = State()
    state_scripts = State()
    state_story_telling = State()

    state_voice_train = State()
    state_voice_hisotry = State()

    state_python = State()
    state_js = State()
    state_cplus = State()
    state_csharp = State()
    state_mql5 = State()
    state_mql4 = State()
    state_pinescript = State()

# ------- commands ---------
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="chat_bots", description="ChatBots"),
        BotCommand(command="text_to_media", description="Text to Media"),
        BotCommand(command="3d_generation", description="3D Image Generation"),
        BotCommand(command="social_media", description="Social Media Automation"),
        BotCommand(command="voice_overs", description="Voice Overs"),
        BotCommand(command="coding", description="Coding"),
    ]
    await bot.set_my_commands(commands)

# ------- Main commands ---------

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hi, сheck the commands to see what models I have.")
    await set_commands(bot)  

@router.message(Command("chat_bots"))
async def cmd_chat_bots(message: types.Message):
    buttons = [
        ("General Use", "general"),
        ("Grok", "grok"),
        ("Browse Web", "web"),
        ("Uncensored", "uncensored"),
        ("Coding", "coding")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

@router.message(Command("text_to_media"))
async def cmd_text_to_media(message: types.Message):
    buttons = [
        ("Text to Image", "ttimage"),
        ("Text to Video", "ttvideo"),
        ("Face Transplant", "face_trans"),
        ("Image to Video", "image_video")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

@router.message(Command("3d_generation"))
async def cmd_3d_generation(message: types.Message):
    buttons = [
        ("Text to 3D", "tt3d"),
        ("Image to 3D", "image_3d")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

@router.message(Command("social_media"))
async def cmd_social_media(message: types.Message):
    buttons = [
        ("Thumbnail generation", "thumbnail"),
        ("Content Ideas", "content_ideas"),
        ("Scripts", "scripts"),
        ("Story Telling", "story_telling")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

@router.message(Command("voice_overs"))
async def cmd_voice_overs(message: types.Message):
    buttons = [
        ("Voice Training", "voice_train"),
        ("Voiceover History", "voice_hisotry")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

@router.message(Command("coding"))
async def cmd_coding(message: types.Message):
    buttons = [
        ("Python", "python"),
        ("JavaScript", "js"),
        ("C++", "cplus"),
        ("C#", "csharp"),
        ("MQL5", "mql5"),
        ("MQL4", "mql4"),
        ("PineScript V5", "pinescript")
    ]
    keyboard = create_keyboard(buttons)
    await message.answer("Choose an option:", reply_markup=keyboard)

# ------- Download from YouTube, Instagram --------
async def try_download(site_type, url, ydl_opts, proxy=None):
    if proxy:
        ydl_opts['proxy'] = proxy

    if site_type == 'youtube' or site_type == 'instagram' or site_type == 'facebook':
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info_dict)
    else:
        raise Exception('Type of site is unknown')

@router.message(F.text.startswith("https://www.youtube.com") | F.text.startswith("https://youtube.com/shorts") | F.text.startswith("https://youtu.be"))
async def handle_youtube_link(message: types.Message, state: FSMContext):
    url = message.text
    await state.set_data({"url": url})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Download Audio 📲", callback_data="download_audio_youtube")],
        [InlineKeyboardButton(text="🎥 Download Video 📲", callback_data="choose_quality")]
    ])

    await message.reply("Choose option:", reply_markup=keyboard)

@router.message(F.text.startswith("https://www.instagram.com") | F.text.startswith("https://www.instagram.com/reel") |
                F.text.startswith("https://www.instagram.com/stories") | F.text.startswith("https://www.instagram.com/p"))
async def handle_instagram_link(message: types.Message, state: FSMContext):
    url = message.text
    await state.set_data({"url": url})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Download Audio 📲", callback_data="download_audio_instagram")],
        [InlineKeyboardButton(text="🎥 Download Video 📲", callback_data="download_video_instagram")]
    ])

    await message.reply("Choose option:", reply_markup=keyboard)

@router.message(F.text.startswith("https://www.facebook.com") | F.text.startswith("https://www.facebook.com/watch") |
                F.text.startswith("https://www.facebook.com/reel") | F.text.startswith("https://www.facebook.com/stories") |
                F.text.startswith("https://www.fb.com") | F.text.startswith("https://www.fb.com/watch") |
                F.text.startswith("https://www.fb.com/reel") | F.text.startswith("https://www.fb.com/stories"))
async def handle_instagram_link(message: types.Message, state: FSMContext):
    url = message.text
    await state.set_data({"url": url})

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Download Audio 📲", callback_data="download_audio_facebook")],
        [InlineKeyboardButton(text="🎥 Download Video 📲", callback_data="download_video_facebook")]
    ])

    await message.reply("Choose option:", reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith("download_audio_"))
async def download_audio(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    site_type = callback_query.data.split("_")[-1]

    await callback_query.message.edit_text(f"📲")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    try:
        audio_file = await try_download(site_type, url, ydl_opts, ydl_opts)
        await bot.send_audio(callback_query.from_user.id, types.FSInputFile(audio_file))
        os.remove(audio_file)
        await callback_query.message.edit_text("Sound has been successfully sent!")
    except DownloadError as e:

        proxy = 'https://135.148.100.78:48149'
        try:
            audio_file = await try_download(site_type, url, ydl_opts, proxy=proxy)
            await bot.send_audio(callback_query.from_user.id, types.FSInputFile(audio_file))
            os.remove(audio_file)
            await callback_query.message.edit_text("Sound has been successfully sent through proxy!")
        except Exception as e:
            await callback_query.answer(f"Failed downloading audio even through proxy: {str(e)}")
    except Exception as e:
        await callback_query.answer(f"Unexpected error: {str(e)}")

@router.callback_query(lambda call: call.data == "choose_quality")
async def choose_quality(callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="360p", callback_data="download_video_youtube_360p")],
        [InlineKeyboardButton(text="720p", callback_data="download_video_youtube_720p")],
        [InlineKeyboardButton(text="1080p", callback_data="download_video_youtube_1080p")]
    ])
    await callback_query.message.edit_text("Select the video quality:", reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith("download_video_"))
async def download_video(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    url = data.get("url")
    quality = ''

    if len(callback_query.data.split("_")) > 3:
        site_type = callback_query.data.split("_")[-2]
        quality = callback_query.data.split("_")[-1]
    else:
        site_type = callback_query.data.split("_")[-1]

    await callback_query.message.edit_text(f"📲")

    if site_type == 'youtube':
        ydl_opts = {
            'format': f'best[height<={quality}]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    elif site_type == 'instagram' or site_type == 'facebook':
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    else:
        raise Exception('Type of site is unknown')

    try:
        video_file = await try_download(site_type, url, ydl_opts)
        await bot.send_video(callback_query.from_user.id, types.FSInputFile(video_file))
        os.remove(video_file)

        if quality != '':
            await callback_query.message.edit_text(f"Video {quality} sent successfully!")
        else:
            await callback_query.message.edit_text(f"Video sent successfully!")

    except DownloadError as e:
        proxy = 'https://47.251.43.115:33333'
        try:
            video_file = await try_download(site_type, ydl_opts, proxy=proxy)
            await bot.send_video(callback_query.from_user.id, types.FSInputFile(video_file))
            os.remove(video_file)

            if quality != '':
                await callback_query.message.edit_text(f"Video {quality} sent successfully through proxy!")
            else:
                await callback_query.message.edit_text(f"Video sent successfully through proxy!")

        except Exception as e:
            await callback_query.answer(f"Failed downloading video even through proxy: {str(e)}")
    except Exception as e:
        await callback_query.answer(f"Unexpected error: {str(e)}")

# ------------  Callback handlers ------------
@router.callback_query(lambda c: c.data in ["general", "grok", "web", "uncensored", "coding"])
async def process_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "general":
        await state.clear()
        await state.set_state(Form.state_general)
        await answer_delete(bot, callback_query, "You selected General.")
    elif code == "grok":
        await state.clear()

        await state.set_state(Form.state_grok)
        await answer_delete(bot, callback_query, "You selected Grok.")
    elif code == "web":
        await state.clear()
        await state.set_state(Form.state_web)
        await answer_delete(bot, callback_query, "You selected Browse Web.")
    elif code == "uncensored":
        await state.set_state(Form.state_uncensored)
        await answer_delete(bot, callback_query, "You selected Uncensored.")
    elif code == "coding":
        await state.set_state(Form.state_coding)
        await answer_delete(bot, callback_query, "You selected Coding.")

@router.callback_query(lambda c: c.data in ["ttimage", "ttvideo", "face_trans", "image_video"])
async def process_text_to_media_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "ttimage":
        await state.clear()        
        await state.set_state(Form.state_ttimage)
        await answer_delete(bot, callback_query, "You selected Text to Image.")
    elif code == "ttvideo":
        await state.set_state(Form.state_ttvideo)
        await answer_delete(bot, callback_query, "You selected Text to Video.")
    elif code == "face_trans":
        await state.set_state(Form.state_face_trans)
        await answer_delete(bot, callback_query, "You selected Face Transplant.")
    elif code == "image_video":
        await state.set_state(Form.state_image_video)
        await answer_delete(bot, callback_query, "You selected Image to Video.")

@router.callback_query(lambda c: c.data in ["tt3d", "image_3d"])
async def process_3d_generation_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "tt3d":
        await state.clear()
        await state.set_state(Form.state_tt3d)
        await answer_delete(bot, callback_query, "You selected Text to 3D.")
    elif code == "image_3d":
        await state.clear()
        await state.set_state(Form.state_image_3d)
        await answer_delete(bot, callback_query, "You selected Image to 3D.")

@router.callback_query(lambda c: c.data in ["thumbnail", "content_ideas", "scripts", "story_telling"])
async def process_social_media_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "thumbnail":
        await state.clear()
        await state.set_state(Form.state_thumbnail)
        await answer_delete(bot, callback_query, "You selected Thumbnail generation.")
    elif code == "content_ideas":
        await state.clear()
        await state.set_state(Form.state_content_ideas)
        await answer_delete(bot, callback_query, "You selected Content Ideas.")
    elif code == "scripts":
        await state.clear()
        await state.set_state(Form.state_scripts)
        await answer_delete(bot, callback_query, "You selected Scripts.")
    elif code == "story_telling":
        await state.clear()
        await state.set_state(Form.state_story_telling)
        await answer_delete(bot, callback_query, "You selected Story Telling.")

@router.callback_query(lambda c: c.data in ["voice_train", "voice_hisotry"])
async def process_voice_overs_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "voice_train":
        await state.clear()
        await state.set_state(Form.state_voice_train)
        await answer_delete(bot, callback_query, "You selected Voice Training.")
    elif code == "voice_hisotry":
        await state.clear()
        await state.set_state(Form.state_voice_hisotry)
        await answer_delete(bot, callback_query, "You selected Voiceover History.")

@router.callback_query(lambda c: c.data in ["python", "js", "cplus", "csharp", "mql5", "mql4", "pinescript"])
async def process_coding_callback(callback_query: CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == "python":
        await state.clear()
        await state.set_state(Form.state_python)
        await answer_delete(bot, callback_query, "You selected Python.")
    elif code == "js":
        await state.clear()
        await state.set_state(Form.state_js)
        await answer_delete(bot, callback_query, "You selected JavaScript.")
    elif code == "cplus":
        await state.clear()
        await state.set_state(Form.state_cplus)
        await answer_delete(bot, callback_query, "You selected C++.")
    elif code == "csharp":
        await state.clear()
        await state.set_state(Form.state_csharp)
        await answer_delete(bot, callback_query, "You selected C#.")
    elif code == "mql5":
        await state.clear()
        await state.set_state(Form.state_mql5)
        await answer_delete(bot, callback_query, "You selected MQL5.")
    elif code == "mql4":
        await state.clear()
        await state.set_state(Form.state_mql4)
        await answer_delete(bot, callback_query, "You selected MQL4.")
    elif code == "pinescript":
        await state.clear()
        await state.set_state(Form.state_pinescript)
        await answer_delete(bot, callback_query, "You selected PineScript V5.")

# -------- States handlers -----------

@router.message(Form.state_general)
async def handle_general(message: types.Message, state: FSMContext):
    message_history.append(f"user: {message.text}")

    sent_message = await bot.send_message(message.from_user.id, "💬")
    message_id = sent_message.message_id

    system_prompt = "You are a telegram bot\n\n"
    if len(message_history) > 0:
        history = "\n".join(message_history)
        system_prompt += f"Previous messages:\n{history}"

    message_text = ""
    for event in replicate.stream(
        "meta/meta-llama-3-8b-instruct",
        input={
            "top_k": 0,
            "top_p": 0.95,
            "prompt": message.text,
            "max_tokens": 512,
            "temperature": 0.7,
            "system_prompt": system_prompt,
            "length_penalty": 1,
            "max_new_tokens": 512,
            "stop_sequences": "<|end_of_text|>,<|eot_id|>",
            "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "presence_penalty": 0,
            "log_performance_metrics": False
        },
    ):
        output = str(event)
        message_text += output
        try:
            await message.bot.edit_message_text(text=message_text, chat_id=message.chat.id, message_id=message_id)
        except Exception as e:
            print(f'Error: {e}')
            pass
    
    message_history.append(f"assistant: {message_text}")


def simulate_stream():
    yield "Example response from AI model."


@router.message(Form.state_grok)
async def handle_grok(message: types.Message, state: FSMContext):
    await message.answer("Grok model response")

@router.message(Form.state_web)
async def handle_web(message: types.Message, state: FSMContext):
    await message.answer("Browse web model response")

@router.message(Form.state_uncensored)
async def handle_uncensored(message: types.Message, state: FSMContext):
    await message.answer("Uncensored model response")

@router.message(Form.state_coding)
async def handle_coding(message: types.Message, state: FSMContext):
    await message.answer("Coding model response")

@router.message(Form.state_ttimage)
async def handle_ttimage(message: types.Message, state: FSMContext):
    await message.answer("Text to Image model response")

@router.message(Form.state_ttvideo)
async def handle_ttvideo(message: types.Message, state: FSMContext):
    await message.answer("Text to Video model response")

@router.message(Form.state_face_trans)
async def handle_face_trans(message: types.Message, state: FSMContext):
    await message.answer("Face Transplant model response")

@router.message(Form.state_image_video)
async def handle_image_video(message: types.Message, state: FSMContext):
    await message.answer("Image to Video model response")

@router.message(Form.state_tt3d)
async def handle_tt3d(message: types.Message, state: FSMContext):
    await message.answer("Text to 3D model response")

@router.message(Form.state_image_3d)
async def handle_image_3d(message: types.Message, state: FSMContext):
    await message.answer("Image to 3D model response")

@router.message(Form.state_thumbnail)
async def handle_thumbnail(message: types.Message, state: FSMContext):
    await message.answer("Thumbnail generation model response")

@router.message(Form.state_content_ideas)
async def handle_content_ideas(message: types.Message, state: FSMContext):
    await message.answer("Content Ideas model response")

@router.message(Form.state_scripts)
async def handle_scripts(message: types.Message, state: FSMContext):
    await message.answer("Scripts model response")

@router.message(Form.state_story_telling)
async def handle_story_telling(message: types.Message, state: FSMContext):
    await message.answer("Story Telling model response")

@router.message(Form.state_voice_train)
async def handle_voice_train(message: types.Message, state: FSMContext):
    await message.answer("Voice Training model response")

@router.message(Form.state_voice_hisotry)
async def handle_voice_hisotry(message: types.Message, state: FSMContext):
    await message.answer("Voiceover History model response")

@router.message(Form.state_python)
async def handle_python(message: types.Message, state: FSMContext):
    await message.answer("Python model response")

@router.message(Form.state_js)
async def handle_js(message: types.Message, state: FSMContext):
    await message.answer("JavaScript model response")

@router.message(Form.state_cplus)
async def handle_cplus(message: types.Message, state: FSMContext):
    await message.answer("C++ model response")

@router.message(Form.state_csharp)
async def handle_csharp(message: types.Message, state: FSMContext):
    await message.answer("C# model response")

@router.message(Form.state_mql5)
async def handle_mql5(message: types.Message, state: FSMContext):
    await message.answer("MQL5 model response")

@router.message(Form.state_mql4)
async def handle_mql4(message: types.Message, state: FSMContext):
    await message.answer("MQL4 model response")

@router.message(Form.state_pinescript)
async def handle_pinescript(message: types.Message, state: FSMContext):
    await message.answer("PineScript V5 model response")

if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)