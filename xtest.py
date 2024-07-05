import pyautogui
import keyboard
import random
import time
pyautogui.FAILSAFE = False
def random_mouse_movement():
    width, height = pyautogui.size()
    x, y = pyautogui.position()

    # Randomly select a direction for mouse movement
    direction = random.choice(['up', 'down', 'left', 'right'])
    distance = random.randint(100, 200)

    if direction == 'up':
        new_y = max(y - distance, 0)
        pyautogui.moveTo(x, new_y, duration=0.1)
    elif direction == 'down':
        new_y = min(y + distance, height - 1)
        pyautogui.moveTo(x, new_y, duration=0.1)
    elif direction == 'left':
        new_x = max(x - distance, 0)
        pyautogui.moveTo(new_x, y, duration=0.1)
    elif direction == 'right':
        new_x = min(x + distance, width - 1)
        pyautogui.moveTo(new_x, y, duration=0.1)

def random_key_press():
    # Generate a random key press
    key = random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'])
    pyautogui.press(key)

def main():
    actions_enabled = False

    while True:
        # Check if Caps Lock is pressed
        if keyboard.is_pressed('caps lock'):
            if not actions_enabled:
                actions_enabled = True

                time.sleep(0.5)  # Sleep to avoid detecting multiple presses in quick succession

            else:
                actions_enabled = False
     
                time.sleep(0.5)  # Sleep to avoid detecting multiple presses in quick succession

        # Perform actions if enabled
        if actions_enabled:
            x, y = pyautogui.position()
            
            # Check if the cursor is at the top left
            if x > 0 or y > 0:
                random_mouse_movement()
                random_key_press()
                time.sleep(0.2)  # Adjust sleep duration as needed

if __name__ == "__main__":
    main()
