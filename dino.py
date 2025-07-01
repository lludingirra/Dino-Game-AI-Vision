import math # Import the math module (not directly used here, but often useful for geometry).
import time # Import the time module for time-related functions (e.g., measuring duration).
import cv2 # Import the OpenCV library for image and video processing.
import cvzone # Import the cvzone library for computer vision helper functions (e.g., findContours, FPS).
import numpy as np # Import numpy for numerical operations, especially for array manipulation.
import pyautogui # Import pyautogui for programmatic control of the mouse and keyboard (to press spacebar).
from cvzone.FPS import FPS # Import FPS class from cvzone to calculate and display frames per second.
from mss import mss # Import mss for efficient cross-platform screen capturing.
# 'types' was removed because it's not directly importable from 'mss' and was causing a type hint error.
# The original line 'from mss import mss, types' should be 'from mss import mss'.

class DinoBot:
    """
    A bot to play the Chrome Dino Game using screen capture and image processing.
    It detects obstacles and presses the spacebar to jump.
    """

    def __init__(self,
                 monitor_x: int = 450,
                 monitor_y: int = 300,
                 monitor_width: int = 650,
                 monitor_height: int = 200,
                 crop_row_start: int = 100,
                 crop_row_end: int = 140,
                 crop_col_start: int = 110,
                 jump_distance: int = 65):
        """
        Initializes the DinoBot.

        Args:
            monitor_x (int): Top-left X coordinate of the screen region to capture.
            monitor_y (int): Top-left Y coordinate of the screen region to capture.
            monitor_width (int): Width of the screen region to capture.
            monitor_height (int): Height of the screen region to capture.
            crop_row_start (int): Starting row for cropping within the captured image.
            crop_row_end (int): Ending row for cropping within the captured image.
            crop_col_start (int): Starting column for cropping within the captured image.
            jump_distance (int): X-coordinate threshold for an obstacle to trigger a jump.
        """
        self.sct = mss() # Initialize MSS for screen capturing.
        self.fps_reader = FPS() # Initialize FPS counter from cvzone.
        self.pyautogui_instance = pyautogui # Assign pyautogui for pressing the spacebar.

        # Define the region of the screen to capture (adjust based on game window position).
        # The 'types.Monitor' type hint was removed as 'types' is not directly importable.
        # This line will still function as it's a runtime dict definition, not a type hinting error.
        self.monitor_region = {
            "top": monitor_y,
            "left": monitor_x,
            "width": monitor_width,
            "height": monitor_height
        }

        # Define cropping parameters for the game area within the captured region.
        self.crop_params = {
            "row_start": crop_row_start,
            "row_end": crop_row_end,
            "col_start": crop_col_start
        }

        self.jump_distance = jump_distance # Store the jump distance threshold.

        print(f"DinoBot initialized. Capture region: {self.monitor_region}, "
              f"Crop: rows {crop_row_start}-{crop_row_end}, columns from {crop_col_start}. "
              f"Jump distance: {jump_distance}")

    def _capture_screen_region(self) -> np.ndarray:
        """
        Captures a specific region of the screen using MSS and converts it to OpenCV format.

        Returns:
            np.ndarray: The captured screen region as an OpenCV BGR image.
        """
        # sct.grab returns raw bytes screenshot in BGRA color space.
        screenshot = self.sct.grab(self.monitor_region)
        # Convert to a NumPy array (BGRA) and then to BGR for OpenCV.
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def _preprocess_image(self, img_crop: np.ndarray) -> np.ndarray:
        """
        Preprocesses the cropped game image to highlight obstacles.

        Args:
            img_crop (np.ndarray): The cropped image containing the game area.

        Returns:
            np.ndarray: The preprocessed binary image with dilated Canny edges.
        """
        # Convert to grayscale for thresholding.
        gray_frame = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        
        # Apply inverse binary thresholding to isolate dark objects (obstacles).
        # Objects darker than 127 become white (255), others become black (0).
        _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Apply Canny edge detection to find edges in the binary image.
        canny_frame = cv2.Canny(binary_frame, 50, 50) # Low and high thresholds can be tuned.

        # Dilate the edges to make them thicker and easier to detect.
        kernel = np.ones((5, 5), np.uint8) # 5x5 kernel for dilation.
        dilated_frame = cv2.dilate(canny_frame, kernel, iterations=2) # Dilate twice for stronger features.

        return dilated_frame

    def _find_obstacles(self, img_crop: np.ndarray, img_pre: np.ndarray) -> tuple[np.ndarray, list]:
        """
        Finds contours (potential obstacles) in the preprocessed image.

        Args:
            img_crop (np.ndarray): The original cropped image on which contours will be drawn.
            img_pre (np.ndarray): The preprocessed image where contours are to be found.

        Returns:
            tuple[np.ndarray, list]: A tuple containing:
                                     - The image with drawn contours.
                                     - A list of found contours (if any).
        """
        # Use cvzone's findContours to detect obstacles.
        # minArea ensures only reasonably sized objects are considered.
        # filter=None means no additional filtering based on shape/aspect ratio.
        img_contours, con_found = cvzone.findContours(img_crop, img_pre, minArea=100, filter=None)
        return img_contours, con_found

    def _apply_game_logic(self, img_contours: np.ndarray, con_found: list) -> np.ndarray:
        """
        Applies game logic to decide if the dinosaur needs to jump and draws visual aids.

        Args:
            img_contours (np.ndarray): The image with contours drawn on it (for visualization).
            con_found (list): List of detected contours with their properties.

        Returns:
            np.ndarray: The image with visual aids for game logic.
        """
        if con_found:
            # Sort contours by their X-coordinate (top-left X of bounding box) to find the leftmost obstacle.
            left_most_contour = sorted(con_found, key=lambda x: x["bbox"][0])

            # Draw a line indicating the jump distance threshold.
            cv2.line(img_contours,
                     (self.jump_distance, left_most_contour[0]["bbox"][1] + 10), # Start of the line (at jump distance X).
                     (left_most_contour[0]["bbox"][0], left_most_contour[0]["bbox"][1] + 10), # End of the line (at obstacle X).
                     (0, 200, 0), # Green color.
                     10) # Thickness.

            # If the leftmost obstacle is within the jump distance, press the spacebar.
            if left_most_contour[0]["bbox"][0] < self.jump_distance:
                self.pyautogui_instance.press("space")
                print("Jump!") # Debug output to console.
        return img_contours

    def run(self):
        """
        Runs the main loop of the DinoBot.
        Captures the screen, processes the image, applies game logic, and displays results.
        Press 'q' to exit.
        """
        print("DinoBot started. Press 'q' to exit.")
        while True:
            # Step 1 - Capture the screen region of the game.
            img_game = self._capture_screen_region()

            # Step 2 - Crop the image to the desired game area within the captured region.
            cp = self.crop_params
            # Slicing syntax: [row_start:row_end, col_start:col_end]
            # If col_end is omitted, it goes to the end.
            img_crop = img_game[cp["row_start"]:cp["row_end"], cp["col_start"]:]

            # Step 3 - Preprocess the Image.
            img_pre = self._preprocess_image(img_crop)

            # Step 4 - Find Obstacles.
            # img_contours will be img_crop with contours drawn on it.
            # Use .copy() to avoid modifying the original img_crop reference.
            img_contours, con_found = self._find_obstacles(img_crop.copy(), img_pre)

            # Step 5 - Apply Game Logic and retrieve the updated contours for display.
            img_contours_with_logic = self._apply_game_logic(img_contours, con_found)

            # Step 6 - Display Result.
            # Replace the cropped region in the full game screenshot with the processed one.
            img_game[cp["row_start"]:cp["row_end"], cp["col_start"]:] = img_contours_with_logic

            # Update and display FPS.
            fps, img_game = self.fps_reader.update(img_game)
            # You can also draw FPS manually if cvzone.FPS doesn't suit your needs.
            # cv2.putText(img_game, f'FPS: {int(fps)}', (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            cv2.imshow("DinoBot Game Window", img_game) # Use a more descriptive window name.

            # Check if 'q' key is pressed to exit.
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("Exiting DinoBot.")
                break

        # Release resources when exiting the loop.
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # --- IMPORTANT ---
    # 1. Open the Chrome Dino Game in your browser.
    # 2. Adjust 'monitor_x', 'monitor_y', 'monitor_width', 'monitor_height'
    #    and 'crop_row_start', 'crop_row_end', 'crop_col_start'
    #    based on the position and size of your game window.
    #    You will likely need to experiment with these values.
    #    'jump_distance' (e.g., 65 pixels) also requires calibration.
    #    'jump_distance' is an X-coordinate threshold relative to the left edge of the cropped window.

    # Example initialization with default values (as in your original code).
    # You might need to change these significantly based on your screen setup!
    dino_bot = DinoBot(
        monitor_x=450,          # X coordinate of the top-left corner of the capture window.
        monitor_y=300,          # Y coordinate of the top-left corner of the capture window.
        monitor_width=650,      # Width of the capture window.
        monitor_height=200,     # Height of the capture window.
        crop_row_start=100,     # Starting row for cropping within the captured window.
        crop_row_end=140,       # Ending row for cropping within the captured window.
        crop_col_start=110,     # Starting column for cropping within the captured window.
        jump_distance=65        # X-coordinate threshold for jumping.
    )
    dino_bot.run()