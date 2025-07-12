import json

def reset_conversation_context():
    """Returns a fresh empty conversation context list."""
    return []

def save_context_to_file(context, file_path):
    """Saves the conversation context to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(context, f, ensure_ascii=False, indent=2)

def load_context_from_file(file_path):
    """Loads the conversation context from a JSON file, returns empty list if file not found."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def update_context(context, new_message):
    """Appends a new message dictionary to the context list."""
    context.append(new_message)

def extract_response_and_update_context(response, context):
    """
    Extracts the assistant's message content from OpenAI response and appends it to context.
    Returns the message content.
    """
    if response.choices:
        ai_message = response.choices[0].message['content'].strip()
        context.append({"role": "assistant", "content": ai_message})
        return ai_message
    return ""
