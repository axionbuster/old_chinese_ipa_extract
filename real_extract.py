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

        # Remove "unattested/reconstruction" symbols /* and /
        ipas = list(map(lambda e: e[2:-1], ipas))
        return ipas
    except:
        print("error")
        return []


# Suppose stdin contains the chinese characters line by line.
# One character per line.
if __name__ == '__main__':
    ipa_cache = dict()
    sesh = http()

    for line in sys.stdin:
        # Get rid of newline at the end
        line = line[:-1]

        # Make sure only single characters are admitted
        if len(line) != 1:
            print("Single Chinese characters only!")
            continue

        ipas = None
        if line not in ipa_cache.keys():
            web = wikt(sesh, line)
            ipas = zhengzhang(web)
            ipa_cache[line] = ipas
        else:
            ipas = ipa_cache[line]
        print(f"{line},{ipas}")
