#!/usr/bin/env python3
"""
Raspberry Pi QR Code Scanner
Uses a webcam to find and decode QR codes (like Spotify links).

How to run:
1. Make sure your Pi is connected to a monitor and keyboard.
OR
2. If using SSH, connect with X11 forwarding (e.g., `ssh -X pi@<your-pi-ip>`)
   (You may need to install XQuartz on a Mac)
"""

import cv2
from pyzbar.pyzbar import decode
import time

def find_spotify_qr():
    """
    Captures video from the webcam, detects QR codes, and prints the decoded link.
    """
    
    # Initialize the webcam. 
    # '0' is usually the default (your Logitech webcam).
    # If it doesn't work, try '1' or '-1'.
    print("Starting webcam... (Press 'q' in the video window to quit)")
    cap = cv2.VideoCapture(0)
    
    # Check if the webcam opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        print("Is it plugged in? Is it being used by another program?")
        print("Try rebooting or changing the '0' in cv2.VideoCapture(0) to 1.")
        return

    # Set a small delay between detections so we don't spam the console
    last_detected_link = ""
    last_detection_time = 0
    COOLDOWN_PERIOD = 5 # seconds

    try:
        while True:
            # Read one frame from the video stream
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break

            # Use pyzbar's 'decode' function to find all QR/barcodes in the frame
            qr_codes = decode(frame)

            found_link = ""

            # Loop over all detected codes
            for code in qr_codes:
                # 1. Decode the data
                # The 'data' attribute is in bytes, so we decode it to a string
                link = code.data.decode('utf-8')
                found_link = link # Store for drawing later

                # 2. Check if it's a new link and we're past the cooldown
                current_time = time.time()
                if link != last_detected_link or (current_time - last_detection_time) > COOLDOWN_PERIOD:
                    print("="*30)
                    print(f"  FOUND QR CODE!")
                    print(f"  Link: {link}")
                    print("="*30)
                    
                    last_detected_link = link
                    last_detection_time = current_time

                # 3. Draw a bounding box and text on the video frame
                # Get the (x, y, width, height) of the QR code
                (x, y, w, h) = code.rect
                # Draw a green rectangle around it
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
                
                # Put the decoded text above the box
                cv2.putText(frame, link, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


            # Display the video frame in a window called 'QR Code Scanner'
            cv2.imshow('QR Code Scanner', frame)

            # Wait for 1ms. If the 'q' key is pressed, break the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quitting...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam released and windows closed.")

# --- Run the main function ---
if __name__ == '__main__':
    find_spotify_qr()
