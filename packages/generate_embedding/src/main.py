import sys
import click
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("dunzhang/stella_en_400M_v5", trust_remote_code=True)

sentences = [
    "That is a happy person",
    "That is a happy dog",
    "That is a very happy person",
    "Today is a sunny day",
]
embeddings = model.encode(sentences)

similarities = model.similarity(embeddings, embeddings)


def convert_to_embedding(text: str) -> str:
    print(similarities.shape)
    return str(similarities)


@click.command(help="Generate embeddings from text input via STDIN")
def generate_embedding():
    """
    Read text from STDIN, convert it to an embedding, and output to STDOUT.
    """
    # Read all input from STDIN
    input_text = sys.stdin.read()

    try:
        embedding = convert_to_embedding(input_text)

        sys.stdout.write(embedding)
    except Exception as e:
        sys.stderr.write(f"Error processing text: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    generate_embedding()
