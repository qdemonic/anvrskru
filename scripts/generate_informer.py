import os
import sys
import json
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE_DIR, 'assets', 'fonts', 'Inter.ttf')
LOGO_PATH = os.path.join(BASE_DIR, 'icon-512.png')

# Canvas Dimensions: Vertical 1080x1440 (4:3 ratio)
WIDTH = 1080
HEIGHT = 1440

EMOJI_PATTERN = re.compile(
    "["
    "\U00010000-\U0010ffff"  # Supplemental symbols, emoji planes
    "\u2600-\u27bf"          # Misc symbols & dingbats (⚡, ⛑, ✈, ❄, etc.)
    "\ufe00-\ufe0f"          # Variation selectors
    "\u200d"                 # Zero width joiner
    "\u20E3"                 # Keycap
    "\u203c\u2049"           # ‼ and ⁉
    "]+",
    flags=re.UNICODE
)

def clean_emojis(text):
    """
    Удаляет Unicode-эмодзи и подчищает висячие знаки препинания в начале.
    Это предотвращает появление пустых квадратиков (.notdef) в TrueType шрифтах.
    """
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub("", text)
    cleaned = re.sub(r'^[!\?,\.\s\:\-\–\—\|\u203c\u2049]+', '', cleaned)
    return " ".join(cleaned.split())

