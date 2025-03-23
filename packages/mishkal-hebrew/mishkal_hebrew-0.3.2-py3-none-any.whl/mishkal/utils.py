import re
from mishkal.phonemize import Letter
from mishkal import vocab
import unicodedata

NORMALIZE_PATTERNS = {
    # Alphabet followed by 1/2 symbols then dagesh. make dagesh first
    "([\u05d0-\u05ea])([\u05b0-\u05c7]{1,2})(\u05bc)": r"\1\3\2",
    r"([^בכךפףו])(\u05bc)": r"\1",
}


def remove_niqqud(text: str):
    return re.sub(vocab.HE_NIQQUD_PATTERN, "", text)


def has_niqqud(text: str):
    return re.search(vocab.HE_NIQQUD_PATTERN, text) is not None


def normalize(text: str) -> str:
    """
    Normalize unicode (decomposite)
    Deduplicate niqqud (eg. only Patah instead of Kamatz)
    Keep only Hebrew characters / punctuation / IPA
    """
    # Decompose text

    text = unicodedata.normalize("NFD", text)
    for k, v in NORMALIZE_PATTERNS.items():
        text = re.sub(k, v, text)
    # Normalize niqqud, remove duplicate phonetics 'sounds' (eg. only Patah)
    for k, v in vocab.NIQQUD_NORMALIZE.items():
        text = text.replace(k, v)

    # Keep only lexicon characters
    text = "".join(
        [
            c
            for c in text
            if c in vocab.SET_INPUT_CHARACTERS or c in vocab.SET_OUTPUT_CHARACTERS
        ]
    )
    return text


def extract_letters(word: str) -> list[Letter]:
    """
    Extract letters from word
    We assume that:
        - Dates expanded to words
        - Numbers expanded to word
        - Symbols expanded already
        - Known words converted to phonemes
        - Rashey Tavot (acronyms) expanded already
        - English words converted to phonemes already
        - Text normalized using unicodedata.normalize('NFD')

    This function extract *ONLY* hebrew letters and niqqud from LEXICON
    Other characters ignored!
    """
    # Normalize niqqud
    for niqqud, normalized in vocab.NIQQUD_NORMALIZE.items():
        word = word.replace(niqqud, normalized)
    # Remove non-lexicon characters
    word = "".join([c for c in word if c in vocab.SET_INPUT_CHARACTERS])
    letters = []
    i = 0
    while i < len(word):
        char = word[i]
        if char in vocab.SET_LETTERS or char == "'":
            symbols = []
            i += 1  # Move to potential niqqud
            # Collect symbols attached to this letter
            while i < len(word) and (
                word[i] in vocab.SET_LETTER_SYMBOLS or word[i] == "'"
            ):
                symbols.append(word[i])
                i += 1  # Move to the next character

            if char in "בכפ" and "\u05bc" in symbols:
                char += "\u05bc"  # Add dagesh to the letter itself
            if (
                "\u05bc" in symbols and char not in "ו"
            ):  # we'll keep dagesh symbol only for vav
                symbols.remove("\u05bc")  # remove dagesh
            # Shin
            if "\u05c1" in symbols:
                char += "\u05c1"
                symbols.remove("\u05c1")
            # Sin
            if "\u05c2" in symbols:
                char += "\u05c2"
                symbols.remove("\u05c2")
            letters.append(Letter(char, set(symbols)))
        else:
            i += 1  # Skip non-letter symbols
    return letters


def get_unicode_names(text: str):
    return [unicodedata.name(c, "?") for c in text]
