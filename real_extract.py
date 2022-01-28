import json
import shutil
import sys
import traceback
import unicodedata

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


# Create an HTTP session
def http() -> requests.Session:
    sesh = requests.Session()
    sesh.mount("http://", HTTPAdapter(max_retries=2))
    sesh.mount("https://", HTTPAdapter(max_retries=2))
    return sesh


# Download the HTTP file from Wiktionary
def wikt(sesh: requests.Session, word: str) -> BeautifulSoup:
    response = sesh.get(f"https://en.wiktionary.org/wiki/{word}?printable=true")
    soup = BeautifulSoup(response.text.replace(">\n<", "><"), "html.parser")
    return soup


# Analyze the text for all Zhengzhang reconstructions (if any).
def zhengzhang(soup: BeautifulSoup) -> [str]:
    try:
        # Identify a parent div whose descendant contains the text "Old Chinese"
        # (The parent div is specified)
        parent = soup.select(
            "#mw-content-text > div.mw-parser-output > div.toccolours.zhpron li"
        )
        child = filter(lambda entry: "Old Chinese" in entry.text, parent)

        # Only choose those whose descendants contain the string "Zhengzhang"
        children = map(
            lambda dd: list(
                filter(lambda entry: "Zhengzhang" in entry.text, dd.select("dd"))
            ),
            child,
        )

        # Now, flatten everything and filter the text
        def flatten(t):
            return [item for sublist in t for item in sublist]

        ipas = map(lambda e: e.select("span.IPAchar"), flatten(children))
        ipas = flatten(map(lambda t: list(map(lambda e: str(e.text), t)), ipas))

        # Separate by comma and then remove spaces
        ipas = flatten(map(lambda s: s.split(","), ipas))
        ipas = map(lambda s: s.strip(), ipas)

        # Remove "unattested/reconstruction" symbols /* and /
        ipas = map(lambda e: e[2:-1], ipas)

        # Normalize
        ipas = map(lambda e: unicodedata.normalize("NFC", e), ipas)

        # Export
        return list(ipas)
    except:
        print("error")
        return []


# Suppose stdin contains the chinese characters line by line.
# Many characters per line
if __name__ == "__main__":
    print("Help: Line-by-line operation.")
    print("Help: Will print the possible pronunciations for each Chinese character")
    print("Help: And then, machine will convert the entire line into IPA pronunciation")
    print("Help: Formats: ")
    print("Help: [Line|Pronounce|IPA|Ignoring] %d: %s")
    print("Help: %d = line number from 1, %s = message")
    print(
        "Help: Will also output a dictionary as cache; CLEARED upon OPENING! BACK IT UP!"
    )

    line_no = 1
    ipa_cache = dict()
    sesh = http()

    # Back up the dictionary
    try:
        shutil.copyfile("dict.json", "dict.backup.json")
    except FileNotFoundError:
        pass
    finally:
        open("dict.json", "a").close()

    try:
        with open("dict.json", "r") as ipa_cache_file:
            try:
                ipa_cache = json.load(ipa_cache_file)
                print("`dict.json` was successfully parsed; thank you.")
            except:
                print(
                    "No dictionary `dict.json` was found or it was unusable; it's a-ok."
                )
            finally:
                ipa_cache_file = open("dict.json", "w")

            for line in sys.stdin:
                try:
                    # First, normalize the line according to Composition
                    unicodedata.normalize("NFC", line)

                    # Get rid of newline
                    line = line[:-1]

                    for ch in line:
                        ipas = None
                        if ch not in ipa_cache.keys():
                            web = wikt(sesh, ch)
                            ipas = zhengzhang(web)
                            ipa_cache[ch] = ipas
                        else:
                            ipas = ipa_cache[ch]
                        print(f"IPA {line_no}: {ch},{ipas}")

                    # Compose the text
                    ipa_print = []

                    for ch in line:
                        if ch not in ipa_cache.keys() or ipa_cache[ch] == []:
                            ipa_print.append(ch)
                        else:
                            ipas = ipa_cache[ch]
                            if len(ipas) == 1:
                                ipa_print.append(ipas[0])
                            else:
                                ipa_print.append(f"{ipas[0]}*")

                    print(f"Line {line_no}: {line}")
                    print(f"Pronounce {line_no}: {' '.join(ipa_print)}")
                except KeyboardInterrupt:
                    break
                except Exception:
                    print(f'Ignoring {line_no}: "{line}"')
                    traceback.format_exc()
                    pass
                finally:
                    line_no += 1
    except KeyboardInterrupt:
        pass
    finally:
        json.dump(ipa_cache, ipa_cache_file, indent=2)
