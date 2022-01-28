import re, requests
from bs4 import BeautifulSoup


def extract_zhprons(soup):
    ul = soup.select('#mw-content-text > div.mw-parser-output > div.toccolours.zhpron li')
    occ = list(filter(lambda entry: re.search('Old Chinese', entry.text), ul))[0]

    # Right. Now, only choose the dd objects with 'Zhengzhang'.

    occ = map(lambda q: list(filter(lambda entry: re.search('Zhengzhang', entry.text), q)), occ)

    def fl(t):
        return [item for sublist in t for item in sublist]

    ipacharspans = map(lambda e: e.select('span.IPAchar'), fl(occ))
    spans = list(map(lambda t: list(map(lambda e: e.string, t)), ipacharspans))
    return fl(spans)


def mkses():
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
    return session


def cchar(ses, cc):
    response = ses.get(f"https://en.wiktionary.org/wiki/{cc}?printable=true")
    soup = BeautifulSoup(response.text.replace('>\n<', '><'), 'html.parser')
    return soup


def flatten(t):
    return [item for sublist in t for item in sublist]


def prog(ses, c):
    s = cchar(ses, c)
    l = extract_zhprons(s)

    # Remove /* ... / [first, second and last characters]
    l = list(map(lambda e: e[2:-1], l))
    return l


s = mkses()


prog(s, "鴽")

#%%

prog(s, "王")
#%%


prog(s, "魚")

#%%
