from typing import List
import openai
import os

from tenacity import retry, wait_random_exponential, stop_after_attempt


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Embed texts using OpenAI's ada model.

    Args:
        texts: The list of texts to embed.

    Returns:
        A list of embeddings, each of which is a list of floats.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # Call the OpenAI API to get the embeddings
    deployment = None

    try:
        if deployment is None:
            print("Creating embeddings using OpenAI")
            response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
        else:
            print("Creating embeddings using Azure")
            response = openai.Embedding.create(input=texts, deployment_id=deployment)

        print("Response received:", response)
        
        # Extract the embedding data from the response
        data = response["data"]  # type: ignore

        # Return the embeddings as a list of lists of floats
        return [result["embedding"] for result in data]
    except openai.error.OpenAIError as e:
        # Log more detailed error information
        print(f"An error occurred: {e}")
        raise
    except Exception as e:
        # Catch any other exceptions that might occur
        print(f"An unexpected error occurred: {e}")
        raise


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_chat_completion(
    messages,
    model="gpt-3.5-turbo",  # use "gpt-4" for better results
    deployment_id = None
):
    """
    Generate a chat completion using OpenAI's chat completion API.

    Args:
        messages: The list of messages in the chat history.
        model: The name of the model to use for the completion. Default is gpt-3.5-turbo, which is a fast, cheap and versatile model. Use gpt-4 for higher quality but slower results.

    Returns:
        A string containing the chat completion.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    # call the OpenAI chat completion API with the given messages
    # Note: Azure Open AI requires deployment id
    response = {}
    if deployment_id == None:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
    else:
        response = openai.ChatCompletion.create(
            deployment_id = deployment_id,
            messages=messages,
        )
    

    choices = response["choices"]  # type: ignore
    completion = choices[0].message.content.strip()
    print(f"Completion: {completion}")
    return completion
