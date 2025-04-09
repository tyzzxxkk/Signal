import re

BAD_WORDS = [
    '바보', '멍청이', '나쁜놈', '욕', '나쁜말'
]

def filter_bad_words(text):
    for word in BAD_WORDS:
        text = re.sub(word, '*' * len(word), text)
    return text
