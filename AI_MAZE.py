import google.generativeai as genai

genai.configure(api_key="api_key")

def generate_dnd_maze():
    text = "Develop a playable Dungeons and Dragons scenario where the player navigates a 20x40 ASCII dungeon maze using the W, A, S, D keys." \
           " Draw the maze with a designated start (S) and end (E) point. Integrate components like traps and challenges." \
           " Offer commands for gameplay and request descriptions for each new scenario. " \
           "Commence by illustrating the initial maze and setting the stage for an immersive adventure."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text)
    return response.text

maze_result = generate_dnd_maze


def play(user_input):
    maze1 = f"The player navigates through the maze using the following commands: w (up), a (left), s (down), d (right). "\
          f"Based on the command, describe the scenario in the maze or provide the description of the player's current position. "\
          f"Initially, the maze description or design looks like this: {maze_result}. "\
          f"User Input: {user_input}"
    model = genai.GenerativeModel("gemini-pro")
    completion = model.generate_content(maze1)
    return completion.text
