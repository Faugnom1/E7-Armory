import cv2
import numpy as np

def capture_screenshot():
    # Command to capture screenshot from Bluestacks using adb
    # adb_path = 'path/to/adb'
    # os.system(f"{adb_path} exec-out screencap -p > screenshot.png")
    # For testing, let's use a static image
    screenshot_path = 'path/to/screenshot.png'
    return cv2.imread(screenshot_path)

def match_templates(image, templates):
    detected_units = []
    for unit_name, template_path in templates.items():
        template = cv2.imread(template_path, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            detected_units.append(unit_name)
            cv2.rectangle(image, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)
    return detected_units

def main():
    templates = {
        'Savior Adin': 'path/to/savior_adin_template.png',
        'Kise': 'path/to/kise_template.png',
        # Add paths for more unit templates
    }
    image = capture_screenshot()
    units = match_templates(image, templates)
    print("Detected units:", units)
    # Send the detected units to the React app (e.g., via WebSocket or HTTP request)

if __name__ == "__main__":
    main()
