import json
import urllib.parse

def encode_blocks_to_url(blocks):
  """
  Encodes a list of structured blocks into a URL-encoded JSON string.

  Args:
    blocks: A list of dictionaries representing the structured blocks.

  Returns:
    A URL-encoded string representing the JSON array of blocks.
  """
  json_string = json.dumps(blocks)

  return json_string

# Example usage:
blocks = [
    {"type": "section", "text": {"type": "plain_text", "text": "Hello, world!"}},
    {"type": "divider"},
    {"type": "context", "elements": [{"type": "mrkdwn", "text": "Some context"}]}
]

url_encoded_blocks = encode_blocks_to_url(blocks)
print(url_encoded_blocks)
print(type(url_encoded_blocks))

    
data = {"name": "John Doe", "age": 30, "city": "New York"}

json_string = json.dumps(data, indent=4)
print(json_string)
print(type(json_string))

json_string = json.dumps(data, indent=4)
print(json_string)
print(type(json_string))