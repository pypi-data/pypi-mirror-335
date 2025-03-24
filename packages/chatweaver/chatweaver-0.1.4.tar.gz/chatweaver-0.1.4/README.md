# ChatWeaver

**ChatWeaver** is a Python library that simplifies the implementation of chatbots powered by OpenAI models. Designed with developers in mind, it provides powerful features and an intuitive interface to enhance the development of conversational AI.

---

## Features

- **Chat History Management**: Easily track and manage conversation context.
- **Message Templates**: Automatically remember and include previous messages in prompts.
- **File Integration**: Add images and PDF files to your prompts seamlessly.
- **Custom Model Support**: Compatible with various OpenAI models.
- **Extensibility**: Flexible architecture for scalable chatbot solutions.

---

## Installation
Install ChatWeaver using pip:

```bash
pip install chatweaver
```

---

## Quick Start

Here’s how you can get started with ChatWeaver:

```python
import chatweaver as cw

model = cw.Model(
    model="gpt-4o", 
    api_key="<Your OpenAI API key here>"
    )

bot = cw.Bot(
    rules=cw.chat_weaver_rules["basic"], 
    name="AiBot", 
    cw_model=model
    )

chat = cw.Chat(
    replies_limit=10, 
    user="Diego", 
    cw_bot=bot
    )

prompt = "Hi how are you?"
print(chat.get_response(prompt=prompt))
```

### Include images and files

You may also include images and files in the prompt by specifying their file paths.
```python
prompt = "Describe the content of the attached image."
image = "path\\to\\image.png"
print(chat.get_response(prompt=prompt, image_path=image))
```

### Implementation of Model Rules

ChatWeaver allows the customization of chatbot behavior through a set of predefined rules, defined in the variable `chat_weaver_rules`. These rules determine the role, style, format, and ethical guidelines the bot must follow. Each rule is designed to suit specific scenarios, enhancing interactivity and consistency in the conversation.

### Available Rules

1. **basic**: Sets the bot with scientifically accurate and reliable goals. Includes:
   - No text formatting.
   - Friendly and respectful communication.
   - Complete and contextual responses.
   - Strict ethical standards.
2. **default**: Optimizes the bot to keep the conversation flowing in a JSON format. Main features:
   - Single-line responses using `\n`.
   - JSON structure with keys like `reasoning`, `reply`, `result`.
3. **informal_chat**: Adjusts the bot for informal conversations. Key features:
   - Friendly and conversational language.
   - Simple JSON response format.
4. **formal_chat**: Adapts the bot for formal conversations. Includes:
   - Polite and respectful communication.
   - Formal JSON structure.
5. **formal_email**: Optimizes the bot for formal email exchanges. Features:
   - Adherence to email structure with greetings, body, and closing.
   - Detailed JSON responses.

### Implementation Example

To use a specific rule in your bot:

```python
import chatweaver as cw

# Configure the model
model = cw.Model(
    model="gpt-4o",
    api_key="<Your OpenAI API key here>"
)

# Configure the bot with a specific rule
bot = cw.Bot(
    rules=cw.chat_weaver_rules["basic"],
    name="AiBot",
    cw_model=model
)

# Create the chat
chat = cw.Chat(
    replies_limit=10,
    user="Diego",
    cw_bot=bot
)

# User prompt
prompt = "Hello, how are you?"
response = chat.get_response(prompt=prompt)
print(response)
```

---

## Requirements
- Python 3.8 or above.
- OpenAI Python library (openai).

---

### Whats new in 0.1.4?
- Implemented a new method for creating chats while ensuring backward compatibility with the existing system.
- Enhanced the Bot's capabilities by enabling it to remember the user's name along with its own.
