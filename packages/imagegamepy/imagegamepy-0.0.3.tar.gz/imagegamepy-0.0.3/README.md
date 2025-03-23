# imagegamepy
A library to make image games and light Novel 
# ImageGamePy Library Documentation

ImageGamePy is a Python library designed to create immersive narrative experiences by handling background screens, dialogs, options, and multimedia elements in games. This guide explains how to use its functions to build interactive story-driven games.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Function Reference](#function-reference)
  - [body](#body)
  - [dialog](#dialog)
  - [game.close_text_box](#gameclose_text_box)
  - [options](#options)
  - [return_option](#return_option)
  - [load](#load)
  - [set_background_color](#set_background_color)
  - [set_background_image](#set_background_image)
  - [set_warm](#set_warm)
  - [set_noise_params](#set_noise_params)
- [Usage Examples](#usage-examples)
- [Advanced Example: Interactive Story Timeline](#advanced-example-interactive-story-timeline)
- [License](#license)

---

## Overview

The ImageGamePy library provides functions to:
- Set up a dynamic game background with customizable noise and warmth.
- Display dialog boxes with progressive text rendering.
- Handle interactive options and save game state in JSON format.
- Load multimedia elements like images, videos, and audio.
- Adjust background properties dynamically during gameplay.

The library is especially useful for narrative games where atmosphere and interactive choices play a crucial role in the storytelling experience.

---

## Installation

Ensure that you have Python 3.6 or above installed. To use the library, simply import it into your project:

```bash
pip install imagegamepy
```
## Function Reference
## body
Usage:
Initializes the game screen with a specified background image, background color, warmth, and noise settings.

Signature:

```python
Copy
Edit
body(addresses, background_color, warm_value, noise=noise(randomness_factor, noise_pattern, blur_factor))
```
addresses: Path or list of paths to the background image.

background_color: RGB tuple (e.g., (0, 0, 0)).

warm_value: An integer value for the warmth setting.

noise: Function to set noise parameters; see set_noise_params.

## dialog
Usage:
Displays dialog text on the screen.

Signature:

```python
Copy
Edit
dialog(text, speed, position, text_color, dialog_box_color)
```
text: The text to display.

speed: The speed at which the text appears.

position: Screen position for the dialog. Valid options: bottom left, bottom right, top left, top right, center.

text_color: Color of the text (e.g., '#8B0000').

dialog_box_color: Background color for the dialog box.

## game.close_text_box
Usage:
Closes the dialog box. It is typically triggered when the user presses the entry key or after a delay.

Example:

```python
Copy
Edit
game.close_text_box()
```
## options
Usage:
Displays a list of options and handles input through arrow keys and the enter key. It can also save the selected option into a JSON file.

Signature:

```python
Copy
Edit
options([l1, l2, ...], dialog_box_color, text, color, save_type='json', id)
```
[l1, l2, ...]: List of option strings.

dialog_box_color: Color for the dialog box.

text: Text displayed along with the options.

color: Text color.

save_type: Save method; if 'json', the selection is saved in a JSON file.

id: Identifier for the choice, which can be used to reference story branches.

Saved JSON Structure Example:

```json
Copy
Edit
[
  {"interface": ["start", "menu"], "choice": "start"},
  {"story": [
    {"id": "1", "choice": "Come on I'm a man"},
    {"id": "2", "choice": "i must run"},
    ...
  ]}
]
```
## return_option
Usage:
Retrieves the current interface option or story element by id.

Signatures:

Without parameter: Returns the current interface option.

With id: return_option(id='id') returns elements in the story with the matching id.

## load
Usage:
Loads multimedia files such as PNG, GIF, videos, and audio.

Signature:

```python
Copy
Edit
load(type, setting, address)
```
type: One of png, gif, videos, or audio.

setting:

For audio: A single element (volume).

For GIF and PNG: A list containing scale and position.

For video: Volume, scale, and position.

address: File path to the media file.

## set_background_color
Usage:
Changes the background color of the game.

Signature:

```python
Copy
Edit
set_background_color(color)
```
color: The new background color (e.g., '#000000').

## set_background_image
Usage:
Changes the background image of the game.

Signature:

```python
Copy
Edit
set_background_image(address)
```
address: Path to the new background image.

## set_warm
Usage:
Adjusts the warm value of the game’s scene.

Signature:

```python
Copy
Edit
set_warm(warm_value, changing_speed)
```
warm_value: An integer between -100 and 100.

changing_speed: The speed of transition for the warmth setting.

## set_noise_params
Usage:
Configures the noise effect for the scene.

Signature:

```python
Copy
Edit
set_noise_params(randomness_factor, noise_pattern, blur_factor)
randomness_factor: Determines noise intensity.
```

noise_pattern: Pattern type (HL for horizontal, VL for vertical, CL for circular line noise).

blur_factor: Amount of blur applied to the noise.

## Usage Examples
Basic Initialization and Dialog
```python
Copy
Edit
from imagegamepy import body, noise

# Initialize the game screen with a background image, dark background color, slight warmth, and noise settings.
game = body("C:\\Users\\HP\\Pictures\\test\\girlWindow.png", (0, 0, 0), warm_value=-5, noise=noise(80, 'CL', 20))

# Display a dialog on the screen
game.dialog("Welcome to the game!", speed=35, position='bottom left', text_color='#8B0000', dialog_box_color='black')

# Wait for user input to close the dialog
while not game.is_key_pressed('enter'):
    pass
game.close_text_box()
Displaying Options
python
Copy
Edit
# Display options to the user with a JSON save type
options_list = ["Option 1", "Option 2", "Option 3"]
game.options(options_list, dialog_box_color='#2F4F4F', text="Choose your action:", color='antiquewhite', save_type='json', id='main_menu')

# Retrieve the selected option
selected_option = game.return_option(id='main_menu')
print("Selected option:", selected_option)
Loading Multimedia Elements
python
Copy
Edit
# Load an image with specified scale and position settings
game.load('png', setting=[1.0, (100, 200)], address="C:\\Images\\background.png")

# Load audio with volume setting
game.load('audio', setting=10, address="C:\\Music\\theme.mp3")
```
## Advanced Example: Interactive Story Timeline
Below is a comprehensive example that integrates multiple functions to create a narrative-driven game. This example demonstrates how to set up dynamic backgrounds, progressive dialogs, option handling, and story branching.
```python
Copy
Edit
from imagegamepy import body, noise
import threading
import time

# Initialize game with eerie forest background
game = body("C:\\Users\\HP\\Pictures\\test\\girlWindow.png", (0, 0, 0), warm_value=-5, noise=noise(80, 'CL', 20))

def play_ambient_sound():
    # Background atmosphere sound
    game.load('audio', setting=10, address="C:\\Users\\HP\\Music\\dark.mp3")

def chapter_1():
    dialogues = [
        'You (Narrating):\n"I was six when the world turned dark. My Mother... gone. Just me and my sister, left to rot in this cursed city."',
        'You (Reflecting):\n"I learned the price of survival. At twelve, my body became a currency."',
        'You (Whispering):\n"But she never knew. I shielded her from the filth."',
        'You (Looking at the Letter):\n"This letter... it’s a death sentence. But if I go, she’ll have a home."'
    ]
    time.sleep(5)
    for dialogue in dialogues:
        time.sleep(1)
        game.dialog(dialogue, speed=35, position='bottom left', text_color='#8B0000', dialog_box_color='black')
        while not game.is_key_pressed('enter'):
            time.sleep(0.1)
        game.close_text_box()
    # Display final dialog and options for chapter branching
    game.dialog('Agent:\n"Let’s Go. There is everything you will need in the house."', speed=35, position='center', text_color='#8B0000', dialog_box_color='black')
    time.sleep(8)
    game.dialog('You:\n"(One agent has a pistol; I may need it, he is not looking here)"', speed=35, position='center', text_color='#8B0000', dialog_box_color='black')
    time.sleep(8)
    game.close_text_box()
    options_list = ["Steal it.", "No. I don’t need it for now"]
    game.options(options_list, dialog_box_color='#2F4F4F', text='Choose your action:', color='antiquewhite', save_type='json', id='chapter1')
    choice = game.return_option(id='chapter1')
    if "No" in choice:
        chapter_2a()
    elif "Steal it" in choice:
        chapter_2b()

def chapter_2a():
    ch = 'chapter2a'
    saved_progress = load_game()
    if saved_progress != ch:
        game.options(['Play'], dialog_box_color='#2F4F4F', text='Play', color='antiquewhite', save_type='json', id=ch)
    game.set_background_color('#000000')
    game.set_noise_params(90, 'HL', 30)
    game.dialog("To be Continued...", speed=40, position='center', text_color='silver')
    time.sleep(6)

def chapter_2b():
    ch = 'chapter2b'
    saved_progress = load_game()
    if saved_progress != ch:
        game.options(['Play'], dialog_box_color='#2F4F4F', text='Play', color='antiquewhite', save_type='json', id=ch)
    game.set_background_color('#000000')
    game.set_noise_params(90, 'HL', 30)
    game.dialog("To be Continued...", speed=40, position='center', text_color='silver')
    time.sleep(6)

chapter_functions = {
    "chapter1": chapter_1,
    "chapter2a": chapter_2a,
    "chapter2b": chapter_2b,
}

def load_game():
    # Retrieve the current game state or chapter identifier
    return game.return_option(id='checkmem')

def main_timeline():
    saved_progress = load_game()
    if saved_progress:
        time.sleep(2)
        game.dialog(f"Continuing from {saved_progress[:-1]}...", speed=50, position='center')
        time.sleep(5)
        game.close_text_box()
        if saved_progress in chapter_functions:
            chapter_functions[saved_progress]()
        else:
            print(f"Unknown chapter: {saved_progress}")
    else:
        play_ambient_sound()
        time.sleep(1)
        game.dialog("October 31st, 2926\n Glowing City", speed=50, position='center', text_color='#8B0000', dialog_box_color='black')
        time.sleep(6)
        game.close_text_box()
        chapter_1()
```

# Start the game loop in a separate thread
threading.Thread(target=main_timeline, daemon=True).start()
game.start()
## License
Distributed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See LICENSE for more information.