import os

from setuptools import setup
from setuptools.command.build_py import build_py

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "help_manager", "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()


class BuildPy(build_py):
    """Собирает один пакет из всех папок libraries.

    - help_manager.py остаётся одиночным модулем: `from help_manager import *`
    - в подпакеты попадает только код библиотеки, без тестов и скриптов запуска
    """

    def find_package_modules(self, package, package_dir):
        return [m for m in super().find_package_modules(package, package_dir)
                if not m[1].startswith("test") and not m[1].endswith("_test")]

    def run(self):
        super().run()
        if not self.dry_run:
            self.copy_file(os.path.join(HERE, "help_manager", "help_manager.py"),
                           os.path.join(self.build_lib, "help_manager.py"))

    def get_source_files(self):
        return super().get_source_files() + [os.path.join(HERE, "help_manager", "help_manager.py")]


setup(
    name="pycraft-tools",
    version="1.3.0",
    author="Yusuf Guseinov",
    author_email="yusufvaleh@gmail.com",
    description="Универсальный помощник на Python: голос, музыка, автоматизация, базы данных, ИИ, умный дом, робот, дневник МЭШ",
    long_description=long_description,
    license="MIT",
    long_description_content_type="text/markdown",
    url="https://github.com/Naruto456y/pycraft-tools",
    packages=[
        "ai_modules",
        "voice_recognition",
        "yandex_music_tools",
        "yandex_smart_home",
        "makerzoid_robot",
        "mosru_diary",
    ],
    entry_points={"console_scripts": ["mosru-diary=mosru_diary.mosru_diary:main"]},
    cmdclass={"build_py": BuildPy},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Natural Language :: Russian",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",   # bleak (робот Makerzoid) не ставится на 3.7
    install_requires=[
        "gtts",
        "pydub",
        "SpeechRecognition",
        "pygame",
        "requests",
        "beautifulsoup4",
        "python-vlc",
        "opencv-python-headless",
        "keyboard",
        "mouse",
        "pyautogui",
        "yandex-music",
        "python-dotenv",
        "deepface",
        "easyocr",
        "mss",
        "Pillow",
        "numpy",
        "psutil",
        "youtube-search-python",
        "pyperclip",
        "PyPDF2",
        "plyer",
    ],
    # Код всех модулей лежит в пакете всегда, а extras доустанавливают зависимости нужного модуля:
    # pip install pycraft-tools[makerzoid_robot]
    extras_require={
        "ai_modules": ["requests"],
        "voice_recognition": ["pyaudio", "vosk", "tqdm", "onnx-asr"],     # микрофон, Vosk, GigaAM
        "yandex_music_tools": ["yandex-music"],
        "yandex_smart_home": ["python-dotenv", "flask"],                   # flask: веб-панель
        "makerzoid_robot": ["bleak", "python-dotenv"],
        "mosru_diary": ["requests", "playwright"],                         # playwright: обновление токена
        "all": ["pyaudio", "vosk", "tqdm", "onnx-asr", "flask", "bleak", "playwright"],
    },
)
