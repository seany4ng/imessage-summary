import re
import json
import subprocess

def normalize_phone(raw: str) -> str:
    """
    Removes non-digit characters, strips leading +1 or 1, returns last 10 digits if possible.
    If it looks like an email (contains '@'), return it as-is.
    """
    raw = raw.strip()
    if "@" in raw:
        # It's an email, leave it alone
        return raw

    # Remove everything but digits
    digits = re.sub(r"\D", "", raw)

    # If it starts with '1' and has 11 digits, drop the leading '1'
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    # If we have 10 digits left, return them
    if len(digits) == 10:
        return digits
    else:
        # If it's not exactly 10 digits by now, just return them all
        # (You might choose to ignore them or handle differently)
        return digits

def parse_applescript_output(raw_output: str):
    """
    Given AppleScript output like:
      'Audrey Zhang, item 1 of +16508231082, Charlie Guo, item 1 of (408) 390-2616, ...'
    produce a list of (name, phoneString).
    
    We assume the pattern:
      - Name tokens do NOT contain 'item X of' or digits (usually).
      - 'item X of +16508231082' is a phone reference.
      - Possibly a phone can appear without 'item X of' if AppleScript outputs something else.
    """
    tokens = [t.strip() for t in raw_output.split(",")]
    pairs = []
    current_name = None

    for token in tokens:
        token = token.strip()
        # If it's an 'item X of +number' pattern
        if token.startswith("item "):
            # e.g. "item 1 of +16508231082"
            phone_part = re.sub(r"^item\s+\d+\s+of\s+", "", token).strip()
            if current_name:
                pairs.append((current_name, phone_part))

        # If it contains enough digits to be a phone, or has an '@' for email, treat it as phone/email
        elif re.search(r"\d", token) or "@" in token:
            # Could be a raw phone like "+16692569550" or something with parentheses
            if current_name:
                pairs.append((current_name, token))

        else:
            # Otherwise assume it's a name
            current_name = token

    return pairs


def run_fetch_contacts():
    # 1) Run AppleScript to fetch all contacts
    script = r'''
    tell application "Contacts"
        set namePhonePairs to {}
        set allPersons to every person
        repeat with p in allPersons
            set personName to name of p
            set phoneNumbers to value of phones of p

            repeat with phoneNumber in phoneNumbers
                copy {personName, phoneNumber} to the end of namePhonePairs
            end repeat
        end repeat

        return namePhonePairs
    end tell
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    raw_output = result.stdout.strip()
    if result.stderr:
        print("AppleScript stderr:", result.stderr.strip())
    if result.returncode != 0:
        print("Error running osascript. Return code:", result.returncode)
        exit(1)

    print("Raw AppleScript output:\n", raw_output)

    # 2) Parse into (name, phoneString) pairs.
    #    Because the AppleScript "list of lists" is coming back in a weird textual format,
    #    we parse that via a custom approach:
    pairs = parse_applescript_output(raw_output)

    # 3) Build a dict of phone->name (or email->name)
    #    ignoring duplicates (last one wins, for simplicity)
    data_map = {}
    for name, phone_str in pairs:
        norm = normalize_phone(phone_str)
        if norm:
            data_map[norm] = name

    # 4) Write the JSON file:
    #    {
    #      "data": {
    #         "5552223333": "John Doe",
    #         ...
    #      }
    #    }
    out_json = {
        "data": data_map
    }
    with open("all-contacts.json", "w") as f:
        json.dump(out_json, f, indent=4)
    print("Wrote all-contacts.json")


if __name__ == "__main__":
    run_fetch_contacts()
