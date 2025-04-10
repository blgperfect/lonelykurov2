from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from io import BytesIO

# Chemins vers les ressources
FONT_PATH = os.path.join("assets", "fonts", "NotoSans-Regular.ttf")
BACKGROUND_PATH = os.path.join("assets", "images", "background.png")

def draw_progress_bar(draw, x, y, width, height, percentage, color_bg, color_fill):
    draw.rectangle([x, y, x + width, y + height], fill=color_bg)
    draw.rectangle([x, y, x + int(width * percentage), y + height], fill=color_fill)

async def generate_rank_card(member, level=0, current_xp=0, xp_needed=100, background_path=None):
    width, height = 800, 240
    background_path = background_path or BACKGROUND_PATH

    background = Image.open(background_path).convert("RGBA").resize((width, height))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 120))
    background = Image.alpha_composite(background, overlay)

    card = Image.new("RGBA", (width, height))
    card.paste(background, (0, 0))

    draw = ImageDraw.Draw(card)
    font_large = ImageFont.truetype(FONT_PATH, 32)
    font_medium = ImageFont.truetype(FONT_PATH, 24)
    font_small = ImageFont.truetype(FONT_PATH, 18)

    draw.text((180, 40), f"{member.display_name}", font=font_large, fill=(255, 255, 255))
    draw.text((180, 90), f"Niveau : {level}", font=font_medium, fill=(255, 255, 255))
    draw.text((180, 125), f"XP : {current_xp} / {xp_needed}", font=font_small, fill=(255, 255, 255))

    percentage = current_xp / xp_needed if xp_needed else 0
    draw_progress_bar(draw, 180, 160, 580, 20, percentage, (50, 50, 50), (102, 204, 255))

    avatar_asset = await member.display_avatar.read()
    avatar = Image.open(BytesIO(avatar_asset)).convert("RGBA").resize((128, 128))
    mask = Image.new("L", avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 128, 128), fill=255)
    avatar = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
    avatar.putalpha(mask)

    card.paste(avatar, (30, 55), avatar)

    output_buffer = BytesIO()
    card.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer

async def generate_leaderboard_image(members_data):
    from PIL import ImageFont
    width, height = 900, 110 + len(members_data) * 90
    background = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # fond transparent

    draw = ImageDraw.Draw(background)
    font_large = ImageFont.truetype(FONT_PATH, 36)
    font_medium = ImageFont.truetype(FONT_PATH, 24)
    font_small = ImageFont.truetype(FONT_PATH, 18)

    draw.text((width // 2 - 140, 20), "🎖️ Leaderboard XP", font=font_large, fill="white")

    for idx, data in enumerate(members_data):
        y = 100 + idx * 90
        box_color = (255, 105, 180, 180)  # rose plus foncé semi-transparent
        draw.rounded_rectangle([50, y, width - 50, y + 80], radius=20, fill=box_color)

        # Avatar
        avatar_data = await data["avatar"].read()
        avatar = Image.open(BytesIO(avatar_data)).convert("RGBA").resize((64, 64))
        mask = Image.new("L", (64, 64), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 64, 64), fill=255)
        avatar.putalpha(mask)
        background.paste(avatar, (60, y + 8), avatar)

        draw.text((140, y + 10), f"#{idx + 1}  {data['name']}", font=font_medium, fill="white")
        draw.text((140, y + 45), f"Niveau {data['level']} | XP Total : {data['total_xp']}", font=font_small, fill="white")

    buffer = BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
