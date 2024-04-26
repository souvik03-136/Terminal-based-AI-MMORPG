import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)



def generate_dnd_maze():
    text = "This API aims to create a captivating text-based dungeon maze adventure." \
           " It will generate a randomized maze layout with clear start and end points," \
           " allowing players to navigate using WASD controls." \
           " Combat encounters with randomly generated monsters like goblins," \
           " skeletons, and spiders will be triggered using the 'F' key," \
           " requiring players to utilize their character's stats and abilities for victory." \
           " Inventory management will be crucial, with '0 to 9' keys providing access to items like healing potions," \
           " weapons, and tools, which can be used strategically." \
           " The maze will be riddled with traps, environmental hazards, and puzzles" \
           ", adding layers of complexity and challenge." \
           " Hidden passages and randomly generated treasures will reward exploration," \
           " while varying difficulty levels and potential character customization options will enhance replayability." \
           " Through API endpoints, the system will process player actions, generate responses," \
           " and manage all aspects of the adventure, delivering an immersive and engaging text-based experience."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(text)
    return response.text


maze_result = generate_dnd_maze


def play(user_input):
    maze1 = f"The player navigates through the maze using the following commands: w (up), a (left), s (down), d (right). " \
            f"Based on the command, describe the scenario in the maze or provide the description of the player's current position. " \
            f"Initially, the maze description or design looks like this: {maze_result}. " \
            f"User Input: {user_input}"
    model = genai.GenerativeModel("gemini-pro")
    completion = model.generate_content(maze1)
    return completion.text
