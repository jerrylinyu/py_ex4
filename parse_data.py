## Import the necessary modules
import json

## Logic for loading and reading from a JSON file. 
## The function must return only the items
def load_items(filename):
    try:
        with open(filename, 'r') as fail:
            text = json.load(fail)
    except FileNotFoundError:
        print("This file doesn't exist")
    except OSError:
        print("An error occurred when trying to read the file")
    return text["items"]


## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    unclaimed_items = []
    for item in items:
        if item["status"] == "unclaimed":
            # 返回的是item ID(dice)
            unclaimed_items.append(item)
    return unclaimed_items

## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    with open(filename, 'w') as saveFile:
        json.dump(result, saveFile, indent=4)


if __name__ == "__main__":
    item = load_items("found_items.json")
    print(type(item), item)

    unclaimed_items = get_unclaimed_items(item)
    print(type(unclaimed_items), unclaimed_items)

    save_result(unclaimed_items, "unclaimed_items.json")
