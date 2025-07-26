# Embed unclean addresses and find nearest matches in the FAISS index of clean addresses

import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import gc


clean_address_file = "address_street.csv"
model_name = "model/street_matching_model"
faiss_index = "new_street_index.faiss"
dirty_address = "dirty_data/sample_set_3.csv"


print("Loading FAISS index...")
index = faiss.read_index(faiss_index)

res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
del index
gc.collect()

print("Loading clean address data...")
header_type = {
    'street_key': 'string',
    'street_identifier': 'string',
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

clean_address_df = pd.read_csv(clean_address_file, dtype=header_type, na_filter=null_values)

id_to_address = clean_address_df.to_dict('records')


print("Loading unclean address data...")
header_type = {
    'address_detail_pid': 'string',
    'full_address': 'string'
}
null_values = ['NULL', '']

unclean_address_df = pd.read_csv(dirty_address, dtype=header_type, na_filter=null_values)
unclean_address = unclean_address_df['full_address'].tolist()


print("Loading embedding model...")
# model = SentenceTransformer("all-MiniLM-L6-v2", model_kwargs={"torch_dtype": "bfloat16"})
model = SentenceTransformer(model_name, model_kwargs={"torch_dtype": "bfloat16"})
top_k = 20


print("Encoding unclean addresses...")
address_embeddings = model.encode(unclean_address, normalize_embeddings=True, show_progress_bar=True, batch_size=128)


print("Searching for matches...")
# D, I = index.search(address_embeddings, top_k)
D, I = gpu_index.search(address_embeddings, top_k)


print("Evaluating matches...")
total_matches = len(unclean_address)

match_at_1 = 0
match_at_3 = 0
match_at_5 = 0
match_at_10 = 0
match_at_20 = 0

for i in range(total_matches):
    true_id = unclean_address_df.iloc[i]['street_key']
    match_ids = I[i]
    found_rank = None

    for j in range(min(len(match_ids), 20)):
        match_id = match_ids[j]
        if match_id != -1:
            predicted_id = id_to_address[match_id]['street_key']
            if str(true_id) == str(predicted_id):
                found_rank = j + 1
                break

    if found_rank:
        if found_rank <= 20:
            match_at_20 += 1
        if found_rank <= 10:
            match_at_10 += 1
        if found_rank <= 5:
            match_at_5 += 1
        if found_rank <= 3:
            match_at_3 += 1
        if found_rank == 1:
            match_at_1 += 1
    else:
        print(unclean_address[i])

print(f"Match in Top 1:  {match_at_1}")
print(f"Match in Top 3:  {match_at_3}")
print(f"Match in Top 5:  {match_at_5}")
print(f"Match in Top 10: {match_at_10}")
print(f"Correct matches: {match_at_20} / {total_matches} ({match_at_20/total_matches:.2%})")
