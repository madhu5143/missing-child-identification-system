import os
import sys
from sqlalchemy import text
sys.path.append(os.getcwd())
from app.database import engine

def migrate_vector_dim():
    with engine.connect() as conn:
        try:
            print("Dropping old index...")
            conn.execute(text("DROP INDEX IF EXISTS images_embedding_vector_idx"))
            
            print("Altering column type to vector(512)...")
            # We must cast the existing data to the new dimension, though in our case 
            # fix_database_embeddings already tried to write 512d arrays, maybe it just truncated or failed silently
            conn.execute(text("ALTER TABLE images ALTER COLUMN embedding_vector TYPE vector(512)"))
            
            print("Recreating HNSW index for cosine similarity...")
            # We use vector_ip_ops because our vectors are strictly L2 normalized in the pipeline,
            # so inner product <#> mathematically equals cosine similarity, but is much faster.
            conn.execute(text("CREATE INDEX images_embedding_vector_idx ON images USING hnsw (embedding_vector vector_ip_ops)"))
            
            conn.commit()
            print("Migration successful: pgvector is now configured for 512 dimensions.")
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate_vector_dim()
