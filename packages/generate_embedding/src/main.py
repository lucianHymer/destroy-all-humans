import asyncio
import sys
import json
import click
from pydantic import BaseModel
from typing import List
from .utils.queue import Queue

# from sentence_transformers import SentenceTransformer
#
# sentences = [
#     "That is a happy person",
#     "That is a happy dog",
#     "That is a very happy person",
#     "Today is a sunny day",
# ]
#
# start_time = time.time()
# model = SentenceTransformer(
#     "dunzhang/stella_en_400M_v5",
#     trust_remote_code=True,
#     device="cpu",
#     config_kwargs={"use_memory_efficient_attention": False, "unpad_inputs": False},
# )
# model_load_time = time.time() - start_time
# print(f"Model loading time: {model_load_time:.2f} seconds", file=sys.stderr)
#
# start_time = time.time()
# embeddings = model.encode(sentences)
# embedding_time = time.time() - start_time
# print(f"Embedding generation time: {embedding_time:.2f} seconds", file=sys.stderr)
#
# start_time = time.time()
# similarities = model.similarity(embeddings, embeddings)
# similarity_time = time.time() - start_time
# print(f"Similarity calculation time: {similarity_time:.2f} seconds", file=sys.stderr)


# TODO DRY
class GenerateEmbeddingsRequest(BaseModel):
    sentences: List[str]


class GenerateEmbeddingsResponse(BaseModel):
    embeddings: List[List[float]]


queue = Queue("generate_embedding")


async def convert_to_embedding(text: str) -> List[List[float]]:
    origin_message = await queue.send(
        GenerateEmbeddingsRequest(sentences=[text]).model_dump()
    )
    response_message = await origin_message.receive_response()

    if response_message is None:
        raise Exception("No response received")

    response = GenerateEmbeddingsResponse.model_validate(response_message.data)

    return response.embeddings


@click.command(help="Generate embeddings from text input via STDIN")
def generate_embedding():
    """
    Read text from STDIN, convert it to an embedding, and output to STDOUT.
    """
    # Read all input from STDIN
    input_text = sys.stdin.read()

    try:
        # Run the async function in an event loop
        embedding = asyncio.run(convert_to_embedding(input_text))

        # Convert the embedding list to a JSON string and ensure we add a newline
        sys.stdout.write(json.dumps(embedding) + "\n")
    except Exception as e:
        sys.stderr.write(f"Error processing text: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    generate_embedding()
