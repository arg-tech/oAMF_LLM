import re
import json
import logging


def extract_relation(response):
    # Remove <think> tags and their content
    response_cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    logging.info(f"response_cleaned: {response_cleaned}")

    relation = "None"  # Default value

    try:
        # Extract JSON substring from response if present
        json_match = re.search(r'\{.*?\}', response_cleaned, re.DOTALL)
        if json_match:
            parsed_response = json.loads(json_match.group())

            if isinstance(parsed_response, dict):
                # Handle dictionary formats: {'relation': label} and {relation: label}
                if "relation" in parsed_response:
                    relation = parsed_response["relation"]
                elif parsed_response:
                    relation = list(parsed_response.values())[0]  # Return the first value
        else:
            # If no JSON, check for "relation:label" format
            match = re.search(r'relation\s*:\s*(\w+)', response_cleaned, re.IGNORECASE)
            if match:
                relation = match.group(1).strip()

    except (ValueError, json.JSONDecodeError):
        pass  # If JSON parsing fails, continue alternative extraction
            # Handle "relation:label" format
    if '"relation":' in response_cleaned:
        relation = response_cleaned.split(":", 1)[1].strip()

    return relation


response = """```json
{
  "relation": "None"
}
```"""

print(extract_relation(response))