import sqlite3
from dotenv import load_dotenv
import os
import google.generativeai as genai


# Env stuff
load_dotenv(dotenv_path=".env.local")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Path to our DB
db_path = "chat_backup.db"

# Currently using Gemini 2.0. Will switch to OpenAI eventually
# NOTE: names in one-shot learning anonymized for privacy purposes
prompt = """
You are a helpful assistant that takes a list of texts sent by people around age 22 and provides a concise, multi-paragraph summarization of the texts.
Each message is formatted as sender_id: message. The sender_id is arbitrary, but will help you follow along the conversation.
It will clarify to you who sent the message, which may be helpful context.
Note that a sender_id of 0 indicates that it was sent by me. You can refer to those messages as "you".
Please do not expose the sender_id in the prompt. If you see a message saying, "100: hello", do NOT include the 100 in the response.
Give up to 3 paragraphs with 3-4 sentences per paragraph at most. If there are a huge amount of messages, feel free to provide a longer summary if necessary.

Structure
Input format: a list of text messages
Output format: one, two, or three paragraphs of summarization. Up to 200 word summary.

Example
Input:
[
	"1: hi squad",
	"1: i am currently starting to plan my flight back to the states",
	"1: and would love to make it in time to take grad pics together",
	"1: i know it is early but do either of u know when u might do it",
	"1: and/or would finals week be too late/inconvenient. thoughts",
	"2: I did not plan on doing grad pics",
	"2: finals week will probably be a little stressful",
	"2: I’m a lil nervous for my classes next sem LOLL",
	"0: bob u cant not plan on doing grad pics...",
	"1: yea...",
	"0: at least take them with us during dead week?",
	"0: alice maybe you come home a week early to take grad pics with bob?",
	"1: sounds good, i'll come back then",
]
Output:
Alice suggests taking grad pics with a group of her friends. Bob doesn't want to take them due to stress from classes during finals week. You and Alice agree it's unacceptable to not take grad pics. To solve this, Alice offers to come home early, so the three of you can take grad pics together.

Now do this on the following input.
"""
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp")


def decode_binary(attributed_body: bytes):
	# Creds: https://github.com/my-other-github-account/imessage_tools

	attributed_body = attributed_body.decode('utf-8', errors='replace')
	if "NSNumber" in str(attributed_body):
		attributed_body = str(attributed_body).split("NSNumber")[0]
		if "NSString" in attributed_body:
			attributed_body = str(attributed_body).split("NSString")[1]
			if "NSDictionary" in attributed_body:
				attributed_body = str(attributed_body).split("NSDictionary")[0]
				attributed_body = attributed_body[6:-12]

	return attributed_body


def fetch_messages_from_chat(chat_name, limit=100):
	# Connect to db
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# SQL Query
	query = """
	SELECT m.text, m.attributedBody, m.handle_id
	FROM message as m
	JOIN chat_message_join AS cmj ON m.ROWID = cmj.message_id
	JOIN chat as c ON cmj.chat_id = c.ROWID
	WHERE c.display_name = ?
	ORDER BY m.date DESC
	"""
	
	# Execute.
	# We arbitrarily include 5x the limit to make sure we have at least limit messages.
	cursor.execute(query, (chat_name,))
	results = cursor.fetchall()

	# Extract results
	messages = []
	for text, body, handle_id in results:
		if text is not None and (stripped_text := text.strip()):
			messages.append(f"{handle_id}: {stripped_text}")

		elif body:
			decoded_text = decode_binary(body)
			if decoded_text:
				messages.append(f"{handle_id}: {decoded_text}")

		if len(messages) >= limit:
			break

	conn.close()
	return list(reversed(messages))


if __name__ == "__main__":
	display_name = "temp = ’tis’; return temp + ‘ms’ if o, s else temp + ‘nots’"
	messages = fetch_messages_from_chat(chat_name=display_name)
	full_prompt = prompt + f"\nInput: {messages}\nOutput:"
	response = model.generate_content(full_prompt)

	# Print the model-generated response
	print(response.text)
