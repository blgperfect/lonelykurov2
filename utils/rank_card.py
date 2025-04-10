# utils/rank_card.py

from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp

BACKGROUND_PATH = "assets/images/background.png"
FONT_PATH = "assets/fonts/NotoSans-Regular.ttf"

async def generate_rank_card(member, level, xp, next_level_xp, total_messages, total_vocal):
    width, height = 900, 250
    card = Image.open(BACKGROUND_PATH).resize((width, height)).convert("RGBA")
    draw = ImageDraw.Draw(card)

    # Chargement police
    font_large = ImageFont.truetype(FONT_PATH, 36)
    font_medium = ImageFont.truetype(FONT_PATH, 28)
    font_small = ImageFont.truetype(FONT_PATH, 22)

    # Avatar
    avatar_asset = member.avatar or member.default_avatar
    buffer_avatar = io.BytesIO()
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_asset.url) as response:
            buffer_avatar.write(await response.read())
    avatar_img = Image.open(buffer_avatar).resize((160, 160)).convert("RGBA")
    mask = Image.new("L", avatar_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0) + avatar_img.size, fill=255)
    avatar_img.putalpha(mask)
    card.paste(avatar_img, (40, 45), avatar_img)

    # Texte
    draw.text((230, 30), member.display_name, font=font_large, fill="white")
    draw.text((230, 75), f"Niveau : {level}", font=font_medium, fill="white")
    draw.text((230, 110), f"XP Total : {xp} / {next_level_xp}", font=font_medium, fill="white")
    draw.text((230, 150), f"💬 Msgs: {total_messages}  🔊 Vocal: {total_vocal} min", font=font_small, fill="#cccccc")

    # Barre de progression
    bar_x, bar_y = 230, 200
    bar_width, bar_height = 620, 25
    progress = min(xp / next_level_xp, 1.0)
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill="#3e3e3e")
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height], fill="#9f59d1")

    # Sauvegarde image
    buffer = io.BytesIO()
    card.save(buffer, "PNG")
    buffer.seek(0)
    return buffer
