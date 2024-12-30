# imessage-summary
Have you ever opened iMessage to 200+ messages from your friends in an important group chat, not sure how to catch up on it all? Rather than reading all those messages one-by-one, you can now generate concise summaries of recent texts in a group chat, saving you time that you would have spent scrolling and reading.

## Quickstart guide
Currently this runs as a Python script that reads your iMessage chat history for only the specific chat(s) you allow. No data is stored on our end, as the query runs locally and the OpenAI API call uses a token you provide.

1. Give your terminal (Terminal, iTerm2, Warp, etc.) full disk access. You can find this in Settings > Privacy & Security > Full Disk Access.
2. Bring your own API Key (BYOAK). Create an OpenAI organization [here](https://platform.openai.com/docs/overview) and generate a new API key. Mild usage of 4o-mini is free, and the entire process only takes a few minutes.
3. Run `pip install -r requirements.txt`. It is recommended to do this in a virtualenv.
4. Run `python3 analyze.py -h` to see the available command line args. The required ones are chat name (`-c`) of your iMessage group chat and your MacOS username (e.g. `/Users/{seany4ng}` => `seany4ng`). To find your MacOS username, run pwd from any directory and you'll see your full path.
5. Run the python script accordingly: `python3 analyze.py -c "secret chat" -u "seany4ng"`. Feel free to add more args for customizability, using above command to see available ones.

If you have any questions or concerns, email me at szyang [at] berkeley [dot] edu.