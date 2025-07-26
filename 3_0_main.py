# Batch clean stuff?

import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd
import gc
import time
from utils import preprocess_address_text, build_indexes, best_address_match


dirty_address = "dirty_data/dirty_data_1.csv"
address_street_file = "address_street.csv"
address_number_file = "address_number.csv"
model_name = "model/street_matching_model"
faiss_index = "new_street_index.faiss"

top_k = 20


print("Loading address street data...")
street_df = pd.read_csv(address_street_file, dtype='string')
id_to_address = street_df.to_dict('records')


print("Loading address number data...")
number_df = pd.read_csv(address_number_file, dtype='string')


print("Building indexes...")
keys, streets, street_by_key, numbers_by_key = build_indexes(street_df, number_df)


print("Loading unclean address data...")
unclean_address_df = pd.read_csv(dirty_address, dtype='string')
unclean_address = unclean_address_df['dirty_address'].tolist()
unclean_address = list(map(preprocess_address_text, unclean_address))


print("Loading FAISS index...")
index = faiss.read_index(faiss_index)

res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
del index
gc.collect()


print("Loading embedding model...")
model = SentenceTransformer(model_name, model_kwargs={"torch_dtype": "bfloat16"})


print("Encoding unclean addresses...")
address_embeddings = model.encode(unclean_address, normalize_embeddings=True, show_progress_bar=True, batch_size=128)


print("Searching for matches...")
# D, I = index.search(address_embeddings, top_k)
D, I = gpu_index.search(address_embeddings, top_k)


print("Searching for matches...")
total_matches = len(unclean_address)

start = time.time()
for i in range(total_matches):
    print(f"Unclean address: {unclean_address[i]}")
    clean_address = best_address_match(unclean_address[i], I[i], keys, street_by_key, numbers_by_key)
    print(f"Clean address: {clean_address}")
end = time.time()
print(f"Elapsed time: {end - start:.4f} seconds")