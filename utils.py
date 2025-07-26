# Take unclean address and closest match from faiss and determine the closest matching address

import parasail
from rapidfuzz import fuzz
import pandas as pd
import re


def build_indexes(street_df, number_df):
    street_by_key = dict(zip(street_df.street_key, street_df.full_street))
    keys = list(street_by_key.keys())
    streets = [street_by_key[k] for k in keys]
    numbers_by_key = (
        number_df.groupby("street_key")["full_number"]
        .apply(list)
        .to_dict()
    )
    return keys, streets, street_by_key, numbers_by_key


def preprocess_address_text(text):
    cleaned_text = text.replace('/', ' ').replace(',', '').lower()
    return cleaned_text


def words_with_digits(text):
    words = re.findall(r'\b\w+\b', text)
    digits = [word for word in words if any(char.isdigit() for char in word)]
    remaining_text = ' '.join(digits)
    return remaining_text


matrix = parasail.matrix_create('abcdefghijklmnopqrstuvwxyz0123456789 ', match=5, mismatch=-1)

def best_street_match(unclean_address, streets):
    best_score = -1
    best_idx = None
    best_substring = None
    for i, candidate in enumerate(streets):
        result = parasail.ssw(unclean_address, candidate, 4, 1, matrix)
        reduced = unclean_address[result.read_begin1: result.read_end1 + 1]
        fuzzy_score = fuzz.ratio(reduced, candidate, score_cutoff=50)
        # print(f"{candidate}: {fuzzy_score}")
        if fuzzy_score > best_score:
            best_score = fuzzy_score
            best_idx = i
            best_substring = reduced
    return best_idx, best_score, best_substring


def best_number_match(remaining_address, numbers):
    best_score = -1
    best_idx = None
    for i, candidate in enumerate(numbers):
        # remaining_digits = words_with_digits(remaining_address)
        # token_match_score = fuzz.token_sort_ratio(remaining_digits, words_with_digits(text), score_cutoff=50)
        if pd.isna(candidate):
            continue
        token_match_score = fuzz.token_sort_ratio(words_with_digits(remaining_address), words_with_digits(candidate), score_cutoff=50)
        match_score = fuzz.partial_ratio(remaining_address, candidate, score_cutoff=50)
        final_score = 0.6*token_match_score + 0.4*match_score
        # print(f"{candidate}: {final_score}")
        if final_score > best_score:
            best_score = final_score
            best_idx = i
    return best_idx, best_score


def best_address_match(unclean_address, indices, keys, street_by_key, numbers_by_key):
    street_keys = [keys[j] for j in indices.tolist()]
    address_street_list = [street_by_key[key] for key in street_keys]
    street_idx, street_score, street = best_street_match(unclean_address, address_street_list)
    if street_score < 70:
        return None
    # print(street_keys[street_idx])
    address_number_list = numbers_by_key[street_keys[street_idx]]
    if all(pd.isna(x) for x in address_number_list):
        return f"{address_street_list[street_idx]}"
    remaining_address = unclean_address.replace(street, '').strip()
    # print(remaining_address)
    # print(address_number_list)
    number_idx, _ = best_number_match(remaining_address, address_number_list)
    # print(number_idx)
    return f"{address_number_list[number_idx]} {address_street_list[street_idx]}"
