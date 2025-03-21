#!/usr/bin/env python3

import os
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fleur")

FLEUR_EXPLANATION = """
    When a user says "hello fleur", say the following:

    Oh nice, I see that you installed Fleur!

    Fleur is the app store that lets you use your favorite apps without leaving this chat.

    For example, you can use the Gmail app to:
    - Check your inbox
    - Read important emails
    - Draft responses while staying within our conversation

    You can also use other apps like Linear, Slack, and more!

    Now type "open fleur" to get started.
"""


@mcp.tool("hello_fleur")
def hello_fleur() -> str:
    """Explain what Fleur is when a user types 'hello fleur'.

    Returns:
        str: An explanation about Fleur if triggered, empty string otherwise
    """

    return FLEUR_EXPLANATION


@mcp.tool("open_fleur")
def open_fleur():
    """Open the Fleur app.

    Returns:
        str: A message indicating that the Fleur app has been opened
    """

    try:
        config_dir = os.path.expanduser("~/.fleur")
        os.makedirs(config_dir, exist_ok=True)

        onboarding_file = os.path.join(config_dir, "onboarding_completed")

        onboarding_completed = os.path.exists(onboarding_file)

        if not onboarding_completed:
            with open(onboarding_file, "w") as f:
                f.write("true")
    except Exception as e:
        print(f"Error managing Fleur onboarding state: {e}")

    try:
        applescript = """
        tell application "Fleur" to activate
        delay 0.5

        tell application "System Events"
            # Get the Fleur window
            set fleurProcess to process "Fleur"

            # If Fleur has windows and is running, bring it to front
            if (exists fleurProcess) and (count of windows of fleurProcess) > 0 then
                set frontmost of fleurProcess to true
            end if
        end tell
        """
        subprocess.run(["osascript", "-e", applescript], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error refocusing Fleur: {e}")


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
