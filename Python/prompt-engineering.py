import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI

printFullResponse = False

# Example knowledge base for information retrieval
knowledge_base = {
    "python": "Python is a programming language known for its readability and simplicity.",
    "azure": "Azure is a cloud computing service created by Microsoft for building, testing, deploying, and managing applications and services.",
    "openai": "OpenAI is an AI research and deployment company known for developing advanced AI models."
}

def retrieve_information(query):
    """Simple information retrieval based on keywords."""
    return knowledge_base.get(query.lower(), None)

async def main():
    try:
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

        client = AsyncAzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2024-02-15-preview"
        )

        # Initialize conversation history
        conversation_history = []

        while True:
            print("------------------\nPausing the app to allow you to change the system prompt.\nPress enter to continue...")
            input()
            system_text = open(file="system.txt", encoding="utf8").read().strip()

            user_text = input("Enter user message, or 'quit' to exit: ")
            if user_text.lower() == 'quit':
                print('Exiting program...')
                break

            # Retrieve information if needed
            retrieved_info = retrieve_information(user_text)
            if retrieved_info:
                print("Retrieved Information:\n" + retrieved_info + "\n")
                conversation_history.append({"role": "user", "content": user_text})
                conversation_history.append({"role": "assistant", "content": retrieved_info})
            else:
                # Add user message to conversation history
                conversation_history.append({"role": "user", "content": user_text})

                # Call the OpenAI model with conversation history
                await call_openai_model(system_message=system_text,
                                         conversation_history=conversation_history,
                                         model=azure_oai_deployment,
                                         client=client)

    except Exception as ex:
        print(ex)

async def call_openai_model(system_message, conversation_history, model, client):
    messages = [{"role": "system", "content": system_message}] + conversation_history

    print("\nSending request to Azure OpenAI model...\n")
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )

    if printFullResponse:
        print(response)
    assistant_response = response.choices[0].message.content
    print("Response:\n" + assistant_response + "\n")

    # Add assistant's response to conversation history
    conversation_history.append({"role": "assistant", "content": assistant_response})

if __name__ == '__main__':
    asyncio.run(main())
