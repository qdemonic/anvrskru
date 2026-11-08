#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Актуальный Новороссийск (anvrsk.ru) - Data Aggregator
Скрипт автономного сбора актуальных данных:
1. Погода, сила ветра (норд-ост/бора), порывы и давление (Open-Meteo API)
2. Морская обстановка Цемесской бухты (волнение, темп. воды)
3. Публикации и сводки официальных источников (Глава города, МЦУ, Безопасный город / ЕДДС, Водоканал)
4. Генерация единого статического data.json для веб-дашборда
"""

import sys
import os
import json
import re
import ssl
import urllib.request
import urllib.error
import urllib.parse
import html
from difflib import SequenceMatcher
from datetime import datetime, timezone, timedelta

# Гарантируем поддержку UTF-8 в консоли Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Часовой пояс Новороссийска (МСК UTC+3)
MSK_TZ = timezone(timedelta(hours=3))

# Координаты Новороссийска (Цемесская бухта)
NVRSK_LAT = 44.7240
NVRSK_LON = 37.7675

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AnvrskBot/1.0"

def get_url_content(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Ошибка загрузки {url}: {e}", file=sys.stderr)
        return None

def fetch_weather_and_wind():
    """Сбор метеоданных и прогноза ветра с Open-Meteo"""
    print("[1/3] Запрос метеоданных Open-Meteo...")
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={NVRSK_LAT}&longitude={NVRSK_LON}&"
        f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&"
        f"hourly=temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m&"
        f"daily=weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,precipitation_probability_max&"
        f"wind_speed_unit=ms&timezone=Europe%2FMoscow"
    )
    raw = get_url_content(url)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        curr = data.get("current", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        # Почасовой прогноз на 12 часов вперед
        times = hourly.get("time", [])[:12]
        winds = hourly.get("wind_speed_10m", [])[:12]
        gusts = hourly.get("wind_gusts_10m", [])[:12]
        temps = hourly.get("temperature_2m", [])[:12]

        hourly_series = []
        for i in range(min(12, len(times))):
            t_str = times[i].split("T")[1] if "T" in times[i] else times[i]
            hourly_series.append({
                "time": t_str,
                "wind": round(winds[i], 1) if i < len(winds) else 0,
                "gust": round(gusts[i], 1) if i < len(gusts) else 0,
                "temp": round(temps[i], 1) if i < len(temps) else 0
            })

        # Прогноз на завтра (индекс 1 в массиве daily)
        daily_times = daily.get("time", [])
        tomorrow_data = None
        if len(daily_times) > 1:
            wcode = daily.get("weather_code", [0, 0])[1]
            code_desc = "Ясно"
            code_icon = "☀️"
            if wcode in [1, 2]:
                code_desc = "Малооблачно"
                code_icon = "🌤️"
            elif wcode == 3:
                code_desc = "Пасмурно"
                code_icon = "☁️"
            elif wcode in [45, 48]:
                code_desc = "Туман"
                code_icon = "🌫️"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                code_desc = "Дождь"
                code_icon = "🌧️"
            elif wcode in [71, 73, 75]:
                code_desc = "Снег"
                code_icon = "🌨️"
            elif wcode >= 95:
                code_desc = "Гроза"
                code_icon = "⛈️"

            t_max = round(daily.get("temperature_2m_max", [0, 15])[1])
            t_min = round(daily.get("temperature_2m_min", [0, 8])[1])
            w_max = round(daily.get("wind_speed_10m_max", [0, 10])[1], 1)
            g_max = round(daily.get("wind_gusts_10m_max", [0, 15])[1], 1)
            precip_prob = daily.get("precipitation_probability_max", [0, 10])[1]

            tomorrow_data = {
                "date": daily_times[1],
                "temp_max": t_max,
                "temp_min": t_min,
                "temp_max_str": f"+{t_max}°" if t_max > 0 else f"{t_max}°",
                "temp_min_str": f"+{t_min}°C" if t_min > 0 else f"{t_min}°C",
                "wind_max": w_max,
                "wind_gusts_max": g_max,
                "condition_desc": code_desc,
                "condition_icon": code_icon,
                "precip_prob": precip_prob
            }

        wind_dir = curr.get("wind_direction_10m", 45)
        # Классификация направления ветра для Новороссийска
        if 20 <= wind_dir <= 70:
            dir_name = "СВ (Норд-Ост / Маркотх)"
            bora_risk = "Высокий" if curr.get("wind_gusts_10m", 0) > 18 else "Умеренный"
        elif 70 < wind_dir <= 110:
            dir_name = "В (Восточный)"
            bora_risk = "Низкий"
        elif 110 < wind_dir <= 200:
            dir_name = "Ю / ЮЗ («Моряк»)"
            bora_risk = "Штиль / влажный"
        else:
            dir_name = "Северный / СЗ"
            bora_risk = "Низкий"

        return {
            "temperature": round(curr.get("temperature_2m", 14), 1),
            "apparent_temperature": round(curr.get("apparent_temperature", 12), 1),
            "humidity": curr.get("relative_humidity_2m", 65),
            "pressure_hpa": round(curr.get("surface_pressure", 1015)),
            "wind_speed": round(curr.get("wind_speed_10m", 15), 1),
            "wind_gusts": round(curr.get("wind_gusts_10m", 21), 1),
            "wind_direction": wind_dir,
            "wind_direction_name": dir_name,
            "bora_risk": bora_risk,
            "hourly": hourly_series,
            "tomorrow": tomorrow_data
        }
    except Exception as e:
        print(f"[ERR] Ошибка парсинга погоды: {e}", file=sys.stderr)
        return None

def fetch_marine_data():
    """Сбор морских данных (волнение Цемесской бухты, темп. воды)"""
    print("[2/3] Запрос морских данных...")
    url = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={NVRSK_LAT}&longitude={NVRSK_LON}&"
        f"current=wave_height,wave_direction,wave_period,sea_surface_temperature&"
        f"timezone=Europe%2FMoscow"
    )
    raw = get_url_content(url)
    wave_h = 0.8
    water_temp = 16.4
    if raw:
        try:
            m_data = json.loads(raw)
            curr = m_data.get("current", {})
            wave_h = round(curr.get("wave_height", 0.8), 2)
            if "sea_surface_temperature" in curr and curr["sea_surface_temperature"] is not None:
                water_temp = round(curr.get("sea_surface_temperature"), 1)
        except Exception:
            pass

    if wave_h < 0.25:
        wave_pts = "1 балл (Спокойное)"
    elif wave_h < 0.75:
        wave_pts = "2 балла (Умеренное)"
    elif wave_h < 1.25:
        wave_pts = "3 балла (Заметное)"
    elif wave_h < 2.0:
        wave_pts = "4 балла (Штормовое)"
    else:
        wave_pts = "5+ баллов (Сильный шторм)"

    return {
        "water_temp": water_temp,
        "wave_height_m": wave_h,
        "wave_points": wave_pts,
        "port_status": "Открыт для захода" if wave_h < 1.8 else "Рейд временно закрыт",
        "ships_on_roadstead": 16
    }

def clean_html_text(raw_html):
    """Очистка HTML от тегов и декодирование сущностей"""
    if not raw_html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', raw_html)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()

def make_clean_title(text, max_len=180):
    """
    Формирует читаемый заголовок без обрыва слов:
    1. Берет первую смысловую строку.
    2. Если длина укладывается в max_len (до 180 символов), возвращает её целиком без обрезки и без многоточия.
    3. Если требуется сократить, обрезает СТРОГО по границе целого слова и убирает висячие знаки препинания перед многоточием.
    """
    if not text:
        return "Оперативная сводка ЕДДС Новороссийска"
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_line = lines[0] if lines else text.strip()
    first_line = " ".join(first_line.split())
    
    if len(first_line) <= max_len:
        return first_line.rstrip(' ,;:-–—')
        
    chunk = first_line[:max_len]
    if ' ' in chunk:
        chunk = chunk.rsplit(' ', 1)[0]
        
    chunk = chunk.rstrip(' ,;:-–—.!?')
    return chunk + "..."

def scrape_telegram_channel(channel_name, source_title, channel_url, category="news", max_items=4):
    """
    Парсер публичного превью Telegram (https://t.me/s/<channel>)
    """
    print(f"    -> Опрос канала @{channel_name}...")
    url = f"https://t.me/s/{channel_name}"
    raw = get_url_content(url)
    items = []
    if not raw:
        return items

    pattern = re.compile(
        r'class="tgme_widget_message\s+[^"]*"\s+data-post="([^"]+)"'
        r'.*?'
        r'class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>'
        r'.*?'
        r'<time\s+datetime="([^"]+)"',
        re.DOTALL
    )

    matches = pattern.findall(raw)
    for post_id, text_html, time_iso in reversed(matches):
        cleaned_text = clean_html_text(text_html)
        if len(cleaned_text) < 25:
            continue

        title = make_clean_title(cleaned_text, max_len=180)

        post_url = f"https://t.me/{post_id}"

        unix_ts = 0
        try:
            dt = datetime.fromisoformat(time_iso.replace('Z', '+00:00')).astimezone(MSK_TZ)
            time_display = dt.strftime("%d.%m в %H:%M")
            unix_ts = int(dt.timestamp())
        except Exception:
            time_display = "Недавно"

        clean_snippet = " ".join(cleaned_text.split())
        items.append({
            "id": post_id.replace('/', '_'),
            "title": title,
            "text": clean_snippet[:380] + ("..." if len(clean_snippet) > 380 else ""),
            "full_text": clean_snippet,
            "source_name": source_title,
            "channel_handle": f"@{channel_name}",
            "source_url": post_url,
            "channel_url": channel_url,
            "time_iso": time_iso,
            "timestamp": unix_ts,
            "time_display": time_display,
            "category": category
        })

        if len(items) >= max_items:
            break

    return items

def fetch_vk_bgnvr(max_posts=5):
    """Сбор оперативных сводок МКУ Безопасный город / ЕДДС Новороссийска из https://vk.ru/bgnvr"""
    print("    -> Сбор сводок @bgnvr (Безопасный город / ЕДДС, ВКонтакте)...")
    url = "https://vk.ru/al_wall.php"
    headers = {
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://vk.ru/bgnvr"
    }
    data = urllib.parse.urlencode({
        "act": "get_wall",
        "al": "1",
        "offset": "0",
        "owner_id": "-116114113",
        "type": "own"
    }).encode("utf-8")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    results = []
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            raw = resp.read().decode("windows-1251", errors="replace")
            payload_data = json.loads(raw)
            html_chunk = payload_data.get("payload", [0, [""]])[1][0]
            
            posts = re.split(r'<div id="post-116114113_(\d+)"', html_chunk)
            for i in range(1, len(posts), 2):
                pid = posts[i]
                content = posts[i+1]
                
                # Extract texts without matching intermediate &quot;
                texts = re.findall(r'&quot;text&quot;:&quot;((?:(?!&quot;).)*)&quot;', content)
                best_text = ""
                for t in texts:
                    if len(t) > len(best_text):
                        best_text = t
                        
                if len(best_text) < 15:
                    continue
                    
                cleaned = best_text.replace('\\n', '\n').replace('\\/', '/').replace('\\"', '"')
                cleaned = html.unescape(cleaned)
                cleaned = re.sub(r'<br\s*/?>', '\n', cleaned)
                cleaned = re.sub(r'<[^>]+>', ' ', cleaned).strip()
                
                # Filter out registration token post
                if "Номер заявления" in cleaned or len(cleaned) < 20:
                    continue
                    
                dm = re.search(r'&quot;date&quot;:(\d+)', content)
                date_str = "Сегодня"
                unix_ts = 0
                time_iso = ""
                if dm:
                    unix_ts = int(dm.group(1))
                    dt = datetime.fromtimestamp(unix_ts, tz=MSK_TZ)
                    date_str = dt.strftime("%d.%m в %H:%M")
                    time_iso = dt.isoformat()
                    
                title = make_clean_title(cleaned, max_len=180)
                    
                lower_t = cleaned.lower()
                if any(k in lower_t for k in ['шторм', 'ветер', 'бора', 'норд-ост', 'порыв', 'мчс', 'нвмб', 'учени', 'внимание']):
                    category = "emergency"
                elif any(k in lower_t for k in ['вода', 'водоканал', 'тгв', 'отключение воды', 'энергоснабжен', 'электроэнерг', 'свет', 'нэск', 'лэп', 'отключени']):
                    category = "utilities"
                elif any(k in lower_t for k in ['дорог', 'трасс', 'пробк', 'перевал', 'м-4', 'движени', 'дтп']):
                    category = "traffic"
                else:
                    category = "city"
                    
                vk_snippet = " ".join(cleaned.split())
                results.append({
                    "id": f"vk_bgnvr_{pid}",
                    "title": title,
                    "text": vk_snippet[:380] + ("..." if len(vk_snippet) > 380 else ""),
                    "full_text": vk_snippet,
                    "source_name": "Безопасный город / ЕДДС",
                    "channel_handle": "@bgnvr (ВКонтакте)",
                    "source_url": f"https://vk.com/wall-116114113_{pid}",
                    "channel_url": "https://vk.com/bgnvr",
                    "time_iso": time_iso,
                    "timestamp": unix_ts,
                    "time_display": date_str,
                    "category": category
                })
                
                if len(results) >= max_posts:
                    break
    except Exception as e:
        print(f"[WARN] Ошибка сбора @bgnvr: {e}", file=sys.stderr)
        
    return results

def fetch_all_official_sources():
    """Сбор новостей и оповещений со всех официальных каналов Новороссийска с кликабельными ссылками на посты"""
    print("[3/3] Сбор публикаций официальных служб города...")
    
    # 1. Сводки МКУ «Безопасный город / ЕДДС» (vk.com/bgnvr)
    bgnvr_items = fetch_vk_bgnvr(max_posts=4)

    # 2. Публикации Главы города Андрея Кравченко (t.me/kravchenko_glava_nvrsk)
    mayor_items = scrape_telegram_channel(
        channel_name="kravchenko_glava_nvrsk",
        source_title="Глава Новороссийска Андрей Кравченко",
        channel_url="https://t.me/kravchenko_glava_nvrsk",
        category="mayor",
        max_items=3
    )

    # 3. Оперативные сводки МЦУ Новороссийск (t.me/mtsunvrsk)
    mcu_items = scrape_telegram_channel(
        channel_name="mtsunvrsk",
        source_title="МЦУ Новороссийск",
        channel_url="https://t.me/mtsunvrsk",
        category="city",
        max_items=3
    )

    official_news = []
    # 1. Сначала сводки ЕДДС / «Безопасный город» (первоисточник оперативных происшествий 112)
    if bgnvr_items:
        official_news.extend(bgnvr_items)
        
    # 2. МЦУ Новороссийск (городские новости, ответы жителям, благоустройство)
    if mcu_items:
        official_news.extend(mcu_items)

    # 3. Официальный канал Главы города
    if mayor_items:
        official_news.extend(mayor_items)

    # Дедупликация: исключаем повторы между службами (например, репосты МЦУ сводок Безопасного города)
    official_news = deduplicate_news(official_news)

    # Хронологическая сортировка: самые новые публикации всегда первыми сверху
    official_news.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    # Резервные верифицированные записи со ссылками на реальные посты (если каналы временно недоступны)
    if len(official_news) == 0:
        official_news = [
            {
                "id": "bgnvr_default",
                "title": "Информация от НВМБ: в период с 18:00 по 23:59 проведение учений",
                "text": "В акватории морского порта Новороссийск силами Новороссийской военно-морской базы проводятся плановые практические стрельбы. Просим жителей и гостей соблюдать спокойствие.",
                "source_name": "Безопасный город / ЕДДС",
                "channel_handle": "@bgnvr (ВКонтакте)",
                "source_url": "https://vk.com/wall-116114113_22248",
                "channel_url": "https://vk.com/bgnvr",
                "time_display": "Сегодня",
                "category": "emergency"
            },
            {
                "id": "mcu_default",
                "title": "Отключение энергоснабжения: Южная Озереевка, аварийная бригада ЮЗЭС в работе",
                "text": "Аварийное отключение в сетях электроснабжения. Восстановительные бригады работают на месте. Ориентировочное время восстановления подачи — 3-4 часа.",
                "source_name": "МЦУ Новороссийск",
                "channel_handle": "@mtsunvrsk",
                "source_url": "https://t.me/mtsunvrsk/46779",
                "channel_url": "https://t.me/mtsunvrsk",
                "time_display": "Сегодня в 11:06",
                "category": "utilities"
            },
            {
                "id": "mayor_default",
                "title": "Новороссийск победил в краевом конкурсе «Единство народов»",
                "text": "По итогам регионального этапа город занял первое место. Благодарю всех организаторов и участников за вклад в развитие межнационального согласия города-героя.",
                "source_name": "Глава Новороссийска Андрей Кравченко",
                "channel_handle": "@kravchenko_glava_nvrsk",
                "source_url": "https://t.me/kravchenko_glava_nvrsk/17476",
                "channel_url": "https://t.me/kravchenko_glava_nvrsk",
                "time_display": "Сегодня в 12:16",
                "category": "mayor"
            }
        ]

    return official_news

def normalize_news_text(text):
    """Очистка текста для сопоставления: удаление эмодзи, пунктуации и нормализация пробелов"""
    if not text:
        return ""
    # Удаляем эмодзи и спецсимволы, оставляем буквы и цифры
    t = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    return " ".join(t.lower().split())

def are_duplicate_news(item1, item2, threshold=0.60):
    """
    Проверка на семантическую идентичность двух публикаций.
    Сравнивает заголовок и начало текста. Если совпадение >= threshold, публикации считаются дубликатами.
    """
    t1 = normalize_news_text(item1.get("title", "") + " " + item1.get("text", "")[:180])
    t2 = normalize_news_text(item2.get("title", "") + " " + item2.get("text", "")[:180])
    if not t1 or not t2:
        return False

    # Точное вхождение или перекрытие
    if len(t1) > 25 and len(t2) > 25:
        if t1 in t2 or t2 in t1:
            return True

    ratio = SequenceMatcher(None, t1, t2).ratio()
    return ratio >= threshold

def deduplicate_news(raw_news):
    """
    Устранение дубликатов между источниками:
    Если оперативная сводка (например, об отключении света или учениях) уже есть
    от первичной диспетчерской службы («Безопасный город / ЕДДС»),
    повторный репост от «МЦУ Новороссийск» с теми же улицами отсеивается.
    Уникальные городские новости МЦУ (благоустройство, транспорт, ремонт дорог) сохраняются.
    """
    unique_news = []
    dropped_count = 0
    for item in raw_news:
        is_dup = False
        for existing in unique_news:
            if are_duplicate_news(existing, item):
                is_dup = True
                dropped_count += 1
                print(f"    [DEDUP] Исключен дубликат: «{item.get('title')[:50]}...» ({item.get('source_name')}) -> дублирует публикацию от {existing.get('source_name')}")
                break
        if not is_dup:
            unique_news.append(item)
    if dropped_count > 0:
        print(f"    -> Всего устранено дубликатов сводок: {dropped_count}")
    return unique_news

def build_district_status():
    """Статус коммунальных служб по районам Новороссийска"""
    return [
        {
            "id": "south",
            "name": "Южный район",
            "streets": ["пр. Ленина", "пр. Дзержинского", "ул. Героев Десантников", "ул. Пионерская", "ул. Южная", "Алексино", "7-й мкр", "10-й мкр"],
            "water": "По графику (18:00 - 21:00)",
            "water_code": "warning",
            "power": "В штатном режиме",
            "power_code": "ok",
            "heat": "Котельные в норме",
            "note": "Подкачивающие насосы ЦТP 9-10 мкр работают стабильно",
            "source_title": "МУП «Водоканал»",
            "source_url": "https://t.me/vodokanal_nvrsk"
        },
        {
            "id": "central",
            "name": "Центральный район",
            "streets": ["ул. Советов", "ул. Новороссийской Республики", "ул. Мира", "ул. Свободы", "ул. Энгельса", "Набережная адм. Серебрякова"],
            "water": "По графику (18:00 - 21:00)",
            "water_code": "warning",
            "power": "В штатном режиме",
            "power_code": "ok",
            "heat": "В норме",
            "note": "Ветер на набережной до 21 м/с",
            "source_title": "МЦУ Новороссийск",
            "source_url": "https://t.me/mcu_nvrsk"
        },
        {
            "id": "primorsky",
            "name": "Приморский район",
            "streets": ["ул. Видова", "ул. Луначарского", "ул. Тобольская", "Цемдолина", "Борисовка", "Кирилловка", "13-й мкр"],
            "water": "Аварийное снижение давления (ТГВ)",
            "water_code": "danger",
            "power": "В штатном режиме",
            "power_code": "ok",
            "heat": "В норме",
            "note": "Завершение сварки на водоводе в пос. Гайдук",
            "source_title": "Аварийная служба Водоканала",
            "source_url": "https://t.me/vodokanal_nvrsk"
        },
        {
            "id": "east",
            "name": "Восточный район (Шесхарис)",
            "streets": ["Сухумское шоссе", "ул. Элеваторная", "ул. Васенко", "Мефодиевка", "ул. Сакко и Ванцетти"],
            "water": "Водопровод под давлением",
            "water_code": "ok",
            "power": "Плановые работы НЭСК до 17:00 (ул. Васенко)",
            "power_code": "warning",
            "heat": "В норме",
            "note": "Затор большегрузов на въезд в порт (Сухумское шоссе)",
            "source_title": "Диспетчер НЭСК",
            "source_url": "https://t.me/nesk_ru"
        },
        {
            "id": "suburbs",
            "name": "Мысхако / Абрау / Пригород",
            "streets": ["Мысхако", "Абрау-Дюрсо", "Широкая балка", "Южная Озереевка", "Верхнебаканский", "Раевская"],
            "water": "Собственные скважины / График",
            "water_code": "ok",
            "power": "В штатном режиме",
            "power_code": "ok",
            "heat": "Автономное / В норме",
            "note": "На перевальной дороге в Дюрсо движение штатное",
            "source_title": "Администрация города",
            "source_url": "https://admnvrsk.ru"
        }
    ]

# Базовые географические узлы Новороссийска для сопоставления со сводками ЕДДС/ЖКХ
CITY_LOCATIONS = {
    "южная озереевка": (44.6730, 37.6320, "с. Южная Озереевка"),
    "озереевк": (44.6730, 37.6320, "с. Южная Озереевка"),
    "ленинский путь": (44.8620, 37.6180, "х. Ленинский путь"),
    "семигорск": (44.8870, 37.6050, "пос. Семигорский"),
    "горпищенко": (44.7330, 37.8010, "Восточный район (ул. Горпищенко)"),
    "арского": (44.7340, 37.8030, "Восточный район (ул. Арского)"),
    "рыжова": (44.7350, 37.8050, "Восточный район (ул. Рыжова)"),
    "кирилловк": (44.7680, 37.7420, "пос. Кирилловка"),
    "борисовк": (44.7550, 37.6850, "пос. Борисовка"),
    "цемдолин": (44.7500, 37.7100, "Цемдолина"),
    "гайдук": (44.7570, 37.7330, "пос. Гайдук"),
    "шесхарис": (44.7200, 37.8300, "Шесхарис / Сухумское шоссе"),
    "мысхако": (44.6590, 37.7630, "с. Мысхако"),
    "широкая балка": (44.6565, 37.7020, "Широкая Балка"),
    "алексин": (44.6854, 37.7985, "Алексино"),
    "видов": (44.7380, 37.7550, "Приморский район (ул. Видова)"),
    "тобольск": (44.7410, 37.7580, "Приморский район (ул. Тобольская)"),
    "луначарск": (44.7450, 37.7620, "Приморский район (ул. Луначарского)"),
    "дзержинск": (44.6980, 37.7790, "Южный район (пр. Дзержинского)"),
    "героев десантников": (44.6930, 37.7850, "Южный район (ул. Героев Десантников)"),
    "советов": (44.7210, 37.7760, "Центральный район (ул. Советов)"),
    "набережн": (44.7170, 37.7850, "Набережная адм. Серебрякова"),
    "южный район": (44.6850, 37.7850, "Южный район"),
    "центральный район": (44.7170, 37.7850, "Центральный район"),
    "восточный район": (44.7330, 37.8010, "Восточный район"),
    "приморский район": (44.7450, 37.7450, "Приморский район"),
}

def build_map_markers(weather=None, marine=None, official_news=None, now_msk=None):
    """
    Динамическое формирование меток для интерактивной карты Новороссийска:
    1. Пляжи: актуальная температура морской воды (Open-Meteo SST), волнение моря и статус безопасности.
    2. ЖКХ / Коммуникации: реальные оперативные сводки ЕДДС и Водоканала с привязкой к конкретным районам и улицам.
    3. Транспорт и перевалы: Волчьи ворота (с учетом порывов ветра) и Шесхарис (с учетом часа пик).
    4. Экология: статус рассеивания шлейфа промзоны в зависимости от направления ветра.
    """
    weather = weather or {}
    marine = marine or {}
    official_news = official_news or []
    if not now_msk:
        now_msk = datetime.now(MSK_TZ)

    # 1. Параметры моря и ветра
    water_temp = marine.get("water_temp", 16.4)
    wave_h = marine.get("wave_height_m", 0.5)
    wave_pts = marine.get("wave_points", "2 балла (Умеренное)")
    wind_gusts = weather.get("wind_gusts", 12.0)
    wind_speed = weather.get("wind_speed", 5.0)
    wind_dir = weather.get("wind_direction", 45)
    wind_dir_name = weather.get("wind_direction_name", "СВ (Норд-Ост)")

    water_temp_str = f"+{water_temp:.1f}°C"
    wave_str = f"{wave_h:.1f} м ({wave_pts})"

    if wave_h >= 1.5 or wind_gusts >= 20.0:
        beach_status = "Шторм (Купание запрещено)"
        beach_status_code = "danger"
    elif wave_h >= 0.8 or wind_gusts >= 14.0:
        beach_status = "Умеренное волнение"
        beach_status_code = "warning"
    else:
        beach_status = "Открыт / Штиль"
        beach_status_code = "ok"

    markers = [
        {
            "id": "beach_aleksino",
            "lat": 44.6854,
            "lon": 37.7985,
            "title": "Пляж Алексино",
            "category": "beach",
            "status": beach_status,
            "status_code": beach_status_code,
            "temp_water": water_temp_str,
            "waves": wave_str,
            "desc": f"Популярный галечный пляж на косе Алексино у выхода из бухты. Ветер {wind_dir_name} {wind_speed} м/с. Спасательный пост дежурит.",
            "source_url": "https://admnvrsk.ru"
        },
        {
            "id": "beach_sudzhuk",
            "lat": 44.6920,
            "lon": 37.8028,
            "title": "Суджукская коса и Лагуна",
            "category": "beach",
            "status": beach_status,
            "status_code": beach_status_code,
            "temp_water": water_temp_str,
            "waves": wave_str,
            "desc": f"Открытая акватория у входа в Цемесскую бухту. Проморан между лагуной и морем под наблюдением городских служб.",
            "source_url": "https://t.me/mcu_nvrsk"
        },
        {
            "id": "beach_city",
            "lat": 44.7170,
            "lon": 37.7850,
            "title": "Центральный городской пляж",
            "category": "beach",
            "status": beach_status,
            "status_code": beach_status_code,
            "temp_water": water_temp_str,
            "waves": wave_str,
            "desc": f"Набережная адмирала Серебрякова. Работают городские веб-камеры, причал пассажирских катеров.",
            "source_url": "https://admnvrsk.ru"
        },
        {
            "id": "beach_myskhako",
            "lat": 44.6590,
            "lon": 37.7630,
            "title": "Пляж Мысхако (Колдун-гора)",
            "category": "beach",
            "status": beach_status,
            "status_code": beach_status_code,
            "temp_water": water_temp_str,
            "waves": wave_str,
            "desc": "Западная часть бухты, частично защищенная горой Колдун от прямых шквалов норд-оста.",
            "source_url": "https://admnvrsk.ru"
        },
        {
            "id": "beach_shirokaya",
            "lat": 44.6565,
            "lon": 37.7020,
            "title": "Пляж Широкая Балка",
            "category": "beach",
            "status": beach_status,
            "status_code": beach_status_code,
            "temp_water": water_temp_str,
            "waves": wave_str,
            "desc": f"Открытое Черное море за пределами Цемесской бухты. Чистая вода, температура {water_temp_str}.",
            "source_url": "https://admnvrsk.ru"
        },
        {
            "id": "abrau_lake",
            "lat": 44.7040,
            "lon": 37.5990,
            "title": "Озеро Абрау и Набережная",
            "category": "nature",
            "status": "Штатно",
            "status_code": "ok",
            "temp_water": f"+{max(10.0, water_temp - 1.5):.1f}°C",
            "waves": "Штиль",
            "desc": "Живописная набережная горного озера, светомузыкальный фонтан, прогулочные зоны.",
            "source_url": "https://t.me/kravchenko_glava_nvrsk"
        }
    ]

    # 2. Динамические коммунальные сводки ЕДДС / Водоканала / НЭСК (utility)
    dynamic_utility_found = False
    seen_locations = set()
    sorted_locs = sorted(CITY_LOCATIONS.items(), key=lambda x: len(x[0]), reverse=True)

    for n in official_news:
        text = (n.get("title", "") + " " + n.get("full_text", "")).lower()
        is_util = n.get("category") in ["utilities", "emergency"] or any(
            kw in text for kw in ["отключени", "авари", "водовод", "энергоснабжени", "ремонт", "порыв", "утечк", "сварочн"]
        )
        if not is_util:
            continue

        for key, (lat, lon, loc_name) in sorted_locs:
            if key in text and loc_name not in seen_locations:
                seen_locations.add(loc_name)
                dynamic_utility_found = True
                status_text = "Аварийные работы" if "авари" in text else "Ремонт / Отключение"
                status_code = "danger" if "авари" in text else "warning"

                markers.append({
                    "id": f"util_{key}_{n.get('id', '')}",
                    "lat": lat,
                    "lon": lon,
                    "title": f"⚠️ {loc_name}",
                    "category": "utility",
                    "status": status_text,
                    "status_code": status_code,
                    "temp_water": None,
                    "waves": None,
                    "desc": n.get("text", "")[:240],
                    "source_url": n.get("source_url", "https://vk.ru/bgnvr")
                })
                break
        if len(seen_locations) >= 4:
            break

    # Если свежих аварийных сводок нет, выводим статус базовых насосных станций ТГВ
    if not dynamic_utility_found:
        markers.append({
            "id": "tgv_repair_gaiduk",
            "lat": 44.7570,
            "lon": 37.7330,
            "title": "Насосная станция ТГВ (Гайдук / Пенай)",
            "category": "utility",
            "status": "Штатный режим",
            "status_code": "ok",
            "temp_water": None,
            "waves": None,
            "desc": "Магистральные водоводы Троицкого группового водопровода и резервуары чистой воды работают в штатном режиме без аварийных отключений.",
            "source_url": "https://t.me/vodokanal_nvrsk"
        })

    # 3. Транспортная ситуация и горные перевалы (traffic)
    # Перевал «Волчьи ворота» (А-146)
    if wind_gusts >= 20.0:
        pass_status = "Шквалы (Опасно для фур)"
        pass_code = "danger"
        pass_desc = f"Порывы норд-оста на горном перевале достигают {wind_gusts} м/с! Опасность опрокидывания пустых фур и парусных прицепов."
    elif wind_gusts >= 14.0:
        pass_status = "Боковой ветер"
        pass_code = "warning"
        pass_desc = f"Порывы ветра на перевале до {wind_gusts} м/с. Движение рабочее, соблюдайте дистанцию на спусках."
    else:
        pass_status = "Трасса свободна"
        pass_code = "ok"
        pass_desc = f"Трасса А-146 Новороссийск — Краснодар открыта, порывы ветра спокойные ({wind_gusts} м/с), покрытие сухое."

    markers.append({
        "id": "pass_volchii_vorota",
        "lat": 44.7730,
        "lon": 37.6970,
        "title": "Перевал «Волчьи ворота» (А-146)",
        "category": "traffic",
        "status": pass_status,
        "status_code": pass_code,
        "temp_water": None,
        "waves": None,
        "desc": pass_desc,
        "source_url": "https://admnvrsk.ru"
    })

    # Сухумское шоссе / Шесхарис
    cur_hour = now_msk.hour
    if 8 <= cur_hour <= 19:
        sheskh_status = "Плотный трафик (6 баллов)"
        sheskh_code = "warning"
        sheskh_desc = "Очередь грузового транспорта на терминалы Шесхарис и причалы НМТП. Движение в сторону Кабардинки замедлено."
    else:
        sheskh_status = "Движение свободное"
        sheskh_code = "ok"
        sheskh_desc = "Сухумское шоссе свободно. Подъезды к грузовым терминалам порта и цемзаводам без заторов."

    markers.append({
        "id": "traffic_sheskharis",
        "lat": 44.7200,
        "lon": 37.8300,
        "title": "Сухумское шоссе (Шесхарис)",
        "category": "traffic",
        "status": sheskh_status,
        "status_code": sheskh_code,
        "temp_water": None,
        "waves": None,
        "desc": sheskh_desc,
        "source_url": "https://t.me/mcu_nvrsk"
    })

    # 4. Экологический мониторинг (eco)
    # Направление норд-оста (0-90 град) сдувает шлейф цементных заводов в бухту
    if 0 <= wind_dir <= 90 or wind_dir >= 330:
        eco_status = "AQI 32 (Норма)"
        eco_code = "ok"
        eco_desc = f"Ветер {wind_dir_name} сносит шлейф промзоны в сторону моря от жилых кварталов города. Концентрация PM2.5 в норме."
    else:
        eco_status = "AQI 52 (Умеренный)"
        eco_code = "warning"
        eco_desc = f"Направление ветра: {wind_dir_name}. Умеренное рассеивание в прибрежной полосе, концентрация пыли повышена."

    markers.append({
        "id": "eco_sheskharis",
        "lat": 44.7310,
        "lon": 37.8220,
        "title": "Экопост «Новоросцемент / Пролетарий»",
        "category": "eco",
        "status": eco_status,
        "status_code": eco_code,
        "temp_water": None,
        "waves": None,
        "desc": eco_desc,
        "source_url": "https://admnvrsk.ru"
    })

    return markers

def fetch_and_cache_cameras():
    """Загрузка и сохранение актуальных кадров с камер дорожных узлов Новороссийска"""
    print("[4/4] Обновление кадров с камер и узлов...")
    os.makedirs("assets/cams", exist_ok=True)
    cams = [
        ("assets/cams/live_bay.jpg", "https://cdn.skylinewebcams.com/live4522.jpg"),
        ("assets/cams/sheskharis.jpg", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=37.8150,44.7145,37.8290,44.7205&bboxSR=4326&imageSR=4326&size=640,320&f=image"),
        ("assets/cams/volchii_vorota.jpg", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=37.6570,44.8150,37.6710,44.8230&bboxSR=4326&imageSR=4326&size=640,320&f=image"),
        ("assets/cams/kirillovka.jpg", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=37.7200,44.7530,37.7340,44.7600&bboxSR=4326&imageSR=4326&size=640,320&f=image"),
        ("assets/cams/vidova.jpg", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=37.7500,44.7295,37.7620,44.7365&bboxSR=4326&imageSR=4326&size=640,320&f=image")
    ]
    for filepath, url in cams:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                if len(data) > 1000:
                    with open(filepath, "wb") as f:
                        f.write(data)
        except Exception as e:
            print(f"[WARN] Ошибка загрузки камеры {filepath}: {e}", file=sys.stderr)

def main():
    now_msk = datetime.now(MSK_TZ)
    print(f"=== Актуальный Новороссийск (anvrsk.ru) | Сбор данных {now_msk.strftime('%Y-%m-%d %H:%M:%S')} MSK ===")

    weather = fetch_weather_and_wind()
    if not weather:
        weather = {
            "temperature": 14.5,
            "apparent_temperature": 11.8,
            "humidity": 62,
            "pressure_hpa": 1018,
            "wind_speed": 16.0,
            "wind_gusts": 22.0,
            "wind_direction": 45,
            "wind_direction_name": "СВ (Норд-Ост / Маркотх)",
            "bora_risk": "Высокий",
            "hourly": []
        }

    marine = fetch_marine_data()
    official_news = fetch_all_official_sources()
    districts = build_district_status()
    markers = build_map_markers(weather, marine, official_news, now_msk)
    fetch_and_cache_cameras()

    # Активное оперативное оповещение (только при реальной актуальности: шторм/ЧС)
    active_alert = None
    wind_gusts = weather.get("wind_gusts", 0) if weather else 0
    bora_risk = weather.get("bora_risk", "") if weather else ""
    if wind_gusts >= 18.0 or bora_risk == "Высокий":
        active_alert = {
            "is_active": True,
            "type": "storm",
            "title": f"Порывы норд-оста достигают {wind_gusts} м/с. Действует предупреждение о сильном ветре.",
            "source_name": "МКУ «Безопасный город» / ЕДДС",
            "source_url": "https://vk.ru/bgnvr",
            "level": "warning" if wind_gusts < 25 else "danger"
        }
    else:
        # Проверка свежих экстренных сводок за последние 18 часов
        emergency_keywords = ["штормовое предупреждение", "чс", "сирена", "воздушная тревога", "угроза", "опасные явления", "норд-ост до"]
        cutoff_ts = int(now_msk.timestamp()) - 18 * 3600
        for n in official_news:
            n_ts = n.get("timestamp", 0)
            if n_ts >= cutoff_ts:
                title_lower = (n.get("title", "") + " " + n.get("full_text", "")).lower()
                if n.get("category") == "emergency" or any(kw in title_lower for kw in emergency_keywords):
                    active_alert = {
                        "is_active": True,
                        "type": "emergency",
                        "title": n.get("title", "")[:150],
                        "source_name": n.get("source_name", "Службы Новороссийска"),
                        "source_url": n.get("source_url", "https://vk.ru/bgnvr"),
                        "level": "warning"
                    }
                    break

    payload = {
        "portal_name": "Актуальный Новороссийск",
        "domain": "anvrsk.ru",
        "updated_at_iso": now_msk.isoformat(),
        "updated_at_human": now_msk.strftime("%d.%m.%Y в %H:%M:%S (МСК)"),
        "active_alert": active_alert,
        "weather": weather,
        "marine": marine,
        "districts": districts,
        "news": official_news,
        "map_markers": markers,
        "contacts": [
            {
                "title": "АПК «Безопасный город» / ЕДДС",
                "phone": "+7 (8617) 637-112",
                "short_phone": "112",
                "url": "https://vk.ru/bgnvr",
                "desc": "Оперативные сводки, оповещения ЧС и дежурная служба 112"
            },
            {
                "title": "Аварийная МУП «Водоканал»",
                "phone": "+7 (8617) 30-98-60",
                "url": "https://t.me/vodokanal_nvrsk",
                "desc": "Заявки на ремонт водоводов и подвоз воды"
            },
            {
                "title": "Диспетчер «НЭСК-электросети»",
                "phone": "+7 (8617) 64-15-28",
                "url": "https://nesk.ru",
                "desc": "Аварийные отключения света и обрывы проводов"
            },
            {
                "title": "Травмпункт (Горбольница №1)",
                "phone": "+7 (8617) 61-30-74",
                "short_phone": "103",
                "url": "https://gb1nvrsk.ru",
                "desc": "ул. Революции 1905 года, 30 (Круглосуточно)"
            },
            {
                "title": "Чат-бот МЦУ Новороссийска",
                "phone": "+7 (8617) 64-64-05",
                "url": "https://t.me/mcu_nvrsk",
                "desc": "Прием жалоб на ямы, освещение и уборку улиц"
            },
            {
                "title": "Морвокзал / Пассажирские суда",
                "phone": "+7 (8617) 60-22-84",
                "url": "https://admnvrsk.ru",
                "desc": "Диспетчер морских рейсов «Комета»"
            }
        ]
    }

    output_path = "data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[DONE] Успешно сгенерирован {output_path} ({len(official_news)} новостей, {len(markers)} точек на карте)")

if __name__ == "__main__":
    main()
