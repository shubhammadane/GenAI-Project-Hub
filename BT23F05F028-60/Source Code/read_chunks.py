import requests
import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

jsons = sorted(
    os.listdir("jsons"),
    key=lambda x: int(x.split("_")[0])
)

my_dicts = []
chunk_id = 0

for json_file in jsons:

    with open(
        os.path.join("jsons", json_file),
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    print(f"Creating embeddings for {json_file}")

    embeddings = create_embedding(
        [chunk["text"] for chunk in content]
    )

    for i, chunk in enumerate(content):

        chunk["chunk_id"] = chunk_id
        chunk["embedding"] = embeddings[i]

        my_dicts.append(chunk)

        chunk_id += 1

df = pd.DataFrame.from_records(my_dicts)

print(f"\nLoaded {len(df)} chunks")

# Save this dataframe
joblib.dump(df, "embeddings.joblib")
