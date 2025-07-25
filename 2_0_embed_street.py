#  Take csv file with formatted street, generate embeddings and store in FAISS IP index

import faiss
from sentence_transformers import SentenceTransformer
import pandas as pd


clean_address_file = 'address_street.csv'
model_name = "model/street_matching_model"
faiss_index = "new_street_index.faiss"


# model = SentenceTransformer("all-MiniLM-L6-v2", model_kwargs={"torch_dtype": "bfloat16"})
model = SentenceTransformer(model_name, model_kwargs={"torch_dtype": "bfloat16"})

null_values = ['', 'NULL']

df = pd.read_csv(clean_address_file, dtype='string', na_filter=null_values, header=0)

street_list = df['full_street'].str.lower().tolist()


embeddings = model.encode(street_list, normalize_embeddings=True, show_progress_bar=True, batch_size=256)


dimension = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
faiss.write_index(index, faiss_index)
