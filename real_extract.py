import sys
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
def wikt(sess: requests.Session, word: str) -> BeautifulSoup:
    response = sess.get(f"https://en.wiktionary.org/wiki/{word}?printable=true")
    soup = BeautifulSoup(response.text.replace('>\n<', '><'), 'html.parser')
    return soup


# Analyze the text for all Zhengzhang reconstructions (if any).
def zhengzhang(soup: BeautifulSoup) -> [str]:
    try:
        # Identify a parent div whose descendant contains the text "Old Chinese"
        # (The parent div is specified)
        parent = soup.select('#mw-content-text > div.mw-parser-output > div.toccolours.zhpron li')
        child = filter(lambda entry: "Old Chinese" in entry.text, parent)

        # Only choose those whose descendants contain the string "Zhengzhang"
        children = map(
            lambda dd:
                list(filter(
                    lambda entry:
                        'Zhengzhang' in entry.text,
                    dd.select('dd'))),
            child)

        # Now, flatten everything and filter the text
        def flatten(t):
            return [item for sublist in t for item in sublist]

        ipas = map(lambda e: e.select('span.IPAchar'), flatten(children))
        ipas = flatten(map(lambda t: list(map(lambda e: str(e.text), t)), ipas))

        # Separate by comma and then remove spaces
        ipas = flatten(map(lambda s: s.split(','), ipas))
        ipas = map(lambda s: s.strip(), ipas)

        # Remove "unattested/reconstruction" symbols /* and /
        ipas = map(lambda e: e[2:-1], ipas)

        # Export
        return list(ipas)
    except:
        print("error")
        return []


# Suppose stdin contains the chinese characters line by line.
# One character per line.
if __name__ == '__main__':
    ipa_cache = dict()
    sesh = http()

    for line in sys.stdin:
        try:
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
                print(f"{ch},{ipas}")
        except KeyboardInterrupt as ke:
            exit(0)
        except:
            print(f"Ignoring: \"{line}\"", file=sys.stderr)
            pass

#%%
