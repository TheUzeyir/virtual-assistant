import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera could not be opened!")
    exit()

print("Camera is working! Press Q to close.")

while True:
    success, frame = camera.read()

    if not success:
        break

    cv2.imshow("JARVIS Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()