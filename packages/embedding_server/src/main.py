import sys
import time
import asyncio
from sentence_transformers import SentenceTransformer
from typing import List
from pydantic import BaseModel
from .utils.queue import Queue, Message, QueueReceiveOptions

# Load the model once at startup
start_time = time.time()
model = SentenceTransformer(
    "dunzhang/stella_en_400M_v5",
    trust_remote_code=True,
    device="cpu",
    config_kwargs={"use_memory_efficient_attention": False, "unpad_inputs": False},
)
model_load_time = time.time() - start_time
print(f"Model loading time: {model_load_time:.2f} seconds", file=sys.stderr)


# TODO import JSON schema definitions or something else
#      portable and simple


class GenerateEmbeddingsRequest(BaseModel):
    sentences: List[str]


class GenerateEmbeddingsResponse(BaseModel):
    embeddings: List[List[float]]


def generate_embeddings_handler(
    message: Message,
) -> GenerateEmbeddingsResponse:
    try:
        request = GenerateEmbeddingsRequest.model_validate(message.data)
        sentences = request.sentences

        print(f"Generating embeddings for {len(sentences)} sentences", file=sys.stderr)

        embeddings = model.encode(sentences)

        return GenerateEmbeddingsResponse(embeddings=embeddings.tolist())
    except Exception as e:
        print(f"Error generating embedding: {str(e)}", file=sys.stderr)
        raise


# class CompareEmbeddingsRequest(BaseModel):
#    embeddings1: List[List[float]]
#    embeddings2: List[List[float]]
#
#
# class CompareEmbeddingsResponse(BaseModel):
#    similarities: List[List[float]]
#
#
# def compare_embeddings_handler(message: Message) -> Message:
#    try:
#        text1 = message.get("text1")
#        text2 = message.get("text2")
#        if not text1 or not text2:
#            raise ValueError("Both text1 and text2 must be provided")
#
#        embedding1 = model.encode([text1])[0]
#        embedding2 = model.encode([text2])[0]
#        similarity = model.similarity(
#            embedding1.reshape(1, -1), embedding2.reshape(1, -1)
#        )[0][0]
#        return float(similarity)
#    except Exception as e:
#        print(f"Error comparing embeddings: {str(e)}", file=sys.stderr)
#        raise


async def handle_generate_embeddings():
    async for message in Queue("generate_embedding").listen():
        response = generate_embeddings_handler(message)
        await message.respond(response.model_dump())


async def handle_compare_embeddings():
    pass


# async for message in Queue("compare_embeddings").listen():
#     response = compare_embeddings_handler(message)
#     await message.respond(response)


async def main():
    await asyncio.gather(handle_generate_embeddings(), handle_compare_embeddings())


if __name__ == "__main__":
    asyncio.run(main())
