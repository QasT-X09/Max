from voice import speech_to_text
from router import plan_action
from tools import open_calculator, open_browser
from tts import speak
from memory import init_db, save_memory
from vector_memory import load_memory, search_similar
from reflection import init_reflection_table, reflect

# доступные инструменты
TOOLS = {
    "open_calculator": open_calculator,
    "open_browser": open_browser
}

# ключевое слово
WAKE_WORD = "мак"

# инициализация памяти
init_db()
init_reflection_table()
load_memory()

while True:

    text = speech_to_text().lower()

    if not text:
        continue

    print("Вы сказали:", text)

    # проверка wake-word
    if WAKE_WORD not in text:
        continue

    # поиск похожих прошлых команд
    similar = search_similar(text)

    if similar:
        print("Похожие команды:", similar)

    # планирование действия через LLM
    plan = plan_action(text)

    action = plan.get("action")

    # выполнение инструмента
    if action in TOOLS:

        result = TOOLS[action]()

        speak(result)

        save_memory(text, action, result)

        reflection = reflect(text, action, result)

        print("Reflection:", reflection)

    else:

        answer = plan.get("args", {}).get("text", "Не понял команду")

        speak(answer)

        save_memory(text, "answer", answer)

        reflection = reflect(text, "answer", answer)

        print("Reflection:", reflection)