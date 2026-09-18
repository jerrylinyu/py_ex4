## Import the necessary modules
import json
from ollama import chat
from pathlib import Path

## Import the function from the module parse_data
from parse_data import(
    load_items,
    get_unclaimed_items,
    save_result
)

## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

# The rules were drafted and some details were discussed. I asked AI to help me correct them.
def build_prompt(description, available_items):
    system_prompt = """You are an assistant that matches a user's lost item description against a lost-and-found database.
    
    RULES:
    1. Use ONLY the items provided in the given JSON. Never invent items or IDs.
    2. Not all the details of an item must match to be a possible match.
    3. Only JSON must be returned,
    with exactly the following strucutre: { "matches": ["ITEM_ID"], "confidence": "LOW" }
    4. "matches" contains all the possible matches
    5. "confidence" measures how confident the model is about the matches.
    It must be exactly one of: LOW, MEDIUM, HIGH.
    6. If there is no match the the model must return the an empty list
    """

    # ensure_ascii=False可以保证中文在转换时不会出错
    items_json = json.dumps(available_items, ensure_ascii=False, indent=2)

    # 用"""包裹住description防止用户在描述里输入指令，影响程序执行

    user_prompt = f"""A user lost an item. Their description:
    \"\"\"{description}\"\"\"
    Here is the lost-and-found database in JSON format:
    {items_json}
    
    Task: Find ALL possible matches.
    
    Return ONLY the JSON object:
    {{ "matches": ["ITEM_ID"], "confidence": "LOW" }}
    """
    return system_prompt, user_prompt
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = chat(
        model="qwen3:8b",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.message.content


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.

# 可能需要处理异常

def parse_response(response_text):
    suitable_data = json.loads(response_text)
    return suitable_data
    


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence",
# and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    valid_text = ["LOW", "MEDIUM", "HIGH"]
    id_list = []
    for item in available_items:
        id_list.append(item["id"])
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if result["confidence"] not in valid_text:
        return False
    for item in result["matches"]:
        if item not in id_list:
            return False
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("--------------------------------------------------")
    print(f"Confidence: {result["confidence"]}")
    print("\nPossible matches:\n")
    for id in result["matches"]:
        for item in available_items:
            if id == item["id"]:
                print(f"ID: {item['id']}")
                print(f"Item: {item['item']}")
                print(f"Color: {item['color']}")
                print(f"Location: {item['location']}")
                print(f"Date found: {item['date']}\n")
    

## Control center for the entire program.
def main():
    all_items = load_items("found_items.json")

    available_items = get_unclaimed_items(all_items)

    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("==================================================")
    description = input("\nDescribe the item you lost: ")

    print("\nSearching for possible matches...")

    system_prompt,user_prompt = build_prompt(description, available_items)
    result = parse_response(ask_qwen(system_prompt, user_prompt))

    if validate_result(result, available_items):
        if len(result["matches"]) != 0:
            display_matches(result, available_items)
        else:
            print("\nMATCH RESULT")
            print("--------------------------------------------------")
            print(f"Confidence: {result["confidence"]}")
            print("\nPossible matches:\n")
            print("No matching results\n")
    else:
        print("The out put error, please try again.")

    path = Path("output") / "match_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_result(result, path)

    print("Result saved to output/match_result.json")


if __name__ == "__main__":
    main()