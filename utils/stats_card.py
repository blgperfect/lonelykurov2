from PIL import Image, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt

FONT_PATH = "assets/fonts/Roboto-Bold.ttf"  # Change si nécessaire
AVATAR_SIZE = 80

# === HELPER ===
def draw_text(draw, text, xy, font, fill="white"):
    draw.text(xy, text, font=font, fill=fill)

# === USER STATS CARD ===
async def generate_user_card(member, data, save_path):
    img = Image.new("RGBA", (750, 400), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(FONT_PATH, 22)
    font = ImageFont.truetype(FONT_PATH, 18)

    # AVATAR
# Nouvelle ligne (fixée)
    avatar_asset = member.display_avatar.with_size(128)
    avatar_path = f"assets/images/avatar_{member.id}.png"
    await avatar_asset.save(avatar_path)
    avatar = Image.open(avatar_path).resize((AVATAR_SIZE, AVATAR_SIZE)).convert("RGBA")
    img.paste(avatar, (30, 30), avatar)

    # INFOS
    draw_text(draw, f"{member.display_name}", (130, 35), font_big)
    draw_text(draw, f"ID: {member.id}", (130, 65), font)

    # MESSAGES
    messages = data.get("messages", {})
    draw_text(draw, f"Messages : 1j {messages.get('1j', 0)} | 7j {messages.get('7j', 0)} | 14j {messages.get('14j', 0)}", (30, 120), font)

    # VOCAL
    vocal = data.get("vocal_time", {})
    draw_text(draw, f"Vocale : 1j {vocal.get('1j', 0):.2f}h | 7j {vocal.get('7j', 0):.2f}h | 14j {vocal.get('14j', 0):.2f}h", (30, 150), font)

    # TOP
    draw_text(draw, f"📝 Top salon texte : {data.get('top_text', 'N/A')}", (30, 200), font)
    draw_text(draw, f"🎤 Top salon vocal : {data.get('top_vocal', 'N/A')}", (30, 230), font)

    # GRAPHIQUE
    draw_chart(data.get("graph_data", {}), "assets/images/temp_chart_user.png")
    chart = Image.open("assets/images/temp_chart_user.png").resize((600, 100))
    img.paste(chart, (75, 280))

    img.save(save_path)
    os.remove(avatar_path)

# === SERVER STATS CARD ===
def generate_server_card(guild, data, save_path):
    img = Image.new("RGBA", (750, 420), (40, 40, 40))
    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(FONT_PATH, 22)
    font = ImageFont.truetype(FONT_PATH, 18)

    # HEADER
    draw_text(draw, f"{guild.name}", (30, 30), font_big)
    draw_text(draw, f"Créé le : {guild.created_at.strftime('%d %B %Y')}", (30, 65), font)

    # MESSAGES
    m = data.get("messages", {})
    draw_text(draw, f"Messages: 1j {m.get('1j', 0)} | 7j {m.get('7j', 0)} | 14j {m.get('14j', 0)}", (30, 110), font)

    # VOCAL
    v = data.get("vocal_time", {})
    draw_text(draw, f"Vocale: 1j {v.get('1j', 0):.2f}h | 7j {v.get('7j', 0):.2f}h | 14j {v.get('14j', 0):.2f}h", (30, 140), font)

    # CONTRIBUTORS
    c = data.get("contributors", {})
    draw_text(draw, f"Contributeurs: 1j {c.get('1j', 0)} | 7j {c.get('7j', 0)} | 14j {c.get('14j', 0)}", (30, 170), font)

    # TOP
    draw_text(draw, f"# Salon texte : {data.get('top_text', 'N/A')}", (30, 220), font)
    draw_text(draw, f"🎧 Salon vocal : {data.get('top_vocal', 'N/A')}", (30, 250), font)

    draw_text(draw, f"👤 Top membre (msg) : {data.get('top_member_text', 'N/A')}", (30, 290), font)
    draw_text(draw, f"🎙️ Top membre (vocal) : {data.get('top_member_vocal', 'N/A')}", (30, 320), font)

    draw_chart(data.get("graph_data", {}), "assets/images/temp_chart_server.png")
    chart = Image.open("assets/images/temp_chart_server.png").resize((600, 100))
    img.paste(chart, (75, 310))

    img.save(save_path)

# === GRAPH GENERATOR ===
def draw_chart(graph_data, path):
    messages = graph_data.get("messages", [0]*14)
    vocal = graph_data.get("vocal", [0]*14)

    plt.figure(figsize=(5.5, 1.6))
    plt.plot(messages, label="Messages", color="limegreen")
    plt.plot(vocal, label="Vocal", color="deeppink")
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, transparent=True)
    plt.close()
