# Take CSV file with address fields and format it into a full address

import pandas as pd

header_type = {
    "address_detail_pid": "string",
    "legal_parcel_id": "string",
    "address_line_1": "string",
    "address_line_2": "string",
    "address_line_3": "string",
    "country": "string"
}

null_values = ['', 'NULL']

df = pd.read_csv("address_lines.csv", dtype=header_type, na_filter=null_values)


address_fields = [
    "address_line_1",
    "address_line_2",
    "address_line_3",
    "country",
]

df['full_address'] = (
    df[address_fields]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    .str.lower()
)

df = df[[df.columns[0], df.columns[-1]]]

df.to_csv("full_address.csv", index=False, header=True)