#!/usr/bin/env python3
"""morse - 摩尔斯电码编码/解码小工具。

编码：morse encode "HELLO WORLD"
解码：morse decode ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
时序：morse timing "SOS"   （学习用点划时序图）
"""

import argparse
import json
import sys

# 完整码表：字母 + 数字 + 常用标点
MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".",
    "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
    "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---",
    "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--",
    "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--",
    "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--",
    "/": "-..-.", "=": "-...-", "+": ".-.-.", "-": "-....-", ":": "---...",
}
DECODE = {v: k for k, v in MORSE.items()}

DIT, DAH = "·", "−"  # 时序图用符号


def encode(text):
    """文本 -> 摩尔斯码。返回 (编码结果, 跳过的未知字符列表)。"""
    skipped = []
    words = []
    for word in text.upper().split(" "):
        letters = []
        for ch in word:
            if ch in MORSE:
                letters.append(MORSE[ch])
            elif ch:
                if ch not in skipped:
                    skipped.append(ch)
        if letters:
            words.append(" ".join(letters))
    return " / ".join(words), skipped


def decode(code):
    """摩尔斯码 -> 文本。返回 (文本, 未知码列表)。"""
    unknown = []
    words = []
    for word in code.strip().split("/"):
        letters = []
        for token in word.split():
            if token in DECODE:
                letters.append(DECODE[token])
            elif token:
                letters.append("?")
                if token not in unknown:
                    unknown.append(token)
        words.append("".join(letters))
    return " ".join(words), unknown


def timing(text):
    """时序图：·=1 单位点，−=3 单位划；字母内间隔 1 单位，字母间隔 3 单位，词间隔 7 单位。"""
    lines = []
    for word in text.upper().split(" "):
        parts, units = [], 0
        for i, ch in enumerate(word):
            if ch not in MORSE:
                continue
            sym = MORSE[ch].replace(".", DIT).replace("-", DAH)
            spaced = (" " + " " * 1).join(sym)  # 点划之间隔 1 单位
            parts.append(spaced)
            units += sum(1 if c == "." else 3 for c in MORSE[ch])
            units += (len(MORSE[ch]) - 1) * 1  # 点划内间隔
            if i < len(word) - 1:
                parts.append(" " * 3)  # 字母间隔 3 单位
                units += 3
        lines.append(("".join(parts), units))
    return lines


def warn(msg):
    print(f"警告：{msg}", file=sys.stderr)


def cmd_encode(args):
    text = sys.stdin.read() if args.stdin else args.text
    if text is None:
        print("error: 请提供要编码的文本或使用 --stdin", file=sys.stderr)
        return 2
    out, skipped = encode(text.strip())
    for ch in skipped:
        warn(f"跳过不支持的字符：{ch!r}")
    if args.json:
        print(json.dumps({"input": text.strip(), "morse": out,
                          "skipped": skipped}, ensure_ascii=False))
    else:
        print(out)
    return 0


def cmd_decode(args):
    code = sys.stdin.read() if args.stdin else args.code
    if code is None:
        print("error: 请提供要解码的摩尔斯码或使用 --stdin", file=sys.stderr)
        return 2
    out, unknown = decode(code.strip())
    for tok in unknown:
        warn(f"无法识别的码：{tok!r}（已用 ? 代替）")
    if args.json:
        print(json.dumps({"input": code.strip(), "text": out,
                          "unknown": unknown}, ensure_ascii=False))
    else:
        print(out)
    return 0


def cmd_timing(args):
    text = args.text or ""
    if not text.strip():
        print("error: 请提供文本，例如 morse timing SOS", file=sys.stderr)
        return 2
    for diagram, units in timing(text):
        print(diagram)
        print(f"  （共约 {units} 个时间单位：·=1，−=3，字母内间隔 1，字母间隔 3，词间隔 7）")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="morse", description="摩尔斯电码编码 / 解码 / 时序图")
    p.add_argument("--version", action="version", version="morse 0.1.0")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encode", help="文本编码为摩尔斯码")
    e.add_argument("text", nargs="?", help="要编码的文本")
    e.add_argument("--stdin", action="store_true", help="从 stdin 读取")
    e.add_argument("--json", action="store_true", help="JSON 输出")
    e.set_defaults(func=cmd_encode)

    d = sub.add_parser("decode", help="摩尔斯码解码为文本")
    d.add_argument("code", nargs="?", help="要解码的摩尔斯码")
    d.add_argument("--stdin", action="store_true", help="从 stdin 读取")
    d.add_argument("--json", action="store_true", help="JSON 输出")
    d.set_defaults(func=cmd_decode)

    t = sub.add_parser("timing", help="显示点划时序图（学习用）")
    t.add_argument("text", nargs="?", help="要展示时序的文本")
    t.set_defaults(func=cmd_timing)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
