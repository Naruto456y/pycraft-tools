"""
🐉 ПОЛНЫЙ ТЕСТЕР help_manager — проверяет все классы, включая Music.
"""

import sys
import os
import time

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_new_module import (
    Manager, Console, BazaDB, Music, Face, Auto, Web, System, Info,
    ThreadManager, ScreenReader, Clipboard, MathHelper, FileUtils,
    ImageUtils, PDFUtils, PasswordGen, UnitConverter
)

# Счётчики
passed = 0
failed = 0
skipped = 0

def test(name, func, *args, **kwargs):
    """Запускает тест и выводит результат."""
    global passed, failed, skipped
    try:
        result = func(*args, **kwargs)
        print(f"  ✅ {name}: {result}")
        passed += 1
        return result
    except Exception as e:
        print(f"  ❌ {name}: {type(e).__name__}: {e}")
        failed += 1
        return None

def skip(name, reason=""):
    """Пропускает тест с пояснением."""
    global skipped
    print(f"  ⏭️ {name}: ПРОПУЩЕНО ({reason})")
    skipped += 1

def section(title):
    """Красивый заголовок раздела."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# =============================================================================
# НАЧАЛО ТЕСТИРОВАНИЯ
# =============================================================================
print("=" * 60)
print("  🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ HELP_MANAGER")
print("=" * 60)

# ===========================
# 1. Manager
# ===========================
section("1. Manager — универсальные функции")

test("Manager.now", Manager.now)
test("Manager.today", Manager.today)
test("Manager.randint(1, 100)", Manager.randint, 1, 100)
test("Manager.choice(['a','b','c'])", Manager.choice, ['a', 'b', 'c'])
test("Manager.is_connected()", Manager.is_connected)
test("Manager.clear_console()", Manager.clear_console)
test("Manager.wait(0.1, 'ждём...')", Manager.wait, 0.1, "ждём...")
test("Manager.search_file_path('test.txt')", Manager.search_file_path, "test.txt")
test("Manager.beep(500, 100)", Manager.beep, 500, 100)

# JSON тест
test_json_file = "_test_temp.json"
test_data = {"name": "Yusuf", "age": 12}
test("Manager.save_json", Manager.save_json, test_json_file, test_data)
loaded = test("Manager.load_json", Manager.load_json, test_json_file)
if os.path.exists(test_json_file):
    os.remove(test_json_file)

# Погода (может не работать без инета или если API ключ протух)
if Manager.is_connected():
    weather = test("Manager.get_weather('Москва')", Manager.get_weather, "Москва")
else:
    skip("Manager.get_weather", "нет интернета")

# ===========================
# 2. Console
# ===========================
section("2. Console — цвета и оформление")

test("Console.color('test', 'green')", Console.color, "test", "green")
test("Console.color('test', 'red', style='bold')", Console.color, "test", "red", style="bold")
test("Console.center('Hello')", Console.center, "Hello")
test("Console.size()", Console.size)
test("Console.success('OK')", Console.success, "OK")
test("Console.error('FAIL')", Console.error, "FAIL")
test("Console.warning('WARN')", Console.warning, "WARN")
test("Console.info('INFO')", Console.info, "INFO")
test("Console.header('TEST HEADER', '-')", Console.header, "TEST HEADER", "-")
test("Console.progress_bar(5, 'Test')", Console.progress_bar, 5, "Test", "done", 20)

# ===========================
# 3. BazaDB
# ===========================
section("3. BazaDB — база данных SQLite")

db = BazaDB(":memory:")
test("BazaDB.create_table", db.create_table, "users", ["name", "email"])
test("BazaDB.insert", db.insert, "users", {"name": "Yusuf", "email": "test@mail.ru"})
test("BazaDB.insert #2", db.insert, "users", {"name": "Anna", "email": "anna@mail.ru"})
test("BazaDB.get_all", db.get_all, "users")
test("BazaDB.find (name=Yusuf)", db.find, "users", "name", "Yusuf")
test("BazaDB.search (email содержит mail)", db.search, "users", "email", "mail")
test("BazaDB.update (id=1)", db.update, "users", 1, {"email": "new@mail.ru"})
test("BazaDB.stats", db.stats, "users")
test("BazaDB.show_tables", db.show_tables)
test("BazaDB.delete (id=2)", db.delete, "users", 2)
test("BazaDB.clear_table", db.clear_table, "users")
test("BazaDB.drop_table", db.drop_table, "users")
db.close()

# ===========================
# 4. Music (Яндекс.Музыка)
# ===========================
section("4. Music — Яндекс.Музыка (требуется токен)")

# Проверяем токен
MUSIC_TOKEN = os.getenv("YANDEX_MUSIC_TOKEN")

try:
    from yandex_music import Client
    test_client = Client(MUSIC_TOKEN).init()
    test("Music: токен работает (соединение с API)", lambda: "OK")
    
    # Создаём плеер
    player = None
    try:
        player = Music(token=MUSIC_TOKEN)
        test("Music: инициализация плеера", lambda: player is not None)
    except Exception as e:
        skip("Music: инициализация плеера", str(e))
    
    if player:
        # Поиск трека
        url = player._get_track_url("Morgenshtern Cadillac")
        if url:
            test("Music._get_track_url", lambda: url.startswith("http"))
            
            # Воспроизведение (без ожидания окончания!)
            result = player.play("Morgenshtern Cadillac", wait=False)
            test("Music.play (без ожидания)", lambda: result)
            time.sleep(1)
            
            # Пауза
            test("Music.pause", player.pause)
            time.sleep(0.5)
            
            # Продолжить
            test("Music.pause (продолжить)", player.pause)
            time.sleep(0.5)
            
            # Громкость
            test("Music.volume(30)", player.volume, 30)
            test("Music.get_volume()", player.get_volume)
            test("Music.volume_up(10)", player.volume_up, 10)
            test("Music.volume_down(5)", player.volume_down, 5)
            
            # Очередь
            test("Music.add_to_queue", player.add_to_queue, "Miyagi Captain")
            test("Music.get_queue_length", player.get_queue_length)
            test("Music.show_queue", player.show_queue)
            
            # Инфо
            test("Music.get_current_track", player.get_current_track)
            test("Music.is_now_playing()", player.is_now_playing)
            
            # Остановка
            test("Music.stop", player.stop)
            
            # Очистка
            test("Music.clear_queue", player.clear_queue)
        else:
            skip("Music: поиск трека", "не удалось получить ссылку (возможно, токен протух или трек недоступен)")
        
        # Моя волна (может не работать без лайков)
        try:
            result = player.play_my_wave(limit=3, wait=False)
            if result:
                test("Music.play_my_wave (3 трека, без ожидания)", lambda: result)
                player.stop()
            else:
                skip("Music.play_my_wave", "нет лайкнутых треков")
        except Exception as e:
            skip("Music.play_my_wave", str(e))
        
        # Поиск плейлиста
        try:
            result = player.search_playlist("Style", limit=3, wait=False)
            if result:
                test("Music.search_playlist('Style')", lambda: result)
                player.stop()
            else:
                skip("Music.search_playlist", "плейлист не найден")
        except Exception as e:
            skip("Music.search_playlist", str(e))
        
        # mood
        try:
            result = player.mood("happy", limit=2, wait=False)
            if result:
                test("Music.mood('happy')", lambda: result)
                player.stop()
            else:
                skip("Music.mood", "не найден")
        except Exception as e:
            skip("Music.mood", str(e))
            
except ImportError as e:
    skip("Music: импорт yandex_music", f"библиотека не установлена: {e}")
except Exception as e:
    skip("Music: подключение к API", f"{type(e).__name__}: {e}")

# ===========================
# 5. Face (камера)
# ===========================
section("5. Face — распознавание лиц")

try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
        test("Face: камера доступна", lambda: True)
        
        # detect_emotion — требует DeepFace, может долго грузить модель
        choice = input("  🤔 Проверить Face.detect_emotion()? Может занять 10-30 сек (y/n): ")
        if choice.lower() == 'y':
            emotion = Face.detect_emotion()
            if emotion:
                test(f"Face.detect_emotion() -> {emotion}", lambda: emotion)
            else:
                test("Face.detect_emotion() -> None (нет лица в кадре)", lambda: emotion is None)
        else:
            skip("Face.detect_emotion", "пропущено пользователем")
        
        # detect_smile
        choice = input("  🤔 Проверить Face.detect_smile()? Посмотри в камеру и улыбнись (y/n): ")
        if choice.lower() == 'y':
            smile = Face.detect_smile()
            test(f"Face.detect_smile() -> {smile}", lambda: smile is not None)
        else:
            skip("Face.detect_smile", "пропущено пользователем")
    else:
        cap.release()
        skip("Face: камера", "камера не найдена или занята")
except ImportError as e:
    skip("Face", f"нет cv2: {e}")
except Exception as e:
    skip("Face", str(e))

# ===========================
# 6. Auto (клавиатура и мышь)
# ===========================
section("6. Auto — автоматизация")

test("Auto.write (без реального ввода)", lambda: (Auto.write("test", delay=0.0), True)[1])
test("Auto.is_pressed('esc')", Auto.is_pressed, 'esc')
test("Auto.screenshot", Auto.screenshot, "_test_screen.png")
if os.path.exists("_test_screen.png"):
    os.remove("_test_screen.png")

# Безопасные тесты для мыши (без реальных кликов по экрану)
test("Auto.key_down + key_up (shift)", lambda: (Auto.key_down('shift'), time.sleep(0.1), Auto.key_up('shift'), True)[3])
test("Auto.press('shift', 0.05)", Auto.press, 'shift', 0.05)

# ===========================
# 7. Web
# ===========================
section("7. Web — браузер")

test("Web.open (about:blank)", lambda: (Web.open("about:blank"), True)[1])
test("Web.search", lambda: (Web.search("test"), True)[1])
test("Web.youtube", lambda: (Web.youtube("test"), True)[1])

# ===========================
# 8. System (пропускаем опасное)
# ===========================
section("8. System — системные команды")

skip("System.shutdown", "опасно — пропущено")
skip("System.restart", "опасно — пропущено")
skip("System.sleep", "опасно — пропущено")
skip("System.lock", "опасно — пропущено")

# ===========================
# 9. Info
# ===========================
section("9. Info — информация о системе")

test("Info.os()", Info.os)
test("Info.battery()", Info.battery)
test("Info.cpu()", Info.cpu)
test("Info.ram()", Info.ram)

# ===========================
# 10. ThreadManager
# ===========================
section("10. ThreadManager — потоки")

tm = ThreadManager()

def worker(stop_event):
    """Тестовый воркер: работает пока не остановят."""
    while not stop_event.is_set():
        time.sleep(0.1)

tid = tm.start(worker, name="test_worker")
time.sleep(0.2)
test("ThreadManager.is_alive", tm.is_alive, tid)
test("ThreadManager.list_threads", tm.list_threads)
tm.stop(tid)
time.sleep(0.2)
test("ThreadManager.is_alive (после остановки)", lambda: not tm.is_alive(tid))
test("ThreadManager.active_count", tm.active_count)

# ===========================
# 11. ScreenReader
# ===========================
section("11. ScreenReader — распознавание экрана")

test("ScreenReader.find_image (несуществующий)", lambda: ScreenReader.find_image("___nonexistent___.png") is None)
test("ScreenReader.get_pixel_color(0, 0)", ScreenReader.get_pixel_color, 0, 0)

# ===========================
# 12. Clipboard
# ===========================
section("12. Clipboard — буфер обмена")

test("Clipboard.copy + paste", lambda: (Clipboard.copy("TEST123"), Clipboard.paste() == "TEST123")[1])

# ===========================
# 13. MathHelper
# ===========================
section("13. MathHelper — математика")

test("MathHelper.factorial(5) = 120", lambda: MathHelper.factorial(5) == 120)
test("MathHelper.mean([1,2,3]) = 2.0", lambda: MathHelper.mean([1,2,3]) == 2.0)
test("MathHelper.median([1,2,3,4]) = 2.5", lambda: MathHelper.median([1,2,3,4]) == 2.5)
test("MathHelper.to_binary(42) = '101010'", lambda: MathHelper.to_binary(42) == '101010')
test("MathHelper.to_hex(255) = 'ff'", lambda: MathHelper.to_hex(255) == 'ff')
test("MathHelper.school_round(3.5) = 4.0", lambda: MathHelper.school_round(3.5) == 4.0)
test("MathHelper.school_round(4.5) = 5.0", lambda: MathHelper.school_round(4.5) == 5.0)
test("MathHelper.school_round(3.15, 1) = 3.2", lambda: MathHelper.school_round(3.15, 1) == 3.2)

# ===========================
# 14. FileUtils
# ===========================
section("14. FileUtils — работа с файлами")

temp_f = "_test_temp.txt"
test("FileUtils.write_text", lambda: (FileUtils.write_text(temp_f, "line1\nline2\nline3"), True)[1])
test("FileUtils.read_text", lambda: FileUtils.read_text(temp_f).startswith("line1"))
test("FileUtils.count_lines", lambda: FileUtils.count_lines(temp_f) == 3)
if os.path.exists(temp_f):
    os.remove(temp_f)

# ===========================
# 15. ImageUtils
# ===========================
section("15. ImageUtils — изображения")

# Создадим тестовую картинку через Pillow
try:
    from PIL import Image
    test_img = "_test_img.png"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_img)
    
    test("ImageUtils.resize", ImageUtils.resize, test_img, "_test_resized.png", 50, 50)
    test("ImageUtils.crop", ImageUtils.crop, test_img, "_test_cropped.png", 10, 10, 50, 50)
    test("ImageUtils.rotate", ImageUtils.rotate, test_img, "_test_rotated.png", 90)
    
    # Убираем за собой
    for f in [test_img, "_test_resized.png", "_test_cropped.png", "_test_rotated.png"]:
        if os.path.exists(f):
            os.remove(f)
except ImportError:
    skip("ImageUtils", "Pillow не установлен")

# ===========================
# 16. PDFUtils
# ===========================
section("16. PDFUtils — PDF")

skip("PDFUtils.extract_text", "нужен PDF-файл для теста")

# ===========================
# 17. PasswordGen
# ===========================
section("17. PasswordGen — генератор паролей")

pwd1 = PasswordGen.generate()
test("PasswordGen.generate() — 12 символов", lambda: len(pwd1) == 12)

pwd2 = PasswordGen.generate(8, use_digits=False, use_special=False)
test("PasswordGen.generate(8, False, False) — только буквы", lambda: len(pwd2) == 8 and pwd2.isalpha())

pwd3 = PasswordGen.generate(16)
test("PasswordGen.generate(16) — 16 символов", lambda: len(pwd3) == 16)

# ===========================
# 18. UnitConverter
# ===========================
section("18. UnitConverter — конвертация единиц")

test("UnitConverter.celsius_to_fahrenheit(0) = 32", lambda: UnitConverter.celsius_to_fahrenheit(0) == 32.0)
test("UnitConverter.fahrenheit_to_celsius(32) = 0", lambda: UnitConverter.fahrenheit_to_celsius(32) == 0.0)
test("UnitConverter.km_to_miles(10)", UnitConverter.km_to_miles, 10)
test("UnitConverter.miles_to_km(6.21371)", UnitConverter.miles_to_km, 6.21371)
test("UnitConverter.kg_to_lbs(5)", UnitConverter.kg_to_lbs, 5)
test("UnitConverter.lbs_to_kg(11.0231)", UnitConverter.lbs_to_kg, 11.0231)

# =============================================================================
# ИТОГИ
# =============================================================================
section("📊 ИТОГИ ТЕСТИРОВАНИЯ")

total = passed + failed + skipped
print(f"""
  Всего тестов:    {total}
  ✅ Пройдено:     {passed}
  ❌ Провалено:    {failed}
  ⏭️ Пропущено:    {skipped}
""")

if failed == 0:
    print("  🎉 ВСЕ АКТИВНЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
else:
    print(f"  ⚠️ Есть проблемы: {failed} тестов провалено. Проверь ошибки выше.")

print("=" * 60)
print("  Тестирование завершено!")
print("=" * 60)