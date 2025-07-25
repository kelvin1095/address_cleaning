# Using generated dirty data, train model

import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

train_data_file = 'train_data/train_data.csv'

header_type = {
    'street_key': 'string',
    'street_identifier': 'string',
    'full_address': 'string',
    'dirty_address': 'string',
    }
null_values = ['NULL', '']

train_df = pd.read_csv(train_data_file, dtype=header_type, na_filter=null_values)

train_pairs = list(zip(train_df['dirty_address'], train_df['street_identifier']))
train_examples = [
    InputExample(texts=[unclean, clean])
    for unclean, clean in train_pairs
]
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=64)

model = SentenceTransformer('all-MiniLM-L6-v2')

train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(train_objectives=[(train_dataloader, train_loss)],
          output_path='model/street_matching_model',
          epochs=3,
          show_progress_bar=True
)