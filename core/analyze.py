import sqlite3
from dotenv import load_dotenv
import os
from openai import OpenAI
import argparse
import json
from fetch_contacts import run_fetch_contacts


# Constants
load_dotenv(dotenv_path=".env.local")
openai_api_key = os.getenv("OPENAI_API_KEY")
db_path = "/Users/{}/Library/Messages/chat.db"
prompt = """
You are a helpful assistant that takes a list of texts sent by people around age 22 and provides a concise, multi-paragraph summarization of the texts.
Each message is formatted as sender_id: message. The sender_id is arbitrary, but will help you follow along the conversation.
It will clarify to you who sent the message, which may be helpful context.
When the sender ID is `Me`, that refers to messages sent by me. You may refer to me as "you" in your summary.
For everyone else, refer to their interactions and contributions by their names. See below for details.

Structure
Input format: a list of text messages
Output format: A number of paragraphs of paragraph-style output.

Example
Input:
[
	"Alice Avery: hi squad",
	"Alice Avery: i am currently starting to plan my flight back to the states",
	"Alice Avery: and would love to make it in time to take grad pics together",
	"Alice Avery: i know it is early but do either of u know when u might do it",
	"Alice Avery: and/or would finals week be too late/inconvenient. thoughts",
	"Bob Brown: I did not plan on doing grad pics",
	"Bob Brown: finals week will probably be a little stressful",
	"Bob Brown: I’m a lil nervous for my classes next sem LOLL",
	"Me: bob u cant not plan on doing grad pics...",
	"Alice Avery: yea...",
	"Me: at least take them with us during dead week?",
	"Me: alice maybe you come home a week early to take grad pics with bob?",
	"Alice Avery: sounds good, i'll come back then",
]
Output:
Alice suggests taking grad pics with a group of her friends. Bob doesn't want to take them due to stress from classes during finals week. You and Alice agree it's unacceptable to not take grad pics. To solve this, Alice offers to come home early, so the three of you can take grad pics together.

Now do this on the following input.
Please output {} paragraphs, with 3-4 sentences per paragraph.
"""
if openai_api_key is not None:
	client = OpenAI(api_key=openai_api_key)

else:
	client = OpenAI() # No API key needed!


def decode_binary(attributed_body: bytes):
	"""Decodes a bytes object of a message to extract the message plaintext"""
	# Credits: https://github.com/my-other-github-account/imessage_tools
	attributed_body = attributed_body.decode('utf-8', errors='replace')
	if "NSNumber" in str(attributed_body):
		attributed_body = str(attributed_body).split("NSNumber")[0]
		if "NSString" in attributed_body:
			attributed_body = str(attributed_body).split("NSString")[1]
			if "NSDictionary" in attributed_body:
				attributed_body = str(attributed_body).split("NSDictionary")[0]
				attributed_body = attributed_body[6:-12]

	return attributed_body


def fetch_messages_from_chat(chat_name, limit, mac_username, contacts):
	# Connect to db containing my most recent
	conn = sqlite3.connect(db_path.format(mac_username))
	cursor = conn.cursor()

	# SQL Query
	query = """
    SELECT
        m.text,
        m.attributedBody,
		COALESCE(h.id, 'Me') AS handle_value
    FROM message AS m
    JOIN chat_message_join AS cmj
        ON m.ROWID = cmj.message_id
    JOIN chat AS c
        ON cmj.chat_id = c.ROWID
	LEFT JOIN handle AS h
        ON (
			m.handle_id > 0
			AND m.handle_id = h.ROWID
		)
    WHERE c.display_name = ?
    ORDER BY m.date DESC
    """
	
	# Execute.
	cursor.execute(query, (chat_name,))
	results = cursor.fetchall()

	# Extract results
	messages = []
	for text, body, handle_value in results:
		output_text = ""
		if text is not None and (stripped_text := text.strip()):
			output_text = stripped_text

		elif body:
			decoded_text = decode_binary(body)
			if decoded_text:
				output_text = decoded_text

		if output_text:
			if handle_value.startswith("+1"):
				handle_value = handle_value[2:]

			contact_name = contacts.get(handle_value, handle_value)
			messages.append(f"{contact_name}: {output_text}")

		if len(messages) >= limit:
			break

	conn.close()
	return list(reversed(messages))


if __name__ == "__main__":
	# CLI Args
	parser = argparse.ArgumentParser(description="placeholder")
	parser.add_argument(
		"--no-prompt", "-np",
		action="store_true",
		help="No LLM prompting; just prints the messages (for debugging purposes)",
	)
	parser.add_argument(
		"--chat", "-c",
		type=str,
		required=True,
		help="Specify the name of the chat in iMessage",
	)
	parser.add_argument(
		"--messages", "-m",
		type=int,
		default=50,
		help="Number of the most recent messages in a chat to summarize",
	)
	parser.add_argument(
		"--paragraphs", "-p",
		type=int,
		default=2,
		help="Number of output paragraphs. Each paragraph will have 3-4 sentences.",
	)
	parser.add_argument(
		"--username", "-u",
		type=str,
		required=True,
		help="Specify your macOS computer's username. You can find this by running `pwd` from any directory.",
	)
	
	args = parser.parse_args()

	# Retrieving contacts
	if not os.path.exists("all-contacts.json"):
		print("Contacts not loaded. First run will be slow (be patient!)")
		run_fetch_contacts()

	with open("all-contacts.json", "r") as f:
		data = json.load(f)
		contacts = data.get("data", {})
	
	# Message processing
	messages = fetch_messages_from_chat(
		chat_name=args.chat,
		limit=args.messages,
		mac_username=args.username,
		contacts=contacts,
	)

	# Prompting
	if args.no_prompt:
		print(f"No-prompt enabled. Printing message history:\n{messages}")

	else:
		completion = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[
				{"role": "system", "content": prompt.format(args.paragraphs)},
				{"role": "user", "content": str(messages)},
			],
		)
		print(completion.choices[0].message.content)
