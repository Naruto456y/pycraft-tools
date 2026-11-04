# 🎙️ voice_recognition — распознавание речи (PyCraft Tools)

Один интерфейс для трёх движков распознавания русской речи. Выбираете движок строкой и получаете объект с методом `listen()`.

| Движок | Где работает | Что нужно |
|---|---|---|
| `google` | онлайн, через микрофон | `SpeechRecognition`, `pyaudio` |
| `vosk` | офлайн, через микрофон, wake-word, потоковое распознавание | `vosk`, `requests`, `tqdm`; модель скачивается сама |
| `gigaam` | офлайн, GigaAM v3 (ONNX, INT8), принимает аудио, а не микрофон | `onnx-asr`, `numpy` |

## 🚀 Установка

```bash
pip install pycraft-tools[voice_recognition]   # модуль + микрофон (pyaudio), Vosk и GigaAM
```

## 💻 Примеры

```python
from voice_recognition import create_recognizer

rec = create_recognizer("google", language="ru-RU")
print(rec.listen(timeout=5, phrase_limit=5))   # текст в нижнем регистре или ""

rec = create_recognizer("vosk", model_name="small")   # "small" ~80 МБ, "large" ~2 ГБ
print(rec.listen())

rec = create_recognizer("gigaam")
print(rec.recognize_file("speech.wav"))
print(rec.recognize(pcm_bytes))                # сырой PCM int16, mono, 16 кГц
```

`ENGINES` содержит доступные движки. Неизвестное имя даёт `ValueError` со списком допустимых.

## 🔧 Vosk

`VoskRecognizer` умеет больше, чем `listen()`: `recognize_from_file()`, `recognize_stream()` с колбэками `on_partial` и `on_final`, `set_wake_words()`, `stop_listening()`, `reset()`, запасной вариант через Google. Модели лежат в `~/.vosk_models` (можно сменить через `download_dir`).

## 🧠 GigaAM

Модель `gigaam-v3-e2e-ctc` (INT8, около 225 МБ) качается с HuggingFace при первом запуске. Результат без пунктуации, в нижнем регистре, числа цифрами. Для записи с микрофоном и определения конца фразы (VAD) используйте свой код и передавайте готовые байты в `recognize()`.

## ⚠️ Ограничения

- `GigaAMEngine.listen()` не реализован и поднимает `NotImplementedError`.
- Модель GigaAM сохраняется в папку `models/gigaam` рядом с кодом. После `pip install` это папка внутри `site-packages`, а не рабочий каталог.
- `pyaudio` на Windows и Python 3.13 иногда не ставится из PyPI без готового колеса.
