# Work in progress


import parasail
from rapidfuzz import fuzz
import pandas as pd
import re

pd.set_option('display.max_rows', None)

address_street_file = "address_street.csv"
address_number_file = "address_number.csv"


def preprocess_address_text(text):
    cleaned_text = text.replace('/', ' ').replace(',', '').lower()
    return cleaned_text

def words_with_digits(text):
    words = re.findall(r'\b\w+\b', text)
    digits = [word for word in words if any(char.isdigit() for char in word)]
    remaining_text = ' '.join(digits)
    return remaining_text



unclean_address = '367 george st sydney 2000'
unclean_address = preprocess_address_text(unclean_address)

print(unclean_address)
print('-'*50)

street_key = [
    '56b6c0b899d156c92a1bd84ec68b8060',
    'e21d3859b1ff06a1cff3c6d56bc6d54b',
    'ce0b95ffa0db1f6133542c6306161285',
    '566cd7d794a24ae648bb508b0d59bdc3',
    'd52ff517e8f2d6223a6ca19d542c9807',
    'b35f96600b740d1570d0d1187bfc0446',
    '6b2bef8b85baf605ee5daafdd1269c59',
    'bd1c6f0a6ee703b3dfcce0faff84b86d',
    '954860369c35a242e87fd652737d3fb9',
    '8f8e10abf362ac2e0644cf961e4f9f9e',
    '08b4dfc94433ca10b7053b4e34993009',
    'f979a0bc2df57bc43d990645ec5ce2c5',
    '85958f632bee826ec9a3cd0dc3cc1e02',
    'c63aef1a2a5d1192cbd5967dd0822cc8',
    'd598abb1cc832299858a5554d311a74e',
    '2895e71b5266623899e816156f313201',
    'd471df60569d9378b7f6bfeb5d746244',
    '2682baa505fe9e86e62c5f724cedb90d',
    'd222154c05722d6fb5311a05bf193529',
    '366808a3e6155a1451ae329348e870a5',
    ]


street_df = pd.read_csv(address_street_file, dtype='string')
number_df = pd.read_csv(address_number_file, dtype='string')

match_df = (
    street_df[street_df['street_key'].isin(street_key)]
    .set_index('street_key')
    .reindex(street_key)
    .reset_index()
    )


matrix = parasail.matrix_create('abcdefghijklmnopqrstuvwxyz0123456789 ', match=5, mismatch=-1)

def fuzzy_match_street(clean_address):
    results = parasail.ssw(unclean_address, clean_address, 4, 1, matrix)
    reduced = unclean_address[results.read_begin1:results.read_end1+1]
    fuzzy_match_score = fuzz.ratio(reduced, clean_address)
    remaining_address = (unclean_address[:results.read_begin1] + unclean_address[results.read_end1+2:]).strip()
    return pd.Series([fuzzy_match_score, remaining_address])


match_df[['street_score', 'remaining_address']] = match_df['full_street'].apply(fuzzy_match_street)
print(match_df)


print('-' * 50)

# I think I should use max above certain score
key = match_df.loc[match_df['street_score'].idxmax(), 'street_key']
remaining_address = match_df.loc[match_df['street_score'].idxmax(), 'remaining_address']


street_number_set_df = number_df[(number_df['street_key'] == key)].copy()


def number_match_function(text):
    token_match_score = fuzz.token_sort_ratio(words_with_digits(remaining_address), words_with_digits(text))
    match_score = fuzz.partial_ratio(remaining_address, text)
    final_score = 0.6*token_match_score + 0.4*match_score
    return final_score


street_number_set_df['number_score'] = street_number_set_df['full_number'].apply(number_match_function)

street_number_set_df = street_number_set_df[street_number_set_df['number_score'] > 60].sort_values('number_score', ascending=False).reset_index()

print(street_number_set_df)
