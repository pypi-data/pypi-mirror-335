# ChatWeaver

**ChatWeaver** is a Python library that simplifies the implementation of chatbots powered by OpenAI models. Designed with developers in mind, it provides powerful features and an intuitive interface to enhance the development of conversational AI.

## Features

- **Chat History Management**: Easily track and manage conversation context.
- **Message Templates**: Automatically remember and include previous messages in prompts.
- **File Integration**: Add images and PDF files to your prompts seamlessly.
- **Custom Model Support**: Compatible with various OpenAI models.
- **Extensibility**: Flexible architecture for scalable chatbot solutions.

## Installation
Install ChatWeaver using pip:

```bash
pip install chatweaver
```

## Quick Start

Here’s how you can get started with ChatWeaver:

```python
import chatweaver as cw

chat: cw.Chat = cw.Chat(
    model="gpt-4o", 
    api_key="<Your API key here>", 
    rules=cw.chat_weaver_rules["basic"], 
    name="ChatWeaverBot", 
    replies_limit=10, 
    user="User"
    )

prompt: str = "Hi how are you?"
response = chat.get_response(prompt=prompt, user="User")
```

## Requirements
- Python 3.8 or above.
- OpenAI Python library (openai).
