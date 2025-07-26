# Import raw data from sql and transform it

import pandas as pd
import hashlib


def md5_key(text):
    return hashlib.md5(text.encode()).hexdigest()


address_file = 'address_fields.csv'
full_df = pd.read_csv(address_file, dtype='string', header=0)



street_fields = [
    'street_name',
    'street_type_name',
    'street_suffix_name',
    'locality_name',
    'state_code',
    'postcode',
    'country'
    ]

full_df['full_street'] = (
    full_df[street_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)



full_df['street_key'] = (
    full_df['full_street']
    .apply(md5_key)
    )



number_fields = [
    'flat_type_name',
    'flat_number',
    'level_type_name',
    'level_number',
    'street_number'
    ]

full_df['full_number'] = (
    full_df[number_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)


street_df_columns = [
    'street_key',
    'full_street'
]

address_street_df = full_df[street_df_columns]
address_street_df = address_street_df.drop_duplicates()


number_df_columns = [
    'address_detail_pid',
    'full_number',
    'street_key'
]

address_number_df = full_df[number_df_columns]
address_number_df = address_number_df.drop_duplicates()


address_street_df.to_csv("address_street.csv", index=False)
address_number_df.to_csv("address_number.csv", index=False)

full_data = [
    'address_detail_pid',
    'street_key',
    'flat_type_code',
    'flat_type_name',
    'flat_number',
    'level_type_code',
    'level_type_name',
    'level_number',
    'street_number',
    'street_name',
    'street_type_code',
    'street_type_name',
    'street_suffix_code',
    'street_suffix_name',
    'locality_name',
    'state_code',
    'state_name',
    'postcode',
    'country'
]

add_info_df = full_df[full_data]
add_info_df.to_csv("full_dataset.csv", index=False)