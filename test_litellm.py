import instructor
from litellm import completion
from pydantic import BaseModel
from rich import print

class User(BaseModel):
    name: str
    age: int


client = instructor.from_litellm(completion)

resp = client.chat.completions.create(
    model="anthropic/claude-3-7-sonnet-20250219",  # Added "anthropic/" prefix to the model name
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract Jason is 25 years old.",
        }
    ],
    response_model=User,
)

print(resp)

assert isinstance(resp, User)
assert resp.name == "Jason"
assert resp.age == 25