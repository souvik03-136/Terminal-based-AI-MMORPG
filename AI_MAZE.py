import google.generativeai as genai

genai.configure(api_key="api_key")

def generate_dnd_maze():
    text = "Craft an engaging Dungeons and Dragons scenario featuring a 20x40 ASCII dungeon maze, where players navigate using W, A, S, and D keys." \
           " Begin with an illustrated maze showing a designated start (S) and end (E) point. " \
           "Incorporate traps, challenges, and commands for gameplay, seeking descriptions for each scenario. " \
           "Create an immersive adventure by setting the stage with a detailed maze description, storyline, and challenges awaiting the players."
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