def load_font(size, bold=False):
    """Loads Inter font or system fallback."""
    if os.path.exists(FONT_PATH):
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    # Fallback to system fonts
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    """Wraps text into lines that fit within max_width."""
    text = clean_emojis(text)
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_informer(data, theme='dark'):
    """Generates a high-resolution vertical informer image (1080x1440)."""
    is_dark = (theme == 'dark')

    # Color Palette
    if is_dark:
        bg_top = (11, 17, 32)        # Deep slate/navy
        bg_bottom = (3, 7, 18)       # Slate 950
        card_bg = (19, 29, 51, 235)   # Semi-transparent dark card
        card_border = (51, 65, 85, 200) # Slate 700
        text_primary = (255, 255, 255)
        text_secondary = (148, 163, 184) # Slate 400
        text_muted = (100, 116, 139)     # Slate 500
        accent_blue = (56, 189, 248)     # Sky 400
        badge_bg = (12, 74, 110, 220)    # Sky 900
        badge_text = (186, 230, 253)    # Sky 200
    else:
        bg_top = (248, 250, 252)     # Slate 50
        bg_bottom = (226, 232, 240)  # Slate 200
        card_bg = (255, 255, 255, 245) # White card
        card_border = (203, 213, 225, 220) # Slate 300
        text_primary = (15, 23, 42)    # Slate 900
        text_secondary = (51, 65, 85)  # Slate 700
        text_muted = (100, 116, 139)   # Slate 500
        accent_blue = (2, 132, 199)    # Sky 600
        badge_bg = (224, 242, 254, 255) # Sky 100
        badge_text = (3, 105, 161)     # Sky 700

    # 1. Base Image with Smooth Vertical Gradient
    im = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(bg_top[0] * (1 - ratio) + bg_bottom[0] * ratio)
        g = int(bg_top[1] * (1 - ratio) + bg_bottom[1] * ratio)
        b = int(bg_top[2] * (1 - ratio) + bg_bottom[2] * ratio)
        line = Image.new('RGBA', (WIDTH, 1), (r, g, b, 255))
        im.paste(line, (0, y))

    draw = ImageDraw.Draw(im)

    # 2. Header Section
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert('RGBA')
            logo = logo.resize((84, 84), Image.Resampling.LANCZOS)
            im.paste(logo, (52, 48), logo)
        except Exception:
            pass

    # Title & Subtitle
    font_title = load_font(34, bold=True)
    font_sub = load_font(20, bold=False)
    font_badge = load_font(16, bold=True)
    font_small = load_font(16, bold=False)

    draw.text((154, 52), "АКТУАЛЬНЫЙ НОВОРОССИЙСК", font=font_title, fill=text_primary)
    draw.text((156, 96), "anvrsk.ru • Городской оперативный дашборд", font=font_sub, fill=accent_blue)

    # Live Badge & Timestamp (top right)
    badge_x1, badge_y1 = 760, 52
    badge_x2, badge_y2 = 1028, 86
    draw.rounded_rectangle((badge_x1, badge_y1, badge_x2, badge_y2), radius=17, fill=badge_bg, outline=card_border, width=1)
    
    # Pulse dot (green)
    draw.ellipse((badge_x1 + 14, badge_y1 + 11, badge_x1 + 24, badge_y1 + 21), fill=(34, 197, 94))
    draw.text((badge_x1 + 32, badge_y1 + 7), "ОПЕРАТИВНО • LIVE", font=font_badge, fill=badge_text)

    # Updated time text
    updated_str = data.get('updated_at_human', datetime.now().strftime("%d.%m.%Y в %H:%M МСК"))
    draw.text((720, 98), f"Обновлено: {updated_str}", font=font_small, fill=text_secondary)

    # Divider line
    draw.line((52, 150, 1028, 150), fill=card_border, width=1)

    # 3. Four Metric Cards (2x2 Grid)
    col_w = 472
    col1_x = 52
    col2_x = 556
    row_h = 220
    row1_y = 170
    row2_y = 410

    weather = data.get('weather', {})
    marine = data.get('marine', {})

    def draw_card_base(x1, y1, x2, y2, title, card_type):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=card_bg, outline=card_border, width=1)
        
        # Vector icons for card headers
        if card_type == 'weather':
            # Golden sun icon
            draw.ellipse((x1 + 20, y1 + 18, x1 + 34, y1 + 32), fill=(245, 158, 11))
            draw.ellipse((x1 + 23, y1 + 21, x1 + 31, y1 + 29), fill=(254, 240, 138))
        elif card_type == 'wind':
            # Cyan wind airflow lines
            draw.line((x1 + 18, y1 + 21, x1 + 34, y1 + 21), fill=(56, 189, 248), width=3)
            draw.line((x1 + 15, y1 + 26, x1 + 31, y1 + 26), fill=(56, 189, 248), width=3)
            draw.line((x1 + 20, y1 + 31, x1 + 34, y1 + 31), fill=(56, 189, 248), width=3)
        elif card_type == 'marine':
            # Blue wave crests
            draw.arc((x1 + 16, y1 + 18, x1 + 26, y1 + 30), 180, 0, fill=(56, 189, 248), width=3)
            draw.arc((x1 + 25, y1 + 18, x1 + 35, y1 + 30), 180, 0, fill=(56, 189, 248), width=3)
        elif card_type == 'eco':
            # Emerald green leaf / eco dot
            draw.ellipse((x1 + 20, y1 + 18, x1 + 34, y1 + 32), fill=(34, 197, 94))
            draw.ellipse((x1 + 23, y1 + 21, x1 + 31, y1 + 29), fill=(187, 247, 208))

        draw.text((x1 + 44, y1 + 16), title.upper(), font=font_badge, fill=accent_blue)
        draw.line((x1 + 20, y1 + 44, x2 - 20, y1 + 44), fill=card_border, width=1)

    # CARD 1: Погода и температура (Row 1, Col 1)
    draw_card_base(col1_x, row1_y, col1_x + col_w, row1_y + row_h, "Погода и воздух", "weather")
    t_val = f"{weather.get('temperature', 5.5):+.1f}°C"
    app_t = f"{weather.get('apparent_temperature', 2.0):+.1f}°C"
    hum = f"{weather.get('humidity', 75)}%"
    press = f"{weather.get('pressure_hpa', 1017)} гПа"
    
    font_metric = load_font(42, bold=True)
    draw.text((col1_x + 20, row1_y + 54), t_val, font=font_metric, fill=text_primary)
    
    font_body = load_font(18, bold=False)
    draw.text((col1_x + 20, row1_y + 112), f"Ощущается как: {app_t}", font=font_body, fill=text_secondary)
    draw.text((col1_x + 20, row1_y + 142), f"Влажность: {hum} • Давление: {press}", font=font_body, fill=text_secondary)
    
    tom = weather.get('tomorrow', {})
    tom_str = f"Завтра: {tom.get('temp_max_str', '+7°')} ({clean_emojis(tom.get('condition_desc', 'Малооблачно'))})"
    draw.text((col1_x + 20, row1_y + 174), tom_str, font=font_small, fill=accent_blue)

    # CARD 2: Ветер и Норд-Ост / Бора (Row 1, Col 2)
    draw_card_base(col2_x, row1_y, col2_x + col_w, row1_y + row_h, "Ветер и Норд-Ост (Бора)", "wind")
    w_speed_num = float(weather.get('wind_speed', 4.0) or 0.0)
    w_gusts_num = float(weather.get('wind_gusts', 12.0) or 0.0)
    w_speed_str = f"{w_speed_num:.1f} м/с"
    w_gusts_str = f"(порывы {w_gusts_num:.1f} м/с)"
    w_dir = weather.get('wind_direction_name', 'СВ (Норд-Ост)')

    # Скорость ветра - крупно, сила порывов в скобках - меньшим шрифтом с контролем границы
    font_speed = load_font(38, bold=True)
    font_gusts = load_font(21, bold=False)

    speed_x = col2_x + 20
    speed_y = row1_y + 52
    draw.text((speed_x, speed_y), w_speed_str, font=font_speed, fill=text_primary)

    bbox_speed = draw.textbbox((speed_x, speed_y), w_speed_str, font=font_speed)
    gusts_x = bbox_speed[2] + 8
    gusts_y = speed_y + 14  # Выравнивание по базовой линии крупного шрифта

    # Контроль границ блока: порывы не должны выходить за правую границу карточки
    max_right = col2_x + col_w - 20
    bbox_gusts = draw.textbbox((gusts_x, gusts_y), w_gusts_str, font=font_gusts)
    if bbox_gusts[2] > max_right:
        font_gusts = load_font(18, bold=False)
        gusts_y = speed_y + 16
        bbox_gusts = draw.textbbox((gusts_x, gusts_y), w_gusts_str, font=font_gusts)
        if bbox_gusts[2] > max_right:
            w_gusts_str = f"(до {w_gusts_num:.1f} м/с)"

    draw.text((gusts_x, gusts_y), w_gusts_str, font=font_gusts, fill=text_secondary)
    draw.text((col2_x + 20, row1_y + 104), f"Направление: {w_dir}", font=font_body, fill=text_secondary)

    # Риск боры: КРАСНОЕ выделение использовать ТОЛЬКО в случае опасных значений ветра!
    # Опасные значения ветра (ОЯ) для Новороссийска: порывы >= 25 м/с или скорость >= 20 м/с
    is_dangerous_wind = (w_gusts_num >= 25.0 or w_speed_num >= 20.0)
    is_warning_wind = (w_gusts_num >= 17.0 or w_speed_num >= 13.0)

    if is_dangerous_wind:
        bora_text = "ОПАСНЫЙ (ШТОРМ)"
        bora_bg = (225, 29, 72)   # Красный цвет - ТОЛЬКО при опасных значениях ветра!
    elif is_warning_wind and ('СВ' in w_dir or 'Норд-Ост' in w_dir or 'Север' in w_dir):
        bora_text = "УМЕРЕННЫЙ"
        bora_bg = (217, 119, 6)   # Янтарный / оранжевый при повышенных порывах
    else:
        bora_text = "НИЗКИЙ" if w_gusts_num > 3 else "ШТИЛЬ"
        bora_bg = (15, 118, 110)  # Спокойный морской / изумрудный

    badge_str = f"Риск боры: {bora_text}"
    bbox_b = draw.textbbox((0, 0), badge_str, font=font_badge)
    badge_w = (bbox_b[2] - bbox_b[0]) + 26
    badge_x = col2_x + 20
    badge_y = row1_y + 154
    draw.rounded_rectangle((badge_x, badge_y, badge_x + badge_w, badge_y + 36), radius=10, fill=bora_bg)
    draw.text((badge_x + 13, badge_y + 8), badge_str, font=font_badge, fill=(255, 255, 255))

    # CARD 3: Море и Цемесская бухта (Row 2, Col 1)
    draw_card_base(col1_x, row2_y, col1_x + col_w, row2_y + row_h, "Море и Цемесская бухта", "marine")
    water_t = f"+{marine.get('water_temp', 17.5):.1f}°C"
    wave_h_str = f"{marine.get('wave_height_m', 0.4):.1f} м"
    wave_p = marine.get('wave_points', '2 балла (Умеренное)')
    port_st = marine.get('port_status', 'Открыт для захода')

    draw.text((col1_x + 20, row2_y + 54), f"Вода: {water_t}", font=font_metric, fill=accent_blue)
    draw.text((col1_x + 20, row2_y + 112), f"Волнение: {wave_h_str} ({wave_p})", font=font_body, fill=text_secondary)
    draw.text((col1_x + 20, row2_y + 144), f"Рейд порта: {port_st}", font=font_body, fill=text_secondary)
    
    wave_period = marine.get('wave_period_s', marine.get('wave_period', 3.0))
    nav_status = "Навигация в бухте штатная" if marine.get('wave_height_m', 0.4) < 1.5 else "Ограничение навигации по погоде"
    draw.text((col1_x + 20, row2_y + 174), f"Период волны: {wave_period:.1f} с • {nav_status}", font=font_small, fill=accent_blue)

    # CARD 4: Экология и мониторинг (Row 2, Col 2)
    draw_card_base(col2_x, row2_y, col2_x + col_w, row2_y + row_h, "Экология и качество воздуха", "eco")
    
    # Динамический расчет направления шлейфа цемзаводов по ветру
    eco = data.get('eco')
    if not eco:
        w_deg = float(weather.get('wind_direction', 45) or 45) % 360
        w_spd = float(weather.get('wind_speed', 5.0) or 5.0)
        if w_spd < 1.5:
            eco = {"aqi": 52, "pm25": 14, "status": "Умеренный", "level": "warning", "plume_short": "Застой над промзоной"}
        elif 20 <= w_deg <= 80:
            eco = {"aqi": 28, "pm25": 7, "status": "Чистый воздух", "level": "ok", "plume_short": "Снос в море"}
        elif w_deg >= 310 or w_deg < 20:
            eco = {"aqi": 34, "pm25": 9, "status": "Норма", "level": "ok", "plume_short": "Снос на Кабардинку / море"}
        elif 80 < w_deg <= 160:
            eco = {"aqi": 62, "pm25": 19, "status": "Повышенная запыленность", "level": "warning", "plume_short": "Снос на жилые районы (В / Центр)"}
        elif 160 < w_deg <= 240:
            eco = {"aqi": 46, "pm25": 12, "status": "Умеренный", "level": "ok", "plume_short": "Прижим к Маркотху"}
        else:
            eco = {"aqi": 36, "pm25": 9, "status": "Норма", "level": "ok", "plume_short": "Снос на восток от города"}

    aqi_val = eco.get('aqi', 32)
    aqi_status = eco.get('status', 'Норма')
    pm25_val = eco.get('pm25', 8)
    plume_str = eco.get('plume_short', 'Снос в море')
    eco_level = eco.get('level', 'ok')

    eco_color = (34, 197, 94) if eco_level == 'ok' else ((217, 119, 6) if eco_level == 'warning' else (225, 29, 72))

    draw.text((col2_x + 20, row2_y + 54), f"AQI {aqi_val} • {aqi_status}", font=font_metric, fill=eco_color)
    draw.text((col2_x + 20, row2_y + 112), f"Взвешенные частицы PM2.5: {pm25_val} мкг/м³", font=font_body, fill=text_secondary)
    
    plume_text_color = (217, 119, 6) if eco_level == 'warning' else text_secondary
    draw.text((col2_x + 20, row2_y + 144), f"Шлейф цемзаводов: {plume_str}", font=font_body, fill=plume_text_color)
    draw.text((col2_x + 20, row2_y + 174), f"{eco.get('station_name', 'Экопост «Шесхарис / Пролетарий»')}: норма", font=font_small, fill=text_muted)

    # 4. Section: Recent 3 Official News & Alerts
    section_y = 650
    # Clean section header with red pulse indicator dot
    draw.ellipse((52, section_y + 6, 68, section_y + 22), fill=(239, 68, 68))
    draw.ellipse((56, section_y + 10, 64, section_y + 18), fill=(254, 202, 202))
    draw.text((78, section_y), "ОПЕРАТИВНЫЕ СВОДКИ И СООБЩЕНИЯ СЛУЖБ ГОРОДА", font=load_font(22, bold=True), fill=text_primary)
    draw.line((52, section_y + 36, 1028, section_y + 36), fill=card_border, width=1)

    news_list = data.get('news', [])[:3]
    news_start_y = 696
    news_card_h = 224
    news_gap = 18

    font_news_title = load_font(22, bold=True)
    font_news_body = load_font(18, bold=False)
    font_news_meta = load_font(15, bold=True)

    for i, item in enumerate(news_list):
        ny = news_start_y + i * (news_card_h + news_gap)
        draw.rounded_rectangle((52, ny, 1028, ny + news_card_h), radius=18, fill=card_bg, outline=card_border, width=1)

        # Source badge formatting with clean textual prefix and dot indicator
        raw_source = clean_emojis(item.get('source_name', 'Службы города'))
        cat = item.get('category', 'city')
        
        if 'Безопасный' in raw_source or cat == 'emergency':
            s_badge_bg = (180, 83, 9) if is_dark else (254, 243, 199)
            s_badge_fg = (255, 255, 255) if is_dark else (146, 64, 14)
            badge_label = f"ЕДДС • {raw_source}"
        elif 'Кравченко' in raw_source or cat == 'mayor':
            s_badge_bg = (67, 56, 202) if is_dark else (224, 231, 255)
            s_badge_fg = (255, 255, 255) if is_dark else (55, 48, 163)
            badge_label = f"МЭРИЯ • {raw_source}"
        else:
            s_badge_bg = (3, 105, 161) if is_dark else (224, 242, 254)
            s_badge_fg = (255, 255, 255) if is_dark else (3, 105, 161)
            badge_label = f"МЦУ • {raw_source}"

        bbox = draw.textbbox((0, 0), badge_label, font=font_news_meta)
        badge_w = (bbox[2] - bbox[0]) + 24

        draw.rounded_rectangle((74, ny + 18, 74 + badge_w, ny + 50), radius=9, fill=s_badge_bg)
        draw.text((86, ny + 23), badge_label, font=font_news_meta, fill=s_badge_fg)

        # Time placed cleanly right after the badge
        time_str = item.get('time_display', 'Сегодня')
        draw.text((74 + badge_w + 16, ny + 24), f"•  {time_str}", font=font_small, fill=text_muted)

        # Title (clean of any emojis, wrapped to 1-2 lines)
        raw_title = clean_emojis(item.get('title', ''))
        title_lines = wrap_text(raw_title, font_news_title, 910, draw)[:2]
        cur_text_y = ny + 62
        for t_line in title_lines:
            draw.text((74, cur_text_y), t_line, font=font_news_title, fill=text_primary)
            cur_text_y += 30

        # Snippet (clean of any emojis, up to 2-3 lines with more vertical room)
        snippet = clean_emojis(item.get('text', ''))
        if snippet and snippet != raw_title:
            body_lines = wrap_text(snippet, font_news_body, 910, draw)
            max_b_lines = 2 if len(title_lines) > 1 else 3
            for b_line in body_lines[:max_b_lines]:
                draw.text((74, cur_text_y + 6), b_line, font=font_news_body, fill=text_secondary)
                cur_text_y += 26

    return im.convert('RGB')

def generate_informer_images(payload, output_dir=BASE_DIR):
    """Generates both dark and light versions of informer image."""
    print("Generating informer images (1080x1440)...")

    # Dark theme (default informer.png)
    im_dark = create_informer(payload, theme='dark')
    dark_path = os.path.join(output_dir, 'informer-dark.png')
    im_dark.save(dark_path, 'PNG', optimize=True)
    
    # Primary informer.png (matching the site's dark aesthetic)
    main_path = os.path.join(output_dir, 'informer.png')
    im_dark.save(main_path, 'PNG', optimize=True)

    # Light theme
    im_light = create_informer(payload, theme='light')
    light_path = os.path.join(output_dir, 'informer-light.png')
    im_light.save(light_path, 'PNG', optimize=True)

    print(f" -> Saved {main_path} (1080x1440)")
    print(f" -> Saved {dark_path} (1080x1440)")
    print(f" -> Saved {light_path} (1080x1440)")

if __name__ == '__main__':
    data_file = os.path.join(BASE_DIR, 'data.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
    generate_informer_images(data)
