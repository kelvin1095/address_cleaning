# Generate training data for model

import pandas as pd
import random
from faker import Faker

address_fields_file = "address_fields.csv"

random.seed(42)
fake = Faker(['en_AU'])

def introduce_typo(text, typo_prob=0.02):
    chars = list(text)
    if random.random() < typo_prob:
        pos = random.randint(0, len(text) - 1) if text else 0
        typo_type = random.choice(['swap', 'delete', 'replace'])
        if typo_type == 'swap' and pos < len(chars) - 1 and chars[pos+1].isalpha():
            chars[pos], chars[pos+1] = chars[pos+1], chars[pos]
        elif typo_type == 'delete':
            del chars[pos]
        elif typo_type == 'replace':
            chars[pos] = random.choice('abcdefghijklmnopqrstuvwxyz')
    return ''.join(chars)

def add_individual_company_name(text, name_prob=0.05):
    if random.random() < name_prob:
        name_type = random.choice(['individual', 'company'])
        if name_type == 'individual':
            return fake.name() + " " + text
        else:
            return fake.company() + " " + text
    return text


header_type = {
    'address_detail_pid': 'string',
    'street_key': 'string',
    'flat_type_code': 'string',
    'flat_type_name': 'string',
    'flat_number': 'string',
    'level_type_code': 'string',
    'level_type_name': 'string',
    'level_number': 'string',
    'street_number': 'string',
    'street_name': 'string',
    'street_type_code': 'string',
    'street_type_name': 'string',
    'street_suffix_code': 'string',
    'street_suffix_name': 'string',
    'locality_name': 'string',
    'state': 'string',
    'postcode': 'string',
    'country': 'string'
}
null_values = ['NULL', '']
address_df = pd.read_csv(address_fields_file, dtype=header_type, na_filter=null_values)

train_df = address_df.sample(n=20000, random_state=42).reset_index(drop=True)

address_fields = [
    'flat_type_name',
    'flat_number',
    'level_type_name',
    'level_number',
    'street_number',
    'street_name', 
    'street_type_name',
    'street_suffix_name',
    'locality_name', 
    'state', 
    'postcode'
    ]


train_df['full_address'] = (
    train_df[address_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)

address_fields = [
    'street_name', 
    'street_type_name',
    'street_suffix_name',
    'locality_name', 
    'state', 
    'postcode',
    'country'
    ]


train_df['street_identifier'] = (
    train_df[address_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)


train_df['street_name'] = train_df['street_name'].apply(lambda x: introduce_typo(x, typo_prob=0.05))
train_df['locality_name'] = train_df['locality_name'].apply(lambda x: introduce_typo(x, typo_prob=0.05))

train_df["flat_type_random"] = train_df.apply(
    lambda row: (
        '' if pd.isna(row["flat_type_name"])
        else '' if row["flat_type_name"] == "UNIT" and random.random() < 0.4
        else row["flat_type_name"] if random.random() < 0.4
        else row["flat_type_code"]
    ),
    axis=1
)

train_df["level_type_random"] = train_df.apply(
    lambda row: row["level_type_name"] if random.random() < 0.4 else row["level_type_code"],
    axis=1
)

train_df["street_type_random"] = train_df.apply(
    lambda row: row["street_type_name"] if random.random() < 0.1 else row["street_type_code"],
    axis=1
)

train_df["street_suffix_random"] = train_df.apply(
    lambda row: row["street_suffix_name"] if random.random() < 0.1 else row["street_suffix_code"],
    axis=1
)

train_df["state"] = train_df.apply(
    lambda row: row["state"] if random.random() < 0.1 else '',
    axis=1
)

train_df["postcode"] = train_df.apply(
    lambda row: row["postcode"] if random.random() < 0.9 else '',
    axis=1
)

train_df["country"] = train_df.apply(
    lambda row: row["country"] if random.random() < 0.9 else '',
    axis=1
)

address_fields = [
    'flat_type_random',
    'flat_number',
    'level_type_random',
    'level_number',
    'street_number',
    'street_name', 
    'street_type_random',
    'street_suffix_random',
    'locality_name', 
    'state', 
    'postcode',
    'country'
    ]


train_df['dirty_address'] = (
    train_df[address_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)


train_df['dirty_address'] = train_df['dirty_address'].apply(add_individual_company_name, name_prob=0.1)

train_df = train_df[[
    'street_key',
    'street_identifier',
    'full_address',
    'dirty_address'
    ]]

train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(train_df)

train_df.to_csv("train_data/train_data_2.csv", index=False)
