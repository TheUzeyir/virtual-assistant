
import cv2
import requests
import base64

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened!")
    exit()

print("JARVIS Vision is active!")
print("Show an object and press A to analyze.")
print("Press Q to close.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    cv2.imshow("JARVIS LIVE VISION", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("a"):
        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            print("Image encoding failed.")
            continue

        image_base64 = base64.b64encode(
            buffer.tobytes()
        ).decode("utf-8")

        print("\nJARVIS is analyzing...")

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5vl:3b",
                    "prompt": "Describe the object you see. Answer in simple English.",
                    "images": [image_base64],
                    "stream": False
                },
                timeout=120
            )

            response.raise_for_status()
            answer = response.json()["response"]

            print("\nJARVIS:", answer)

        except requests.RequestException as error:
            print("AI Error:", error)

    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
