# Project – Edit Timeline

**Individual Project Brief – Week 6 · u09**

Start: Monday, 16 November 2026. Show the working program on Monday, 23 November 2026.

## The Idea

You build a program that reads your edit list and draws it. `clips.csv` holds the clips of a short video: name, start and end, written the way a video editor shows them, `00:12` and `01:05`. The program converts those times to seconds, computes the length of every clip, finds gaps and overlaps between them, adds up the whole timeline, and writes it as a strip of blocks in a PBM picture — one block per clip, scaled so that the longest film fits in two hundred and forty pixels.

This is a plan you can look at. A list of numbers is hard to judge; a strip shows immediately that the intro is too long and that two clips overlap by four seconds.

## Why This Project Is Yours

You edit clips in DaVinci Resolve, you ride a bike and play basketball, and you said you want something useful — something that turns into knowledge or into money, not an exercise that ends in a folder. A timeline checker is small but real: it does arithmetic that a video editor does silently, and it shows you the result in a form you already understand from the editing program. The project is also about order and fit, in time instead of in a case: every clip must start after the previous one ends, and the program is the thing that checks it.

## What You Already Have

- Lists, indexing, slices, `for` loops and `while`.
- Conditions, comparisons, `//` and `%`, and `%s`, `%d` formatting.
- Reading and writing files with `with`, and the PBM format: `P1`, then a grid of `0` and `1`.
- Terminal and `git` habits from the first weeks.

## The New Thing

A timestamp is text that behaves like a number. Find out how to:

1. Split `01:05` into two parts and convert both to integers.
2. Turn minutes and seconds into seconds, and turn seconds back into `mm:ss` with `//` and `%`.
3. Multiply seconds by a scale factor without losing the last block, and what `int()` does to `4.9`.
4. Decide what to do with a clip that is zero seconds long.
5. Compare an end time with the next start time and tell a gap from an overlap.
6. Choose whether to round a scaled bar up or down, and which choice leaves the picture truthful.

**Write it down:** Create `notes.md` with `## The New Thing – a timestamp is not a number`. Explain the conversion in both directions in four sentences, with one example of each. Add `## The New Thing – scaling to a strip` with the formula you used, and one sentence about what your program does when a clip is shorter than one block.

## The Plan

### Milestone 1 – The edit list

Create `clips.csv` by hand.

1. Three columns: `clip,start,end`. Use `mm:ss` for the times, in order, starting at `00:00`.
2. Eight clips, about three minutes in total. One gap of a few seconds and one overlap of a few seconds, on purpose.
3. Include one clip of one second, so that the smallest block has to be handled.

### Milestone 2 – Time to seconds

Create `timeline.py`.

1. Read the file and print every row with its line number.
2. Split the timestamps on `:` and convert both parts to integers.
3. Print every clip with its start and end in seconds, and its length.
4. Check one clip by hand and write the result in `notes.md`.

At the end of this step the terminal shows `00:12` next to `12` and you trust the conversion.

### Milestone 3 – Check the fit

1. Compare the end of every clip with the start of the next one.
2. Print `gap` with the number of seconds, `overlap` with the number of seconds, or `ok`.
3. Count the problems and print the total number of seconds lost to gaps and overlaps.
4. Do not stop at the first problem: one run must report all of them.

At the end of this step the report names the two broken places in your file.

### Milestone 4 – The total

1. Sum the clip lengths with a loop. Do not use `sum()`.
2. Print the total as `mm:ss` and as seconds, and check that both agree.
3. Print the total length of the timeline from the first start to the last end, gaps included.
4. Print the share of the timeline that is actually used, with one decimal.

### Milestone 5 – The strip

1. Create `timeline.pbm`, two hundred and forty pixels wide and twenty pixels high.
2. Give every clip a block whose width is proportional to its length, and one white pixel between blocks.
3. Fill the block with `1`, and leave the space of a gap empty.
4. Print the strip to the terminal with `#` and `.` and compare it with the numbers in Milestone 4.

### Milestone 6 – Two files out

1. Write `timeline.csv` with `clip,start,end,length,start_s,end_s` and one row per clip.
2. Write `timeline.txt` — a table aligned with field widths, with the problems listed under it.
3. Read `timeline.csv` back and print the number of rows and the total length from the file alone.
4. Make sure that changing one timestamp in `clips.csv` changes the picture without editing the code.

## Example

```text
Reading clips.csv
 1  intro          00:00  00:14   length 14 s
 2  city_wide      00:14  00:31   length 17 s
 3  bike_close     00:31  00:52   length 21 s
 4  hands          00:52  01:04   length 12 s
 5  title          01:04  01:06   length  2 s
 ...

Fit check
  clip 1 -> 2: ok
  clip 2 -> 3: ok
  clip 3 -> 4: gap 4 s
  clip 4 -> 5: ok
  ...
  clip 7 -> 8: overlap 3 s

8 clips, 2 problems, 4 s unused, 3 s doubled
Total length: 02:41 (161 s)
Timeline span: 02:42 (162 s)
Used: 99.4%

timeline.pbm (240x20), the strip wrapped here
########################################################################........
############################################################################
```

The numbers in the picture are an example. Your clips decide your picture.

## Requirements

- One program, `timeline.py`, started from the terminal with `python3 timeline.py`.
- Timestamps are parsed from the text with `split(":")`, never typed in as seconds.
- Durations and totals are computed with loops, not with `sum()`.
- Every clip appears in the strip, including the one-second clip, which must be at least one pixel wide.
- Gaps and overlaps are both reported, with the clip numbers that cause them.
- `timeline.csv` is written with the `csv` module and can be re-read by the same program.
- The strip is a valid PBM file with a correct header.

## Files

```text
edit_timeline/
├── clips.csv
├── timeline.py
├── timeline.csv
├── timeline.txt
├── timeline.pbm
├── notes.md
└── check.py
```

Commit the whole directory to your repository and push it before the Monday session. A directory that exists only on your laptop cannot be checked.

Run `python3 check.py` in the project directory before you commit. It reads the files your program produced, not your code, and prints one line per requirement.


## How It Will Be Checked

- Every duration equals `end - start` in seconds.
- The sum of the durations plus the gaps equals the span of the timeline.
- The reported gap and overlap seconds match the file, not the program's opinion.
- The block widths in the strip are proportional to the durations, and one block is visibly the smallest.
- Changing one timestamp changes the totals, the CSV and the picture together.
- You can explain the scale factor of the strip in one sentence.

**Hint:** Convert once, at the moment you read the row, and keep the seconds in the list. Every later step — duration, gap, total, strip — works on numbers. A program that mixes seconds and `mm:ss` strings will eventually subtract a string from a number.

**Additional challenge:** Add a second row of blocks to the strip for a second version of the edit — the same clips in a different order — and compare the two timelines in one picture. Write one sentence in `notes.md` about which version has fewer gaps and why a program can answer that faster than an editor.

## Suggested Learning Resources

- [Numbers and whole division – `//` and `%`](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)
- [String methods – `split` and `strip`](https://docs.python.org/3/library/stdtypes.html#string-methods)
- [The `csv` module – reading and writing tabular data](https://docs.python.org/3/library/csv.html)
- [Netpbm – description of the PBM format](https://netpbm.sourceforge.net/doc/pbm.html)

**Final goal:** By the end of this project, you should have a program that turns timestamps into seconds, checks the fit of an edit list, summarizes the timeline, and draws it as a PBM strip — using loops, conditions, lists, arithmetic and file handling from the first five weeks.
