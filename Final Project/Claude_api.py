# -*- coding: utf-8 -*-
"""Claude_API.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1wESYB6ZM_m1ffhbLLSAsJHWVo5WzHMBb
"""

pip install anthropic pandas tqdm

import anthropic
client = anthropic.Anthropic(api_key = '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')

import pandas as pd
pd.set_option('display.max_colwidth', None)
import json

# Read the CVS file
df = pd.read_csv('Input.csv')

row_string  = df.iloc[5].to_string(index=False)
appended_string = "\nWhat is wrong with this question. Answer in just one sentence. " + row_string
print(appended_string)

message = client.messages.create(
    model = "claude-3-5-sonnet-20240620",
    max_tokens = 1000,
    temperature = 0,
    #system = "Hello",
    messages = [
        {"role": "user",
        "content": [{"type":"text","text":appended_string}],
        }
    ],
)
# Extract the text from the TextBlock object
if isinstance(message.content, list) and len(message.content) > 0 and isinstance(message.content[0], anthropic.types.TextBlock):
  message_content_string = json.dumps({"text": message.content[0].text})
else:
    # If message.content is already a string or basic data type
  message_content_string = json.dumps(message.content)

message_content_string = message_content_string[10:message_content_string.find('.')]
print(message_content_string)

New_message = message_content_string + "Just answer with a yes or a no. Is this question correct?"
print(New_message)

message = client.messages.create(
    model = "claude-3-5-sonnet-20240620",
    max_tokens = 1000,
    temperature = 0,
    #system = "Hello",
    messages = [
        {"role": "user",
        "content": [{"type":"text","text":New_message}],
        }
    ],
)
# Extract the text from the TextBlock object
if isinstance(message.content, list) and len(message.content) > 0 and isinstance(message.content[0], anthropic.types.TextBlock):
  message_content_string = json.dumps({"text": message.content[0].text})
else:
# If message.content is already a string or basic data type
  message_content_string = json.dumps(message.content)

message_content_string = message_content_string[10:message_content_string.find('.')]
print(message_content_string)

# Read the CVS file
df = pd.read_csv('Input2.csv')

# Create an empty list to store responses
responses = []

for i in range(df.shape[0]):
  row_string  = df.iloc[i].to_string(index=False)
  appended_string = "\nWhat is wrong with this question. Answer in just one sentence. " + row_string
  print(appended_string)

  message = client.messages.create(
      model = "claude-3-5-sonnet-20240620",
      max_tokens = 1000,
      temperature = 0,
      #system = "Hello",
      messages = [
          {"role": "user",
          "content": [{"type":"text","text":appended_string}],
          }
      ],
  )

  # Extract the text from the TextBlock object
  if isinstance(message.content, list) and len(message.content) > 0 and isinstance(message.content[0], anthropic.types.TextBlock):
    message_content_string = json.dumps({"text": message.content[0].text})
  else:
      # If message.content is already a string or basic data type
    message_content_string = json.dumps(message.content)

  message_content_string = message_content_string[10:message_content_string.find('.')]
  print(message_content_string)

  # Append the cleaned string to the responses list
  responses.append(message_content_string)

# Save the responses to a new CSV file
response_df = pd.DataFrame({"Response": responses})
response_df.to_csv("Responses.csv", index=False)

print("Responses saved to 'Responses.csv'")

## Read the CSV file
df2 = pd.read_csv('Responses.csv')

for i in range(df2.shape[0]):
  row_string  = df2.iloc[i].to_string(index=False)
  print(row_string)

# Read the CSV file
df2 = pd.read_csv('Responses.csv')

valid = []

for i in range(df2.shape[0]):

  Res  = df2.iloc[i].to_string(index=False)

  New_message = Res + "Just answer with a yes or a no. Is this question correct?"

  message = client.messages.create(
      model = "claude-3-5-sonnet-20240620",
      max_tokens = 1000,
      temperature = 0,
      #system = "Hello",
      messages = [
          {"role": "user",
          "content": [{"type":"text","text":New_message}],
          }
      ],
  )
  # Extract the text from the TextBlock object
  if isinstance(message.content, list) and len(message.content) > 0 and isinstance(message.content[0], anthropic.types.TextBlock):
    message_content_string = json.dumps({"text": message.content[0].text})
  else:
  # If message.content is already a string or basic data type
    message_content_string = json.dumps(message.content)

  message_content_string = message_content_string[10:message_content_string.find('.')]
  print(message_content_string)

  # Append the cleaned string to the responses list
  valid.append(message_content_string)

# Save the validation to a new CSV file
valid_df = pd.DataFrame({"Response": valid})
valid_df.to_csv("Validatio.csv", index=False)

print("Responses saved to 'Validation.csv'")