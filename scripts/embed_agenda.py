import os
import click
import faiss
import numpy as np
import openai

@click.command()
@click.option('--agenda', default='knowledge/research_agenda.md')
@click.option('--output', default='embeddings/faiss.index')
def main(agenda: str, output: str) -> None:
    """Build FAISS embeddings for the research agenda."""
    with open(agenda, 'r', encoding='utf-8') as f:
        text = f.read()

    chunks = [c.strip() for c in text.split('\n\n') if c.strip()]
    resp = openai.Embedding.create(input=chunks, model='text-embedding-3-small')
    vectors = np.array([r['embedding'] for r in resp['data']]).astype('float32')
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    faiss.write_index(index, output)

if __name__ == '__main__':
    main()
