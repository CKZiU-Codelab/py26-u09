#!/usr/bin/env python3
"""Self-check for the project "Edit Timeline" (u09).

Run it in the project directory:

    python3 check.py

The script reads only the files your program produced. It never runs
your program, so generate the files first, then check them. Each
[fail] line names one requirement; fix it and run the script again.
"""

import csv
import html as html_lib
import os
import re
import sys


class Fail(Exception):
    pass


CHECKS = []
WARNINGS = []


def check(name):
    def register(function):
        CHECKS.append((name, function))
        return function
    return register


def warn(message):
    WARNINGS.append(message)


def read_text(path):
    if not os.path.exists(path):
        raise Fail("%s is missing" % path)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_csv(path):
    if not os.path.exists(path):
        raise Fail("%s is missing" % path)
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise Fail("%s is empty" % path)
    return rows


def require_files(*names):
    missing = [name for name in names if not os.path.exists(name)]
    if missing:
        raise Fail("missing: %s" % ", ".join(missing))


def require_notes(*headings):
    text = read_text("notes.md")
    missing = [heading for heading in headings if heading not in text]
    if missing:
        raise Fail("notes.md has no section: %s" % " | ".join(missing))


def read_pnm(path):
    text = read_text(path)
    lines = [line.split("#")[0] for line in text.splitlines()]
    tokens = " ".join(lines).split()
    if not tokens:
        raise Fail("%s is empty" % path)
    magic = tokens[0]
    if magic not in ("P1", "P2", "P3"):
        raise Fail("%s starts with %r; use the text formats P1, P2 or P3" % (path, magic))
    try:
        width = int(tokens[1])
        height = int(tokens[2])
    except (IndexError, ValueError):
        raise Fail("%s: the width and the height are missing from the header" % path)
    index = 3
    maxval = 1
    if magic in ("P2", "P3"):
        try:
            maxval = int(tokens[3])
        except (IndexError, ValueError):
            raise Fail("%s: the maximum value is missing from the header" % path)
        index = 4
    channels = 3 if magic == "P3" else 1
    needed = width * height * channels
    values = tokens[index:]
    if len(values) != needed:
        raise Fail("%s: the header says %dx%d, which needs %d values, but the file has %d"
                   % (path, width, height, needed, len(values)))
    try:
        numbers = [int(value) for value in values]
    except ValueError:
        raise Fail("%s contains a value that is not an integer" % path)
    for number in numbers:
        if number < 0 or number > maxval:
            raise Fail("%s has the value %d, outside 0..%d" % (path, number, maxval))
    return {"magic": magic, "width": width, "height": height,
            "maxval": maxval, "values": numbers, "path": path}


def find_frames(minimum=8):
    if not os.path.isdir("frames"):
        raise Fail("the frames/ directory is missing")
    names = sorted(name for name in os.listdir("frames") if name.endswith(".pgm"))
    if not names:
        raise Fail("frames/ has no .pgm files")
    bad = [name for name in names if not re.match(r"^frame_\d\d\.pgm$", name)]
    if bad:
        raise Fail("these names do not use two digits: %s" % ", ".join(bad[:3]))
    if len(names) < minimum:
        raise Fail("only %d frames; the animation needs at least %d" % (len(names), minimum))
    return ["frames/" + name for name in names]


