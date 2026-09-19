#!/usr/bin/env python3

import argparse
import random
import re
import sys
import time
from dataclasses import dataclass


@dataclass
class Vocabulary:
    meaning: str
    answer: str


LINE_PATTERN = re.compile(
    r"^(?P<left>.+?)\s+"
    r"(?P<word>[A-Za-z][A-Za-z0-9'&./()=\-]*(?:\s+[A-Za-z][A-Za-z0-9'&./()=\-]*)*)\s*$"
)


def normalize_answer(text: str) -> str:
    """统一大小写，并合并多余空格。"""
    return " ".join(text.strip().lower().split())


def parse_line(line: str, line_number: int) -> Vocabulary | None:
    line = line.strip()

    if not line:
        return None

    if line.startswith("```") or line.startswith("#"):
        return None

    # 处理 mm（= mmm）这种写法，保留主要词汇 mm
    line = re.sub(r"（=\s*[^）]+）", "", line)

    match = LINE_PATTERN.match(line)

    if not match:
        print(
            f"警告：第 {line_number} 行无法解析，已跳过：{line}",
            file=sys.stderr,
        )
        return None

    meaning = match.group("left").strip()
    word = match.group("word").strip()

    if not meaning or not word:
        print(
            f"警告：第 {line_number} 行内容不完整，已跳过：{line}",
            file=sys.stderr,
        )
        return None

    return Vocabulary(
        meaning=meaning,
        answer=word,
    )


def load_vocabularies(filename: str) -> list[Vocabulary]:
    vocabularies = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                item = parse_line(line, line_number)

                if item is not None:
                    vocabularies.append(item)

    except FileNotFoundError:
        print(f"错误：找不到文件：{filename}", file=sys.stderr)
        sys.exit(1)

    except OSError as error:
        print(f"读取文件失败：{error}", file=sys.stderr)
        sys.exit(1)

    if not vocabularies:
        print("错误：文件中没有找到有效的词汇。", file=sys.stderr)
        sys.exit(1)

    return vocabularies


def clear_screen() -> None:
    """
    使用 ANSI Escape Sequence 清屏。
    不依赖 Windows / Linux / macOS 的系统命令。
    """
    print("\033[2J\033[H", end="", flush=True)


def run_quiz(vocabularies: list[Vocabulary]) -> None:
    random.shuffle(vocabularies)

    total = len(vocabularies)
    completed = 0
    first_try_correct = 0
    wrong_attempts = 0

    for index, vocabulary in enumerate(vocabularies, start=1):
        wrong_count = 0

        while True:
            clear_screen()

            print(f"[{index}/{total}] {vocabulary.meaning}")
            print()

            try:
                user_answer = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                clear_screen()
                print("已退出。")
                return

            if user_answer.lower() in {"q", "quit"}:
                clear_screen()
                print("已退出。")
                return

            is_correct = (
                normalize_answer(user_answer)
                == normalize_answer(vocabulary.answer)
            )

            if is_correct:
                completed += 1

                if wrong_count == 0:
                    first_try_correct += 1

                break

            wrong_count += 1
            wrong_attempts += 1

            if wrong_count >= 3:
                print(f"\n答案：{vocabulary.answer}")
                time.sleep(1)
                break

            print("\n错误。")
            time.sleep(0.5)

    clear_screen()

    print(f"完成：{completed}/{total}")
    print(f"首次答对：{first_try_correct}")
    print(f"错误次数：{wrong_attempts}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="英语单词 CLI 打卡程序"
    )

    parser.add_argument(
        "--file",
        default="u2.txt",
        help="词汇文件路径，默认是 u2.txt",
    )

    args = parser.parse_args()

    vocabularies = load_vocabularies(args.file)
    run_quiz(vocabularies)


if __name__ == "__main__":
    main()
