# Take some unclean addresses and find nearest matches in the FAISS index of clean addresses

import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import gc


unclean_address = [
    '367 george st sydney 2000'
]
clean_address_file = "address_street.csv"
model_name = "model/street_matching_model"
faiss_index = "new_street_index.faiss"


def preprocess_address_text(text):
    cleaned_text = text.replace('/', ' ').replace(',', '').lower()
    return cleaned_text

print("Loading FAISS index...")
index = faiss.read_index(faiss_index)

res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
del index
gc.collect()


print("Loading clean address data...")
null_values = ['NULL', '']

clean_address_df = pd.read_csv(clean_address_file, dtype='string', na_filter=null_values)

id_to_address = clean_address_df.to_dict('records')


print("Loading unclean address data...")
unclean_address = list(map(preprocess_address_text, unclean_address))

print("Loading embedding model...")
model = SentenceTransformer(model_name, model_kwargs={"torch_dtype": "bfloat16"})
top_k = 20


print("Encoding unclean addresses...")
address_embeddings = model.encode(unclean_address, normalize_embeddings=True, show_progress_bar=True, batch_size=128)


print("Searching for matches...")
# D, I = index.search(address_embeddings, top_k)
D, I = gpu_index.search(address_embeddings, top_k)


print("Evaluating matches...")
correct_matches = 0
total_matches = len(unclean_address)

for i in range(total_matches):
    print(f"Unclean Address: {unclean_address[i]}")
    match_ids = I[i]
    distances = D[i]
    sorted_indices = sorted(range(top_k), key=lambda x: -distances[x])
    for idx in sorted_indices:
        match_id = match_ids[idx]
        if match_id != -1:
            matched_address = id_to_address[match_id]
            print(f"  Distance: {distances[idx]:.4f} | Street Key: {matched_address['street_key']} | Matched Street: {matched_address['full_street']}")
    print("-" * 60)
