import cv2
import numpy as np
import mediapipe as mp
from collections import deque

# Initialize variables for handling color points and indices
bpoints = [deque(maxlen=1024)]  # Color 0 - Orange Red
gpoints = [deque(maxlen=1024)]  # Color 1 - Green  
rpoints = [deque(maxlen=1024)]  # Color 2 - Blue
ypoints = [deque(maxlen=1024)]  # Color 3 - Yellow
ppoints = [deque(maxlen=1024)]  # Color 4 - Purple
opoints = [deque(maxlen=1024)]  # Color 5 - Orange
epoints = [deque(maxlen=1024)]  # Eraser points
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0
purple_index = 0
orange_index = 0
eraser_index = 0

# Drawing order tracking - keeps track of chronological order
drawing_order = []  # List of (color_index, stroke_index, timestamp) tuples
stroke_counter = 0

# Initialize color constants and canvas setup - Modern theme
colors = [(255, 87, 51), (46, 204, 113), (52, 152, 219), (241, 196, 15), (155, 89, 182), (230, 126, 34)]  # Modern vibrant colors
colorIndex = 0

# Pen types with different thicknesses and styles
pen_types = [
    {"name": "FINE", "thickness": 2, "style": "fine"},      # Fine tip pen
    {"name": "MARKER", "thickness": 8, "style": "marker"},   # Medium marker
    {"name": "BRUSH", "thickness": 15, "style": "brush"}     # Thick brush
]
pen_type_index = 0

# Create clean dark canvas background (no controls)
paintWindow = np.zeros((471, 636, 3), dtype=np.uint8)
# Create modern dark gradient background
for i in range(471):
    gradient_value = int(25 + (15 * i / 471))
    paintWindow[i, :] = [gradient_value, gradient_value, gradient_value]

# Create a mask to track erased areas
erased_mask = np.zeros((471, 636), dtype=np.uint8)

# Initialize Mediapipe for hand tracking
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Initialize the webcam
cap = cv2.VideoCapture(0)
ret = True

