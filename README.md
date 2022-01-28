# old_chinese_ipa_extract

Extract Old Chinese IPA data from Wiktionary (Zhengzhang)

## Usage

The program is `real_extract.py`.

Run the program in Python 3.

In STDIN, delineate each Chinese character (Traditional) in EACH line.

So, one Chinese character at most per line.

## Output

```
>> 童
童,['doːŋ']
>> asdf
Single Chinese characters only!
>> 來
來,['m·rɯːɡ']
>> 王
王,['ɢʷaŋ', 'ɢʷaŋs']
```
