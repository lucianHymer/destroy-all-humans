import asyncio
import sys
import json
import click
from typing import List
from .utils.queue import Queue
from .utils.protocols.embeddings_pb2 import (
    GenerateEmbeddingsRequest,
    GenerateEmbeddingsResponse,
)

queue = Queue("generate_embedding")


async def convert_to_embedding(text: str) -> List[float]:
    request = GenerateEmbeddingsRequest()
    request.sentences.extend([text])
    origin_message = await queue.send(request.SerializeToString())
    response_message = await origin_message.receive_response()

    if response_message is None:
        raise Exception("No response received")

    response = GenerateEmbeddingsResponse()
    response.ParseFromString(response_message.serialized_data)

    single_embedding = response.embeddings[0]

    return [float(value) for value in single_embedding.values]


async def run():
    """
    Read text from STDIN, convert it to an embedding, and output to STDOUT.
    """
    # Read all input from STDIN
    input_text = sys.stdin.read()

    embedding = await convert_to_embedding(input_text)

    # Convert the embedding list to a JSON string and ensure we add a newline
    sys.stdout.write(json.dumps(embedding) + "\n")

    await Queue.cleanup()


@click.command(help="Generate embeddings from text input via STDIN")
def generate_embedding():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run())
        finally:
            if loop.is_running():
                loop.stop()
            if not loop.is_closed():
                loop.close()
                asyncio.set_event_loop(None)
    except Exception as e:
        sys.stderr.write(f"Error processing text: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    generate_embedding()
