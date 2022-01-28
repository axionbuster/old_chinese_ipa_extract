# old_chinese_ipa_extract

Extract Old Chinese IPA data from Wiktionary (Zhengzhang)

## Usage

The program is `real_extract.py`.

Run the program in Python 3.

Simple Usage:

```
> python3 real_extract.py
>> (enter text line by line)
```

Advanced Usage:

```
> time python3 real_extract.py < shijing-luming.txt > out.txt 2> err.txt
python3 real_extract.py < shijing-luming.txt > out.txt 2> err.txt  7.77s user 0.16s system 31% cpu 24.836 total
> time python3 real_extract.py < shijing-luming.txt > out.txt 2> err.txt
python3 real_extract.py < shijing-luming.txt > out.txt 2> err.txt  0.14s user 0.03s system 90% cpu 0.189 total
```

This program caches the results on disk so the second time you run it it only takes a fraction of the time.

## Output

```
>> 呦呦鹿鳴、食野之苹。
IPA 1: 呦,['qrɯw']
IPA 1: 呦,['qrɯw']
IPA 1: 鹿,['b·roːɡ']
IPA 1: 鳴,['mreŋ']
IPA 1: 、,[]
IPA 1: 食,['ɦljɯɡ', 'lɯɡs']
IPA 1: 野,['laːʔ', 'ɦljaʔ']
IPA 1: 之,['tjɯ']
IPA 1: 苹,['beŋ']
IPA 1: 。,[]
Line 1: 呦呦鹿鳴、食野之苹。
Pronounce 1: qrɯw qrɯw b·roːɡ mreŋ 、 ɦljɯɡ* laːʔ* tjɯ beŋ 。
```

* If the Chinese character (or non-Chinese character) didn't have a Zhengzhang pronunciation, it's printed verbatim.
* If the Chinese character had one ZZ pronunciation, the IPA representation is printed.
* If it had more than one pronunciation, the first pronunciation (as in the English Wiktionary) is printed, then it's prefixed by an asterisk.

## Caching

The IPA database (from Chinese characters, Traditional, to IPA) is stored in `dict.json`.

Backups are made in `dict.backup.json` by simply copying.

## Standard Output and Error Streams

The standard output contains lines that are of the following form:

```
LINE = HELPLINE | OTHERLINES
HELPLINE = "Help: " string
OTHERLINES = PREFIX " " number ": " string
PREFIX = "Line" | "Pronounce" | "IPA" | "Ignoring"
```

Examples:

```
>> asdf
Ignoring 1: asdf
>> asdfasdf
Ignoring 2: asdfasdf
```

The numbers after `PREFIX` are line numbers. The first line has line number 1.

You can then use scanf or regex to parse the output.
