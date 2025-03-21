![yae thumbnail](https://github.com/user-attachments/assets/55db4b9a-8649-49b3-bfd4-8af2305f1445)

<h1 align="center"> Waifu-Python </h1>

<div align="center">

A project born out of boredom, designed to simplify and reduce the code related to the [Waifu API](https://github.com/MisfiT2020/wpt/tree/main?tab=readme-ov-file#api-included)

</div>

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **waifu-python**.

```bash
pip install waifu-python
```

## CLI Usage

After installing waifu-python, you can interact with it directly from your terminal. Output for a quick reference:

```bash
╰─ ❯❯ waifu-python 
usage: waifu-python [-h] [--limit LIMIT] [--nsfw | --sfw] [--tags] [--list] [api] [query]

Waifu-Python API client

Required Arguments:
  api            API name
  query          Search query (tag) if any

options:
  -h, --help     show this help message and exit
  --limit LIMIT  Number of images to retrieve
  --nsfw         Fetch in NSFW mode
  --sfw          Fetch in SFW mode
  --tags         Retrieve available tags for the specified API
  --list         List all available API names with SFW/NSFW availability
```

### Examples
- Fetches available Apis

```bash
waifu-python --list
```

- Fetch a random SFW image from a specific API:

```bash
waifu-python danbooru
```

- Fetch a NSFW image with a specific tag:

```bash
waifu-python konachan "raiden shogun" --nsfw 
```

- Retrieve available tags for a given API:

```bash
waifu-python waifuim --tags
```

- Fetch random images with Limits:

```bash
waifu-python random --limit 3
```

- Usage with multiple options:

```bash
waifu-python kemono "raiden shogun" --nsfw --limit 3
```

## Features

- **Flexible Search Input:**  
  Search queries no longer require underscores or hyphens between words, making it easier to find characters and tags.  
  For example, searching for `"Raiden Shogun"` will work the same as `"Raiden_Shogun"` or `"Raiden-Shogun"`  

- **Character Search:**  
  Search for characters by name to get targeted results.  

- **Tag Retrieval:**  
  Retrieve available tags from supported [API](https://github.com/MisfiT2020/wpt/blob/main/README.MD#api-included) to help refine and filter your searches.  

- **Random Image Fetching:**  
  Easily retrieve random images across multiple supported APIs.  

- **API-Specific Image Retrieval:**  
  Fetch random images from a specific API (e.g., **Danbooru, Waifu.im, Waifu.pics, etc.**) based on your preference.  

- **CLI Support:**
   Use `waifu-python` from the command line for quick access to images and tags.

## API Included

| API           | WORKING | TAGS |
|--------------|---------|------|
| [Anilist](https://anilist.co/) | ✓ | - |
| [Danborru](https://danbooru.donmai.us/) | ✓ | - |
| [Gelbooru](https://gelbooru.com/) | ✓ | - |
| [KemonoParty](https://kemono.su/) | ✓ | - |
| [Konachan](https://konachan.net/) | ✓ | - |
| [Nekos.best](https://nekos.best/) | ✓ | ✓ |
| [N-sfw.com](https://n-sfw.com/) | ✓ | ✓ |
| [Pic.re](https://pic.re/) | ✓ | ✓ |
| [Purrbot.site](https://purrbot.site/) | ✓ | - |
| [Rule34](https://rule34.xxx/) | ✓ | - |
| [Safeborru](https://safebooru.org/) | ✓ | - |
| [Waifu.im](https://www.waifu.im/) | ✓ | ✓ |
| [Waifu.pics](https://waifu.pics/) | ✓ | ✓ |
| [Zerochan](https://www.zerochan.net/) | ✓ | - |


## Usage Example

```python
import asyncio
from waifu_python import WaifuIm

async def main():

    image_data1 = await WaifuIm.fetch_sfw_images()
    #Support for tags in Parameters
    image_data2 = await WaifuIm.fetch_sfw_images('raiden-shogun')
    #Retrive tags for the API
    tags = await WaifuIm.get_tags()

    print(f"Random Image{image_data1}\n\nRaiden Shogun{image_data2}\n\nTags{tags}")

asyncio.run(main())
```

## **Required Class Functions**

Each module in this library must implement the following functions:

| Function Name        | APIs Used | Description |
|----------------------|-----------| ------------|
| `fetch_images`      | `Danbooru`, `Yandere`, `Rule34` | Fetches both SFW and NSFW images |
| `fetch_sfw_images`  | `WaifuIm`, `WaifuPics`, `Safebooru`, `NekosBest`, `NSFWBot`, `PicRe`, `Konachan`, `Zerochan` | Fetches only SFW images |
| `fetch_nsfw_images` | `WaifuIm`, `WaifuPics`, `Konachan`, `NSFWBot`, `KemonoParty` | Fetches only NSFW images |
| `fetch_sfw_gif`     | `PurrBot` | Fetches SFW GIFs |
| `fetch_nsfw_gif`    | `PurrBot` | Fetches NSFW GIFs |
| `get_tags`          | `WaifuIm`, `NekosBest`, `WaifuPics`, `PicRe`, `NSFWBot`, `PurrBot` | Fetches Tags from API |


## Example 1: Fetching Images from Multiple APIs

```python
import asyncio
from waifu_python import (
    WaifuIm, NekosBest, WaifuPics, PicRe, PurrBot, NSFWBot,
    Safebooru, Danbooru, Konachan, Yandere, Zerochan, KemonoParty, Rule34
)

async def main():
    # ----- SFW Images -----
    sfw_images = {
        "WaifuIm": await WaifuIm.fetch_sfw_images(),
        "NekosBest": await NekosBest.fetch_sfw_images(),
        "WaifuPics": await WaifuPics.fetch_sfw_images(),
        "PicRe": await PicRe.fetch_sfw_images(),
        "NSFWBot": await NSFWBot.fetch_sfw_images(),
        "PurrBot": await PurrBot.fetch_sfw_images(),
        "SafeBooru": await Safebooru.fetch_images(),
        "Konachan": await Konachan.fetch_sfw_images(),
        "Zerochan": await Zerochan.fetch_sfw_images(),
    }

    # ----- NSFW Images/GIFs -----
    nsfw_images = {
        "WaifuIm": await WaifuIm.fetch_nsfw_images(),
        "WaifuPics": await WaifuPics.fetch_nsfw_images(),
        "NSFWBot": await NSFWBot.fetch_nsfw_images(),
        "PurrBot GIF": await PurrBot.fetch_nsfw_gif(),
        "Danbooru": await Danbooru.fetch_images(),
        "Yandere": await Yandere.fetch_images(),
        "Rule34": await Rule34.fetch_images(),
        "KemonoParty": await KemonoParty.fetch_nsfw_images()
    }

    # ----- Tags -----
    tags = {
        "WaifuIm": await WaifuIm.get_tags(),
        "NekosBest": await NekosBest.get_tags(),
        "WaifuPics": await WaifuPics.get_tags(),
        "PicRe": await PicRe.get_tags(),
        "NSFWBot": await NSFWBot.get_tags(),
        "PurrBot": await PurrBot.get_tags()
    }

    # Display results
    print("----- SFW Images -----")
    for key, value in sfw_images.items():
        print(f"{key}: {value}")

    print("\n----- NSFW Images/GIFs -----")
    for key, value in nsfw_images.items():
        print(f"{key}: {value}")

#------Tags Are Overwhelming------
#   print("\n----- Tags -----")
#   for key, value in tags.items():
#       print(f"{key}: {value}")

asyncio.run(main())

```

## Example 2: Fetching Random Images

```python
import asyncio
from waifu_python import RandomWaifu

async def main():

    random_img = await RandomWaifu.get_random_image()
    sfw_img = await RandomWaifu.get_random_sfw_image()
    nsfw_img = await RandomWaifu.get_random_nsfw_image()
    sfw_gif = await RandomWaifu.get_random_sfw_gif()
    nsfw_gif = await RandomWaifu.get_random_nsfw_gif()

    print("Random Image:", random_img)
    print("SFW Image:", sfw_img)
    print("NSFW Image:", nsfw_img)
    print("SFW GIF:", sfw_gif)
    print("NSFW GIF:", nsfw_gif)

if __name__ == "__main__":
    asyncio.run(main())
```

### Available Methods for Random Image Fetching

| Function | Description |
|----------|-------------|
| `get_random_image()` | Returns a completely random image (SFW or NSFW). |
| `get_random_sfw_image()` | Returns a random SFW image. |
| `get_random_nsfw_image()` | Returns a random NSFW image. |
| `get_random_sfw_gif()` | Returns a random SFW GIF. |
| `get_random_nsfw_gif()` | Returns a random NSFW GIF. |


## Example 3: Anilist Waifus/Characters

```python
import asyncio
from waifu_python import Anilist

async def main():

    waifus = await Anilist.fetch_waifus(search='Mahiru Shiina')
    characters = await Anilist.fetch_characters(search="eren yeager")
    print(waifus)
    print(characters)
    
if __name__ == "__main__":
    asyncio.run(main())
```

### Available Methods:

| Function | Description | Search Parameter | Returned Fields |
|----------|-------------|------------------| --------------- |
| `fetch_waifus(search="<search>")` | Fetches waifus only (female characters). | Optional | `name`, `anime`, `image`, `age`, `gender`, `description` |
| `fetch_characters(search="<search>")` | Fetches all characters (male & female). | Optional | `name`, `anime`, `image`, `age`, `gender`, `description` |

##

🔹 If `search="<character_name>"` is not provided, it will return random characters.



## Example 4: Using Waifu API in a Telegram Bot

```python
from pyrogram import Client, filters
from waifu_python import AniList, SafeBooru, Danbooru

app = Client("Raiden", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

@app.on_message(filters.command("sfw"))
async def send_sfw_image(client, message):
    # Use SafeBooru to fetch a random SFW image.
    args = message.text.split()
    tag = args[1] if len(args) > 1 else None
    try:
        image_url = await SafeBooru.get_random_image(tag)
        if image_url:
            await message.reply_photo(image_url)
        else:
            await message.reply("No SFW image found.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.command("nsfw"))
async def send_nsfw_image(client, message):
    # Use Danbooru to fetch a random NSFW image.
    args = message.text.split()
    tag = args[1] if len(args) > 1 else None
    try:
        image_url = await Danbooru.get_random_image(tag)
        if image_url:
            await message.reply_photo(image_url)
        else:
            await message.reply("No NSFW image found.")
    except Exception as e:
        await message.reply(f"Error: {e}")

# --------------------------------- Anilist ----------------------------------

@app.on_message(filters.command("waifu"))
async def send_waifu_image(client, message):
    # Fetch a random waifu (female character) from Anilist.
    args = message.text.split(maxsplit=1)
    search = args[1] if len(args) > 1 else None
    try:
        waifus = await AniList.fetch_waifus(count=1, search=search)
        if not waifus:
            await message.reply("No waifus found.")
            return
        waifu = waifus[0]
        description = (waifu['description'][:500] + "..."
                       if len(waifu['description']) > 500
                       else waifu['description'])
        caption = (
            f"**Name:** {waifu['name']}\n"
            f"**Anime:** {waifu['anime']}\n"
            f"**Age:** {waifu['age']}\n"
            f"**Gender:** {waifu['gender']}\n\n"
            f"{description}"
        )
        await message.reply_photo(waifu['image'], caption=caption)
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.command("character"))
async def send_character(client, message):
    # Fetch a random character (male or female) from Anilist.
    args = message.text.split(maxsplit=1)
    search = args[1] if len(args) > 1 else None
    try:
        characters = await AniList.fetch_characters(count=1, search=search)
        if not characters:
            await message.reply("No characters found.")
            return
        character = characters[0]
        description = (character['description'][:500] + "..."
                       if len(character['description']) > 500
                       else character['description'])
        caption = (
            f"**Name:** {character['name']}\n"
            f"**Anime:** {character['anime']}\n"
            f"**Age:** {character['age']}\n"
            f"**Gender:** {character['gender']}\n\n"
            f"{description}"
        )
        await message.reply_photo(character['image'], caption=caption)
    except Exception as e:
        await message.reply(f"Error: {e}")

if __name__ == "__main__":
    app.run()
```

## Contributing

We welcome contributions to **waifu-python**! If you'd like to improve the project, please follow these steps:

- **Fork** the repository to your own GitHub account.
- **Clone** the project to your local machine.
- **Create a branch** locally with a succinct but descriptive name (e.g. `feature/your-feature`).
- **Commit** your changes to the branch, following any formatting.
- **Push** your changes to your fork.
- **Open a Pull Request** in our repository, so that we can efficiently review your changes.

Thank you for contributing to **waifu-python**!

## License

    Copyright (c) [2025] [Misfit]

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.