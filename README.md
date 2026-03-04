Инструкция по запуску
Установить зависимости (см. шаг 2). 

(Опционально) задать переменные окружения:

OPENAI_API_KEY

JARVIS_VOICE_MODE=0 (если нужно без голоса)

JARVIS_ALLOWED_DIRECTORY и LLM-параметры. 

Запуск:

python -m jarvis.main --task "джарвис создай файл test.txt и запиши привет"

либо python -m jarvis.main --input-file task.txt. 

Summary
Реализован полный проект jarvis/ с требуемой структурой и автономным конвейером: гибридный LLM router, JSON planner с валидацией/replan, executor+tool registry, reflection loop, SQLite+FAISS memory, sandbox security и voice stack. 

Добавлены COM-инструменты для Excel/Word на pywin32 и инструменты файлов/zip с sandbox-ограничениями. 

Добавлены зависимости в requirements.txt и базовая конфигурация в settings.py