def numbers_in(text):
    return [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", text)]


def require_gif(path):
    if not os.path.exists(path):
        raise Fail("%s is missing; build it with the convert command from the brief" % path)
    with open(path, "rb") as handle:
        head = handle.read(6)
    if not head.startswith(b"GIF8"):
        raise Fail("%s does not start with GIF8; is it really a GIF?" % path)


def scan_sources(forbidden):
    for name in sorted(os.listdir(".")):
        if not name.endswith(".py") or name == "check.py":
            continue
        with open(name, encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                code = line.split("#")[0]
                for token in forbidden:
                    if token in code:
                        warn("%s:%d uses %s; the brief asks for a different tool."
                             % (name, number, token))


def main():
    print("")
    print("Checking the project in %s" % os.getcwd())
    print("")
    passed = 0
    failed = 0
    for name, function in CHECKS:
        try:
            function()
        except Fail as error:
            failed += 1
            print("[fail] %s" % name)
            print("       %s" % error)
        except Exception as error:
            failed += 1
            print("[fail] %s" % name)
            print("       the check itself stopped: %s: %s" % (type(error).__name__, error))
        else:
            passed += 1
            print("[ok]   %s" % name)
    print("")
    for message in WARNINGS:
        print("[warn] %s" % message)
    if WARNINGS:
        print("")
    print("%d passed, %d failed" % (passed, failed))
    if failed:
        print("NOT READY YET - fix the [fail] lines above and run the script again.")
        return 1
    print("PROJECT READY - every automatic check passed. Show the program and notes.md.")
    return 0



def clips_data():
    rows = read_csv("clips.csv")
    if len(rows) < 9:
        raise Fail("clips.csv has %d lines; a header and eight clips are expected" % len(rows))
    clips = []
    for number, row in enumerate(rows[1:], start=2):
        if len(row) != 3:
            raise Fail("line %d has %d cells, three expected" % (number, len(row)))
        seconds = []
        for cell in (row[1], row[2]):
            parts = cell.strip().split(":")
            if len(parts) != 2:
                raise Fail("line %d: %r is not mm:ss" % (number, cell.strip()))
            try:
                minutes = int(parts[0])
                secs = int(parts[1])
            except ValueError:
                raise Fail("line %d: %r is not mm:ss" % (number, cell.strip()))
            seconds.append(minutes * 60 + secs)
        if seconds[1] <= seconds[0]:
            raise Fail("line %d ends before or when it starts" % number)
        clips.append((row[0].strip(), seconds[0], seconds[1]))
    return clips


@check("clips.csv has clips written as mm:ss")
def clips():
    clips_data()


@check("timeline.csv has the six columns and the arithmetic of every row")
def timeline():
    clips = clips_data()
    rows = read_csv("timeline.csv")
    header = [cell.strip().lower() for cell in rows[0]]
    expected = ["clip", "start", "end", "length", "start_s", "end_s"]
    if header != expected:
        raise Fail("timeline.csv header is %s; expected %s"
                   % (",".join(header), ",".join(expected)))
    if len(rows) - 1 != len(clips):
        raise Fail("timeline.csv has %d data rows, clips.csv has %d clips"
                   % (len(rows) - 1, len(clips)))
    for number, row in enumerate(rows[1:], start=2):
        if len(row) != 6:
            raise Fail("line %d of timeline.csv has %d cells, six expected"
                       % (number, len(row)))
        try:
            length = float(row[3])
            start_s = int(float(row[4]))
            end_s = int(float(row[5]))
        except ValueError:
            raise Fail("line %d of timeline.csv has a value that is not a number" % number)
        if end_s - start_s != length:
            raise Fail("line %d: %d - %d is not %g" % (number, end_s, start_s, length))
    for index, (name, start, end) in enumerate(clips):
        row = rows[index + 1]
        if int(float(row[4])) != start or int(float(row[5])) != end:
            raise Fail("row %d of timeline.csv does not match clip %s in clips.csv"
                       % (index + 2, name))


@check("timeline.txt reports the gaps and the overlaps")
def text_report():
    text = read_text("timeline.txt").lower()
    if "gap" not in text or "overlap" not in text:
        raise Fail("timeline.txt must name the gaps and the overlaps; "
                   "one of those words is missing")


@check("timeline.pbm is a 240 by 20 PBM strip")
def strip():
    image = read_pnm("timeline.pbm")
    if image["magic"] != "P1":
        raise Fail("timeline.pbm is %s; the strip uses the text PBM format P1"
                   % image["magic"])
    if (image["width"], image["height"]) != (240, 20):
        raise Fail("the strip is %dx%d; the brief asks for 240x20"
                   % (image["width"], image["height"]))


@check("notes.md has both research notes and the hand-checked clip")
def notes():
    require_notes("## The New Thing – a timestamp is not a number",
                  "## The New Thing – scaling to a strip",
                  "## Milestone 2 – one clip checked by hand")


scan_sources(["sum("])

if __name__ == "__main__":
    sys.exit(main())
