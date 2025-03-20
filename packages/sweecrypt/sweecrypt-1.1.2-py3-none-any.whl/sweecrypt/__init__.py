__version__ = "1.1.2"
db = {
    'a': '`',
    'b': '-',
    'c': ')',
    'd': '/',
    'e': '?',
    'f': '^',
    'g': '#',
    'h': '!',
    'i': ';', 
    'j': '.',
    'k': '\\',
    'l': '~', 
    'm': '&', 
    'n': '*',
    'o': '(',
    'p': '@', 
    'q': '"',
    'r': '>', 
    's': '<', 
    't': '[', 
    'u': ']', 
    'v': '{',
    'w': '}', 
    'x': '|',
    'y': '+', 
    'z': '_', 
    ' ': ',', 
    ',': ':', 
    '.': '=', 
    '!': 'a', 
    '?': 'b',
    '\n': 'c', 
    "'": 'd', 
    '(': 'e', 
    ')': 'f', 
    '1': 'g', 
    '2': 'h', 
    '3': 'i', 
    '4': 'j',
    '5': 'k',
    '6': 'l', 
    '7': 'm', 
    '8': 'n', 
    '9': 'o', 
    '0': 'p', 
    '-': 'q', 
    '&': 'r', 
    ':': 's', 
    ';': 't', 
    '"': 'u', 
    '\\': 'v',
    '/': 'w',
    "~": "x"
}

db2 = {v: k for k, v in db.items()}

def encrypt(s, shift=0):
    tempdb = dict(zip(list(db.keys()), list(db.values())[shift:] + list(db.values())[:shift])) if shift else db
    encoded = ""
    s = s.lower()
    for i in s:
        encoded += tempdb.get(i, "")
    return encoded


def decrypt(s, shift=0):
    if shift:
        shift = shift * -1
    tempdb = dict(zip(list(db2.keys()), list(db2.values())[shift:] + list(db2.values())[:shift])) if shift else db2
    decoded = ""
    for i in s:
        decoded += tempdb.get(i, "")
    return decoded
