from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    print('Checking norms of existing embeddings...')
    r = conn.execute(text('SELECT id, embedding_vector FROM images WHERE embedding_vector IS NOT NULL'))
    for row in r:
        # pgvector-sqlalchemy returns a numpy array if configured, 
        # but here it might be returning a string or list
        val = row.embedding_vector
        if isinstance(val, str):
            # Postgres vector format: '[1.2, 3.4, ...]'
            vec = np.array(eval(val.replace('{', '[').replace('}', ']')))
        else:
            vec = np.array(val)
        
        norm = np.linalg.norm(vec)
        print(f"Image ID {row.id}: Norm = {norm:.4f}")
