# Dino Bot (Computer Vision AI)

This project is an AI bot designed to play the Chrome Dino Game automatically using computer vision techniques. It captures a specific region of the screen where the game is running, processes the image to detect obstacles (cacti and birds), and simulates pressing the spacebar to make the dinosaur jump over them.

## Features

* **Real-time Screen Capture:** Efficiently captures a defined region of your screen using `mss`.
* **Obstacle Detection:** Utilizes OpenCV for image preprocessing (grayscale, thresholding, Canny edge detection, dilation) to reliably identify upcoming obstacles.
* **Automated Jumping:** Triggers a jump (simulates spacebar press via `pyautogui`) when an obstacle approaches a predefined "jump distance" threshold.
* **Configurable Game Region:** Parameters for screen capture and image cropping are fully customizable to adapt to different screen resolutions and game window positions.
* **Visual Feedback:** Displays the processed game screen with detected obstacles and visual aids.
* **Performance Monitoring:** Integrates FPS (Frames Per Second) display for performance tracking.

## Prerequisites

* Python (3.7 or higher recommended)
* The Chrome Dino Game running in a browser window.
* Basic understanding of setting screen coordinates for screen capture.

## Installation

1.  **Clone or Download the Repository:**
    Get the project files to your local machine.

2.  **Install Required Libraries:**
    Open your terminal or command prompt and run:
    ```bash
    pip install opencv-python numpy pyautogui mss cvzone
    ```

## Usage

1.  **Open Chrome Dino Game:**
    Navigate to the Chrome Dino Game (e.g., by typing `chrome://dino` in your browser's address bar when offline, or by hitting spacebar on the "No internet" page).
    * **Important:** The game window *must* be visible on your screen where the bot is configured to capture. Ensure no other windows are overlapping the game area.

2.  **Calibrate Screen Capture Parameters:**
    Open `main.py` and carefully adjust the parameters in the `DinoBot` constructor within the `if __name__ == "__main__":` block:
    * `monitor_x`, `monitor_y`: Top-left coordinates of the rectangular region *on your screen* that contains the Dino game window.
    * `monitor_width`, `monitor_height`: Dimensions of this capture region.
    * `crop_row_start`, `crop_row_end`, `crop_col_start`: These define the specific "look-ahead" area *within* the captured region where the bot will search for obstacles. This is crucial for performance and accuracy.
    * `jump_distance`: This is the X-coordinate (relative to the *cropped* game window's left edge) at which the bot will trigger a jump if an obstacle is detected.
    * **Tip:** You might need to run the script, observe the "DinoBot Game Window", and iteratively adjust these values until the bot accurately captures the game area and jumps effectively.

3.  **Run the Bot:**
    Open your terminal or command prompt, navigate to the project directory, and execute the script:
    ```bash
    python main.py
    ```

4.  **Observe and Enjoy:**
    * A new window titled "DinoBot Game Window" will appear, showing the bot's perspective of the game.
    * The bot will automatically play the Dino game by detecting obstacles and jumping.
    * Press `q` in the terminal or click on the "DinoBot Game Window" and press `q` to stop the bot.

## How It Works

The bot operates in a continuous loop, performing the following steps for each frame:

1.  **Screen Capture (`_capture_screen_region`):** It captures a defined rectangular region of your screen, converting it into an OpenCV-compatible image format.
2.  **Image Cropping:** The captured image is further cropped to focus only on the relevant game area where obstacles appear (the "look-ahead" zone for the dinosaur).
3.  **Image Preprocessing (`_preprocess_image`):**
    * The cropped image is converted to grayscale.
    * An inverse binary threshold is applied to highlight dark obstacles against a lighter background.
    * Canny edge detection is performed to find the outlines of potential obstacles.
    * The detected edges are dilated (thickened) to make them more prominent and easier to detect by contour finding.
4.  **Obstacle Detection (`_find_obstacles`):**
    * `cvzone.findContours` is used on the preprocessed image to identify contours, which represent obstacles.
    * A `minArea` filter ensures that only sufficiently large objects (likely obstacles) are considered.
5.  **Game Logic (`_apply_game_logic`):**
    * If obstacles are found, they are sorted by their X-coordinate to identify the one closest to the dinosaur.
    * A green line is drawn on the visualization to indicate the `jump_distance` threshold.
    * If the leftmost obstacle's X-coordinate falls below the `jump_distance` threshold, `pyautogui.press("space")` is called, simulating a jump.
6.  **Display:** The processed game view (with detected obstacles and jump lines) is displayed in a dedicated window, along with the current FPS.

## Customization & Troubleshooting

* **Calibration is Key:** The most common issue is incorrect calibration of screen capture and crop parameters. Experiment with these values thoroughly.
* **Lighting/Contrast:** If the game's appearance changes (e.g., dark mode), the `cv2.threshold` value (`127`) might need adjustment.
* **Obstacle Size:** The `minArea=100` in `_find_obstacles` can be tuned. If the bot misses small obstacles or detects too much noise, adjust this value.
* **Jump Timing:** The `jump_distance` is critical. If the bot jumps too early or too late, adjust this pixel value.
