# imessage-summary
Have you ever opened your phone to 300 messages in a group chat?
No longer do you have to scroll through hundreds of irrelevant messages.

## Quickstart guide
Currently this app runs as a Python script, but this will change (when I have sufficient time to make changes).

1. Clone/fork this repo
2. Give your terminal (Terminal, iTerm2, Warp, etc.) full disk access. You can find this in Settings > Privacy & Security.
3. Create a `.env.local` file in the directory of this repo and paste your Gemini API key into it. If you don't have a Gemini API key, just make one -- it's free
```
GEMINI_API_KEY=example_api_key
```
4. Run `pip install -r requirements.txt`. Recommend doing this in a virtualenv
5. Run `python3 analyze.py -h` to see the available command line args. The required ones are chat name (`-c`) of your iMessage group chat and your MacOS username (e.g. `/Users/{seany4ng}` => `seany4ng`). To find your MacOS username, run pwd from any directory and you'll see your full path.
6. Run the python script accordingly: `python3 analyze.py -c "secret chat" -u "seany4ng"`. Feel free to add more args for customizability, using above command to see available ones
Credits: https://github.com/my-other-github-account/imessage_tools was helpful in figuring out how to decode the attributed body

If you get stuck email me szyang@berkeley.edu