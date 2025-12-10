import openai
import json
from typing import List, Dict
import logging
from app import config

openai.api_key = config.OPENAI_API_KEY

def ask_question(messages: list) -> str:
    if not messages:
        return {}

    if not isinstance(messages[0], dict):
        messages = [{"role": "user", "content": messages[0]}]

    response = openai.ChatCompletion.create(
        model=config.OPENAI_LANG_MODEL,
        messages=messages
    )
    return response.choices[0].message.content


def extract_vocabularies(text: str, level: str = "B2-C1", count: int = 10) -> List[Dict[str, str]]:
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
        openai.api_key = config.OPENAI_API_KEY

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
            model=config.OPENAI_LANG_MODEL,
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
        )
        choices = response.get("choices")
        if not choices or not choices[0].get("message"):
            raise ValueError("OpenAI returned no choices or message.")

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
