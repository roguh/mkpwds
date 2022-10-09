# 4 words, 4 characters each, numbers, all lowercase, common words?, no repeats
# names are capitalized... TODO extend wordlist with capitalized Proper Nouns e.g. Paris Bob ...
import json
import math
import string
from datetime import timedelta, datetime
from os.path import basename
from typing import Callable, Collection, Optional, Set, Union

# chadistry
# Bobthecool1*
# pogger69*
# pogger69

Filter = Callable[[Set[str]], Set[str]]

naturaltime = None
try:
    from humanize import naturaltime
except ImportError:
    pass

numbers = set(str(i) for i in range(10))

valid_wpa_symbols = set("""1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?><":;(' ')""")

valid_wpa_symbols_no_alpha = valid_wpa_symbols.difference(set(string.ascii_letters))

valid_wpa_symbols_no_digits = valid_wpa_symbols.difference(set(string.digits))

alpha_and_digits = set(string.ascii_letters + string.digits)

digits = set(string.digits)

mega_hint = set('1*')

def length_6(words: Set[str]) -> Set[str]:
    return set(word for word in words if len(word) == 6)

def max_length(words: Set[str], max_length: int) -> Set[str]:
    return set(word for word in words if len(word) <= max_length)

def max_length_4(words: Set[str]) -> Set[str]:
    return max_length(words, max_length=4)

def no_spaces(words: Set[str]) -> Set[str]:
    return set(word for word in words if ' ' not in word)


def union_and_filter(sets: Collection[Set[str]], filters: Collection[Filter]) -> int:
    candidate_words = set.union(*sets)
    for filter_ in filters:
        candidate_words = filter_(candidate_words)
    return candidate_words

def count_candidates(candidate_words: Set[str], word_count: int=4) -> int:
    return len(candidate_words) ** word_count, math.perm(len(candidate_words), word_count)

def seconds_to_crack(count: int) -> float:
    # GTX 670 in 2017
    # https://forums.hak5.org/topic/40736-aircrack-speed/
    return count / 160_000

def show_time(count: int) -> str:
    seconds = seconds_to_crack(count)
    try:
        dt = timedelta(seconds=seconds)
        if naturaltime:
            return naturaltime(datetime.now() + dt)
        return str(dt)
    except OverflowError as exc:
        years = seconds / 60 / 60 / 24 / 364.25
        return f'{years:,} years (overflow! {str(exc).split()[0]})'



def analyze(candidate_words: Set[str], word_count: int=4, name: Optional[str]=None) -> None:
    print('=' * 10, name if name else '---', '=' * 10, end='    ')
    count, count_no_repeats = count_candidates(candidate_words, word_count=word_count)
    print('word count:', len(candidate_words),
          'total possibilities:', f'{count:,}',
          'no repeats:', f'{count_no_repeats:,}', end='    ')
    print(f'{show_time(count)}')
    # print('no repeats time:', f'{show_time(count_no_repeats)}')


def analyze_many(words: Set[str], filters: Collection[Filter]=(), name: str='?', word_counts: Collection[int]=(2, 3, 4, 5, 6, 10, 15)) -> None:
    filters_str = '-'.join([f.__name__ for f in filters])
    for extra_symbols in [valid_wpa_symbols, valid_wpa_symbols_no_alpha, valid_wpa_symbols_no_digits, alpha_and_digits, digits]:
        candidates = union_and_filter([words, extra_symbols], filters)
        print()
        for word_count in word_counts:
            analyze(
                candidates,
                word_count=word_count,
                name=f'{word_count}__{len(extra_symbols)}syms_{name}_{filters_str}'
            )

def analyze_wordlist(fnames: Union[str, Collection[str]], filters: Collection[Filter]=()):
    if isinstance(fnames, (str, bytes)):
        fname_str = basename(fnames)
        fnames = [fnames]

    words = set()
    valid_fnames = []
    for fname in fnames:
        try:
            with open(fname) as f:
                words = words.union(set(f.readlines()))
            valid_fnames.append(fname)
        except OSError:
            print("error opening file", fname)
    fname_str = '-'.join(basename(fname) for fname in valid_fnames)

    for common_ending in ['.data', '.json', '.txt']:
        fname_str = fname_str.replace(common_ending, '')

    if len(words) == 0:
        return
    analyze_many(words, filters, fname_str)


def main():
    analyze_many(set(), name='all', word_counts=[2, 5, 8, 12, 20, 64])
    analyze_wordlist('google-10000-english-usa-no-swears-short.txt')
    analyze_wordlist('google-10000-english/google-10000-english.txt')
    analyze_wordlist('google-10000-english/google-10000-english.txt')
    analyze_wordlist('google-10000-english/google-10000-english.txt', [max_length_4])
    analyze_wordlist('english-words/words.txt', [no_spaces])
    analyze_wordlist('urban-dictionary-word-list/data/P.data', [no_spaces, length_6])
    analyze_wordlist([f'urban-dictionary-word-list/data/{letter}.data' for letter in string.ascii_uppercase], [no_spaces, length_6])

main()
