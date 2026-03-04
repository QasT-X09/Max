from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from jarvis.config.settings import settings
from jarvis.core.classifier import TaskClassifier
from jarvis.core.executor import Executor, ToolRegistry
from jarvis.core.planner import Planner
from jarvis.core.reflection import ReflectionAgent
from jarvis.core.router import LLMRouter
from jarvis.memory.sqlite_memory import SQLiteMemory
from jarvis.memory.vector_memory import VectorMemory
from jarvis.security.sandbox import SandboxSecurityLayer
from jarvis.tools.excel_agent import ExcelAgent
from jarvis.tools.filesystem_agent import FileSystemAgent
from jarvis.tools.word_agent import WordAgent
from jarvis.tools.zip_agent import ZipAgent
from jarvis.voice.tts import TTS
from jarvis.voice.wake_word import WakeWordDetector


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fh = logging.FileHandler(settings.LOG_DIR / "jarvis.log", encoding="utf-8")
    sh = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def build_registry(sandbox: SandboxSecurityLayer) -> ToolRegistry:
    fs = FileSystemAgent(sandbox)
    excel = ExcelAgent(sandbox)
    word = WordAgent(sandbox)
    zip_tool = ZipAgent(sandbox)

    registry = ToolRegistry()
    registry.register("fs_write_text", fs.write_text)
    registry.register("fs_read_text", fs.read_text)
    registry.register("fs_list_dir", fs.list_dir)
    registry.register("fs_delete_file", fs.delete_file)
    registry.register("zip_create", zip_tool.create_zip)
    registry.register("zip_extract", zip_tool.extract_zip)
    registry.register("excel_write_cell", excel.write_cell)
    registry.register("excel_read_range", excel.read_range)
    registry.register("excel_set_formula", excel.set_formula)
    registry.register("excel_create_sheet", excel.create_sheet)
    registry.register("word_insert_text", word.insert_text)
    registry.register("word_replace_text", word.replace_text)
    registry.register("word_save_document", word.save_document)
    return registry


def run_task(task: str, logger: logging.Logger) -> dict:
    sandbox = SandboxSecurityLayer(settings.ALLOWED_DIRECTORY)
    classifier = TaskClassifier()
    router = LLMRouter(
        classifier=classifier,
        complexity_threshold=settings.COMPLEXITY_THRESHOLD,
        ollama_url=settings.OLLAMA_URL,
        ollama_model=settings.OLLAMA_MODEL,
        openai_model=settings.OPENAI_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )
    planner = Planner(router=router, max_replans=settings.MAX_REPLAN_ATTEMPTS)
    registry = build_registry(sandbox)
    executor = Executor(registry=registry, logger=logger)
    sqlite_memory = SQLiteMemory(settings.DB_PATH)
    vector_memory = VectorMemory(settings.FAISS_INDEX_PATH)
    reflection = ReflectionAgent(sqlite_memory=sqlite_memory, vector_memory=vector_memory)

    logger.info("Task received: %s", task)
    logger.info("Available tools: %s", ", ".join(registry.list_tools()))

    plan = None
    result = None
    error = None
    try:
        plan = planner.create_plan(task)
        result = executor.execute_plan(plan)
        logger.info("Execution completed")
    except Exception as exc:  # noqa: BLE001
        error = exc
        logger.exception("Task failed")

    strategy = reflection.reflect(task=task, plan=plan, result=result, error=error)
    response = {
        "task": task,
        "plan": plan,
        "result": result,
        "error": str(error) if error else None,
        "strategy": strategy,
    }
    return response


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local autonomous Jarvis assistant")
    parser.add_argument("--task", type=str, help="Task text")
    parser.add_argument("--input-file", type=Path, help="Text file with command")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = configure_logging()

    task = args.task
    if args.input_file:
        task = args.input_file.read_text(encoding="utf-8").strip()

    if not task:
        task = input("Введите задачу: ").strip()

    if settings.VOICE_MODE:
        wake = WakeWordDetector(settings.WAKE_WORD)
        if not wake.is_activated(task):
            logger.info("Wake-word not detected; task ignored")
            print(json.dumps({"status": "ignored", "reason": "wake_word_not_detected"}, ensure_ascii=False))
            return
        task = task.lower().replace(settings.WAKE_WORD.lower(), "", 1).strip()

    response = run_task(task, logger)

    if settings.VOICE_MODE:
        tts = TTS(engine_name=settings.TTS_ENGINE, openai_api_key=settings.OPENAI_API_KEY)
        if response.get("error"):
            tts.speak("Задача завершилась с ошибкой")
        else:
            tts.speak("Задача выполнена")

    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