while ret:
    ret, frame = cap.read()

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Create modern overlay for video frame
    overlay = np.zeros((100, 640, 3), dtype=np.uint8)
    
    # Create modern dark gradient background for control bar
    for i in range(100):
        gradient_value = int(20 + (25 * i / 100))
        overlay[i, :] = [gradient_value, gradient_value, gradient_value]
    
    # Draw modern video control buttons
    def draw_video_button(img, start_point, end_point, color, text, text_color=(255, 255, 255), is_selected=False):
        # Add glow effect for selected button
        if is_selected:
            glow_start = (start_point[0] - 3, start_point[1] - 3)
            glow_end = (end_point[0] + 3, end_point[1] + 3)
            cv2.rectangle(img, glow_start, glow_end, (255, 255, 255), 2)
        
        # Main button
        cv2.rectangle(img, start_point, end_point, color, -1)
        
        # Add border
        border_color = (255, 255, 255) if is_selected else (120, 120, 120)
        cv2.rectangle(img, start_point, end_point, border_color, 2)
        
        # Calculate text position for centering
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = start_point[0] + (end_point[0] - start_point[0] - text_size[0]) // 2
        text_y = start_point[1] + (end_point[1] - start_point[1] + text_size[1]) // 2
        
        cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1, cv2.LINE_AA)

    # Pen type buttons (top row)
    cv2.putText(overlay, "PEN:", (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    draw_video_button(overlay, (60, 10), (110, 35), (70, 70, 70), "FINE", (255, 255, 255), pen_type_index == 0)
    draw_video_button(overlay, (120, 10), (180, 35), (70, 70, 70), "MARKER", (255, 255, 255), pen_type_index == 1)
    draw_video_button(overlay, (190, 10), (240, 35), (70, 70, 70), "BRUSH", (255, 255, 255), pen_type_index == 2)
    
    # Color buttons (bottom row)
    cv2.putText(overlay, "COLORS:", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    draw_video_button(overlay, (80, 45), (105, 70), colors[0], "", (255, 255, 255), colorIndex == 0)
    draw_video_button(overlay, (115, 45), (140, 70), colors[1], "", (255, 255, 255), colorIndex == 1)
    draw_video_button(overlay, (150, 45), (175, 70), colors[2], "", (255, 255, 255), colorIndex == 2)
    draw_video_button(overlay, (185, 45), (210, 70), colors[3], "", (255, 255, 255), colorIndex == 3)
    draw_video_button(overlay, (220, 45), (245, 70), colors[4], "", (255, 255, 255), colorIndex == 4)
    draw_video_button(overlay, (255, 45), (280, 70), colors[5], "", (255, 255, 255), colorIndex == 5)
    
    # Clear button
    draw_video_button(overlay, (540, 25), (610, 55), (220, 53, 69), "CLEAR", (255, 255, 255))
    
    # Current pen info
    current_pen = pen_types[pen_type_index]
    info_text = f"{current_pen['name']} {current_pen['thickness']}px"
    cv2.putText(overlay, info_text, (350, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    
    # Blend overlay with frame
    frame[0:100, :] = cv2.addWeighted(frame[0:100, :], 0.2, overlay, 0.8, 0)

    # Process hand landmarks
    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        landmarks = []
        pinky_extended = False  # Initialize pinky_extended flag
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * 640)
                lmy = int(lm.y * 480)
                landmarks.append([lmx, lmy])

            # Draw landmarks on frame with modern styling
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS,
                                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2),
                                mp.solutions.drawing_utils.DrawingSpec(color=(255, 255, 255), thickness=2))
            
            # Detect finger positions
            fore_finger = (landmarks[8][0], landmarks[8][1])
            center = fore_finger
            thumb = (landmarks[4][0], landmarks[4][1])
            pinky = (landmarks[20][0], landmarks[20][1])  # Pinky finger tip
            
            # Check if pinky is extended (eraser mode)
            # More sensitive detection - check if pinky is extended relative to other fingers
            pinky_extended = (landmarks[20][1] < landmarks[18][1] - 10) and (landmarks[20][1] < landmarks[16][1])  # Pinky tip above pinky joint and ring finger
            
            if pinky_extended:
                # Draw eraser indicator
                cv2.circle(frame, pinky, 20, (255, 255, 255), 3)
                cv2.circle(frame, pinky, 25, (255, 0, 0), 2)
                cv2.putText(frame, "ERASER", (pinky[0] - 35, pinky[1] - 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
                
                # Use pinky as center for erasing
                center = pinky
            else:
                # Draw modern finger indicator for painting
                cv2.circle(frame, center, 8, (0, 255, 255), -1)
                cv2.circle(frame, center, 12, (255, 255, 255), 2)

            # Handle button actions
            if thumb[1] - center[1] < 30:
                bpoints.append(deque(maxlen=512))
                blue_index += 1
                gpoints.append(deque(maxlen=512))
                green_index += 1
                rpoints.append(deque(maxlen=512))
                red_index += 1
                ypoints.append(deque(maxlen=512))
                yellow_index += 1
                ppoints.append(deque(maxlen=512))
                purple_index += 1
                opoints.append(deque(maxlen=512))
                orange_index += 1
                epoints.append(deque(maxlen=512))
                eraser_index += 1
                
                # Add to drawing order when starting new stroke
                indices = [blue_index, green_index, red_index, yellow_index, purple_index, orange_index]
                drawing_order.append((colorIndex, indices[colorIndex], stroke_counter))
                stroke_counter += 1
            elif center[1] <= 100:  # Increased area for new interface
                # Pen type selection (top row)
                if 60 <= center[0] <= 110:
                    pen_type_index = 0  # FINE
                elif 120 <= center[0] <= 180:
                    pen_type_index = 1  # MARKER
                elif 190 <= center[0] <= 240:
                    pen_type_index = 2  # BRUSH
                # Color selection (bottom row)
                elif 80 <= center[0] <= 105:
                    colorIndex = 0  # Color 1
                elif 115 <= center[0] <= 140:
                    colorIndex = 1  # Color 2
                elif 150 <= center[0] <= 175:
                    colorIndex = 2  # Color 3
                elif 185 <= center[0] <= 210:
                    colorIndex = 3  # Color 4
                elif 220 <= center[0] <= 245:
                    colorIndex = 4  # Color 5
                elif 255 <= center[0] <= 280:
                    colorIndex = 5  # Color 6
                # Clear button
                elif 540 <= center[0] <= 610:
                    bpoints = [deque(maxlen=512)]
                    gpoints = [deque(maxlen=512)]
                    rpoints = [deque(maxlen=512)]
                    ypoints = [deque(maxlen=512)]
                    ppoints = [deque(maxlen=512)]
                    opoints = [deque(maxlen=512)]
                    epoints = [deque(maxlen=512)]
                    blue_index = 0
                    green_index = 0
                    red_index = 0
                    yellow_index = 0
                    purple_index = 0
                    orange_index = 0
                    eraser_index = 0
                    # Clear drawing order
                    drawing_order.clear()
                    stroke_counter = 0
                    # Reset to clean dark gradient background
                    for i in range(471):
                        gradient_value = int(25 + (15 * i / 471))
                        paintWindow[i, :] = [gradient_value, gradient_value, gradient_value]
                    # Reset erased mask
                    erased_mask.fill(0)
            else:
                # Add points for drawing only (not erasing)
                if not pinky_extended:
                    # Only draw/paint if not in eraser mode
                    current_pen = pen_types[pen_type_index]
                    thickness = current_pen["thickness"]
                    
                    # Scale drawing coordinates to match paint window
                    scale_x = 636 / 640
                    scale_y = 471 / 480
                    scaled_x = int(center[0] * scale_x)
                    scaled_y = int((center[1] - 100) * scale_y) if center[1] > 100 else center[1]
                    scaled_center = (scaled_x, scaled_y)
                    
                    if colorIndex == 0:
                        bpoints[blue_index].appendleft(scaled_center)
                    elif colorIndex == 1:
                        gpoints[green_index].appendleft(scaled_center)
                    elif colorIndex == 2:
                        rpoints[red_index].appendleft(scaled_center)
                    elif colorIndex == 3:
                        ypoints[yellow_index].appendleft(scaled_center)
                    elif colorIndex == 4:
                        ppoints[purple_index].appendleft(scaled_center)
                    elif colorIndex == 5:
                        opoints[orange_index].appendleft(scaled_center)
                # Don't add any points when erasing - real-time erasing handles it
    else:
        bpoints.append(deque(maxlen=512))
        blue_index += 1
        gpoints.append(deque(maxlen=512))
        green_index += 1
        rpoints.append(deque(maxlen=512))
        red_index += 1
        ypoints.append(deque(maxlen=512))
        yellow_index += 1
        ppoints.append(deque(maxlen=512))
        purple_index += 1
        opoints.append(deque(maxlen=512))
        orange_index += 1
        epoints.append(deque(maxlen=512))
        eraser_index += 1
        
        # Add to drawing order when starting new stroke (no hand detected)
        indices = [blue_index, green_index, red_index, yellow_index, purple_index, orange_index]
        drawing_order.append((colorIndex, indices[colorIndex], stroke_counter))
        stroke_counter += 1

    # Redraw everything in chronological order to maintain proper layering
    # First clear the paint window with gradient background
    for i in range(471):
        gradient_value = int(25 + (15 * i / 471))
        paintWindow[i, :] = [gradient_value, gradient_value, gradient_value]
    
    # Then draw all strokes in chronological order
    points_arrays = [bpoints, gpoints, rpoints, ypoints, ppoints, opoints]
    
    # Sort drawing order by stroke counter to maintain chronological sequence
    sorted_drawing_order = sorted(drawing_order, key=lambda x: x[2])
    
    for color_idx, stroke_idx, _ in sorted_drawing_order:
        if color_idx < len(points_arrays) and stroke_idx < len(points_arrays[color_idx]):
            stroke_points = points_arrays[color_idx][stroke_idx]
            
            for k in range(1, len(stroke_points)):
                if stroke_points[k - 1] is None or stroke_points[k] is None:
                    continue
                
                # Get current pen thickness
                current_pen = pen_types[pen_type_index]
                thickness = current_pen["thickness"]
                
                # Draw with pen style effects
                if current_pen["style"] == "brush":
                    # Brush style - add circles for smoother look
                    cv2.line(paintWindow, stroke_points[k - 1], stroke_points[k], colors[color_idx], thickness)
                    cv2.circle(paintWindow, stroke_points[k], thickness//2, colors[color_idx], -1)
                elif current_pen["style"] == "marker":
                    # Marker style - slightly transparent effect
                    cv2.line(paintWindow, stroke_points[k - 1], stroke_points[k], colors[color_idx], thickness)
                else:
                    # Fine pen style - clean lines
                    cv2.line(paintWindow, stroke_points[k - 1], stroke_points[k], colors[color_idx], thickness)

    # Draw eraser effect - only when actively erasing (not from stored points)
    # This prevents continuous erasing that blocks new drawing
    if result.multi_hand_landmarks:
        for handslms in result.multi_hand_landmarks:
            landmarks = []
            for lm in handslms.landmark:
                lmx = int(lm.x * 640)
                lmy = int(lm.y * 480)
                landmarks.append([lmx, lmy])
            
            # Check if currently in eraser mode
            pinky_extended = (landmarks[20][1] < landmarks[18][1] - 10) and (landmarks[20][1] < landmarks[16][1])
            
            if pinky_extended:
                # Only erase when pinky is currently extended
                center_x, center_y = landmarks[20][0], landmarks[20][1]
                radius = 20
                
                # Show eraser feedback on camera
                cv2.circle(frame, (center_x, center_y), radius, (0, 0, 255), 2)
                cv2.putText(frame, "ERASING", (center_x - 30, center_y - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Debug: Show coordinates
                cv2.putText(frame, f"Cam: {center_x},{center_y}", (10, 450), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                
                # Map coordinates to paint window (only erase in drawing area)
                if center_y > 100:  # Below control panel
                    # Scale coordinates from camera (640x480) to resized frame (636x471)
                    scale_x = 636 / 640
                    scale_y = 471 / 480
                    
                    # Scale and adjust coordinates
                    paint_x = int(center_x * scale_x)
                    paint_y = int((center_y - 100) * scale_y)  # Adjust for control panel and scale
                    
                    # Debug: Show paint coordinates
                    cv2.putText(frame, f"Paint: {paint_x},{paint_y}", (10, 470), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                    
                    # Ensure coordinates are within bounds
                    if 0 <= paint_x < 636 and 0 <= paint_y < 471:
                        # Show that we're erasing
                        cv2.putText(frame, "ERASING ACTIVE!", (200, 450), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        # Clear stored points in eraser area and update drawing order
                        points_to_remove = []
                        for idx, (color_idx, stroke_idx, stroke_time) in enumerate(drawing_order):
                            if color_idx < len([bpoints, gpoints, rpoints, ypoints, ppoints, opoints]) and stroke_idx < len([bpoints, gpoints, rpoints, ypoints, ppoints, opoints][color_idx]):
                                deque_points = [bpoints, gpoints, rpoints, ypoints, ppoints, opoints][color_idx][stroke_idx]
                                
                                # Create new deque without points in eraser area
                                points_to_keep = deque(maxlen=deque_points.maxlen)
                                for point in deque_points:
                                    if point is not None:
                                        px, py = point
                                        distance = ((px - paint_x) ** 2 + (py - paint_y) ** 2) ** 0.5
                                        if distance > radius:  # Keep points outside eraser area
                                            points_to_keep.append(point)
                                
                                # If no points left in this stroke, mark for removal from drawing order
                                if len(points_to_keep) == 0:
                                    points_to_remove.append(idx)
                                else:
                                    deque_points.clear()
                                    deque_points.extend(points_to_keep)
                        
                        # Remove empty strokes from drawing order (in reverse to maintain indices)
                        for idx in reversed(points_to_remove):
                            drawing_order.pop(idx)
                        
                        # Also restore gradient background
                        for y in range(max(0, paint_y - radius), min(471, paint_y + radius + 1)):
                            for x in range(max(0, paint_x - radius), min(636, paint_x + radius + 1)):
                                distance = ((x - paint_x) ** 2 + (y - paint_y) ** 2) ** 0.5
                                if distance <= radius:
                                    gradient_value = int(25 + (15 * y / 471))
                                    paintWindow[y, x] = [gradient_value, gradient_value, gradient_value]

    # Combine frames into one display
    combined_frame = np.zeros((480, 1272, 3), dtype=np.uint8)
    frame_resized = cv2.resize(frame, (636, 471))

    # Apply modern dark background to combined frame
    combined_frame[:, :] = [30, 30, 30]  # Dark background

    # Then assign the resized frame to combined_frame
    combined_frame[:471, :636] = frame_resized
    combined_frame[:471, 636:] = paintWindow
    
    # Add modern window title and info
    cv2.putText(combined_frame, "Modern Hand Tracking Paint Studio", (380, 485), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Add current tool info
    current_pen = pen_types[pen_type_index]
    tool_info = f"Tool: {current_pen['name']} | Thickness: {current_pen['thickness']}px"
    cv2.putText(combined_frame, tool_info, (380, 505), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    
    cv2.imshow("Modern Paint Studio", combined_frame)

    # Check for 'q' key press to stop
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources and close windows
cap.release()
cv2.destroyAllWindows()