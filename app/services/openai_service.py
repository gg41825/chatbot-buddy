import openai
import json
import logging
from app.config import config, get_config_value


def ask_question(messages: list[str]):
    if not messages:
        return ""

    # default role to user
    messages = {"role": "user", "content": messages} if "role" not in messages[0] else messages

    openai.api_key = get_config_value("openai", "api.key")
    response = openai.ChatCompletion.create(
        model=get_config_value("openai", "lang.model", "gpt-3.5-turbo"),
        messages=messages
    )
    return response


def extract_vocabularies(text: str, level: str = "B2-C1", count: int = 5):
    """
    Extract German vocabularies from article text using OpenAI.

    Args:
        article_text: The German article text
        level: Vocabulary level (default: B2-C1)
        count: Number of vocabularies to extract (default: 10)

    Returns:
        List of dictionaries with keys: german, english, chinese, sentence
    """
    try:
        openai.api_key = get_config_value("openai", "api.key")

        prompt = f"""You are a German language instructor. Analyze the following German article and extract exactly {count} vocabulary items at the {level} level.

For each vocabulary item, provide the following fields:
1.The German word (preserve original casing)
2.The English translation
3.The Traditional Chinese translation
4.A practical daily-life example sentence in German that naturally uses this word (the example must not be taken from the article)

Return the result as a JSON array with the following exact structure and field names:
[
  {{
    "german": "German word",
    "english": "English translation",
    "chinese": "繁體中文翻譯",
    "sentence": "Example sentence from the text"
  }}
]

Text:
{text}

Important: Output only the JSON array without any additional text or explanation, and avoid using emojis and —"""

        response = openai.ChatCompletion.create(
            model=get_config_value("openai", "lang.model", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful German language teacher. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        content = response['choices'][0]['message']['content'].strip()

        # Try to parse JSON response
        try:
            vocabularies = json.loads(content)
            return vocabularies
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                vocabularies = json.loads(json_str)
                return vocabularies
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                vocabularies = json.loads(json_str)
                return vocabularies
            else:
                logging.error(f"Failed to parse OpenAI response as JSON: {content}")
                return []

    except Exception as e:
        logging.error(f"Error extracting vocabularies: {str(e)}")
        return []


def format_vocabularies_for_line(vocabularies: list) -> str:
    """
    Format vocabularies list into a readable message for LINE.

    Args:
        vocabularies: List of vocabulary dictionaries

    Returns:
        Formatted string for LINE message
    """
    if not vocabularies:
        return "Sorry, I couldn't extract vocabularies from the text."

    message = f"Found {len(vocabularies)} German vocabularies:\n\n"

    for i, vocab in enumerate(vocabularies, 1):
        message += f"{i}. {vocab['german']}\n"
        message += f"{vocab['english']}\n"
        message += f"{vocab['chinese']}\n"
        if vocab.get('sentence'):
            # Truncate long sentences
            sentence = vocab['sentence']
            if len(sentence) > 100:
                sentence = sentence[:97] + "..."
            message += f"{sentence}\n"
        message += "\n"

    return message.strip()
