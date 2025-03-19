import sys
from openai import AzureOpenAI

if len(sys.argv) < 2:
    print("Usage: python chat_completion.py <prompt>")
    sys.exit(1)

prompt = sys.argv[1]

api_version = "2024-08-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint="https://aws.openai.azure.com/",
    api_key="9apB9EtnpbOJYqPS0vzEbr8T976woI5FYLtnN2HdnTRkQymT5lZNJQQJ99AKACYeBjFXJ3w3AAABACOGFyYH"
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": prompt,
        },
    ],
)
print(completion.to_json())
