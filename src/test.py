import re, json
def extract_relation(response):
    # Remove <think> tags and their content
    response_cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

    try:
        # Try parsing as JSON
        parsed_response = json.loads(response_cleaned)

        if isinstance(parsed_response, dict):
            # Handle dictionary formats: {'relation': label} and {relation: label}
            if "relation" in parsed_response:
                return parsed_response["relation"]
            elif parsed_response:
                return list(parsed_response.values())[0]  # Return the first value
        elif isinstance(parsed_response, str):
            if ":" in response_cleaned:
                return response_cleaned.split(":", 1)[1].strip()

    except ValueError:
        pass  # Not JSON, try alternative parsing

    # Handle "relation:label" format
    if ":" in response_cleaned:
        return response_cleaned.split(":", 1)[1].strip()

    return "None"
response = "relation: Attack"
res = extract_relation(response)

print(res)