#!/usr/bin/env python3

import sys
import click

def convert_to_embedding(text: str) -> str:
    return text.capitalize()

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

if __name__ == '__main__':
    generate_embedding()
