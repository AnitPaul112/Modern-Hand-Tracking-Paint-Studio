# Modern Hand Tracking Paint Studio

A sophisticated real-time hand tracking paint application built with OpenCV and MediaPipe. Create digital art using only your hands - no mouse or stylus required!

## Features

### ✨ Hand Gesture Controls
- **Drawing**: Use your index finger to paint
- **Erasing**: Extend your pinky finger to erase content
- **Brush Selection**: Touch buttons with your finger to switch tools
- **Color Selection**: Touch color buttons to change drawing colors

### 🎨 Drawing Tools
- **Fine Pen**: 2px thickness for precise drawing
- **Marker**: 8px thickness for medium strokes
- **Brush**: 15px thickness for bold artistic strokes

### 🌈 Color Palette
- Orange Red (255, 87, 51)
- Green (46, 204, 113)
- Blue (52, 152, 219)
- Yellow (241, 196, 15)
- Purple (155, 89, 182)
- Orange (230, 126, 34)

### 🎯 Advanced Features
- **Real-time Hand Tracking**: Powered by MediaPipe
- **Chronological Drawing Order**: Maintains proper layer ordering
- **Modern UI**: Dark gradient theme with intuitive controls
- **Live Canvas**: Split-screen view with camera feed and drawing canvas
- **Smart Erasing**: Intelligent point-based erasing system
- **Visual Feedback**: Real-time indicators for active tools

## Requirements

```bash
pip install opencv-python
pip install mediapipe
pip install numpy
```

## Installation & Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd mediapipe
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. **Run the application**
   ```bash
   python board.py
   ```

## How to Use

### Getting Started
1. **Position your hand** in front of the camera
2. **Calibrate** by ensuring your hand is clearly visible
3. **Start drawing** by pointing with your index finger

### Drawing Controls
- **Select Pen Type**: Touch the pen buttons (FINE, MARKER, BRUSH) in the top row
- **Choose Colors**: Touch the colored squares in the bottom row
- **Clear Canvas**: Touch the red "CLEAR" button
- **Exit**: Press 'Q' key to quit

### Hand Gestures
- **Draw**: Point with index finger in the drawing area
- **Erase**: Extend your pinky finger and move over content to erase
- **Select Tools**: Touch interface buttons with your index finger
- **New Stroke**: Bring thumb close to index finger, then separate

### Interface Layout
```
┌─────────────────────────────────────────────────────────┐
│ Camera Feed (640x480)     │ Drawing Canvas (636x471)    │
│ ┌─────────────────────┐   │ ┌─────────────────────────┐ │
│ │ PEN: [FINE][MARKER] │   │ │                         │ │
│ │      [BRUSH]        │   │ │    Your Artwork Here    │ │
│ │ COLORS: ●●●●●●      │   │ │                         │ │
│ │               [CLEAR]│   │ │                         │ │
│ │                     │   │ │                         │ │
│ │   Hand tracking     │   │ │   Dark gradient         │ │
│ │   visualization     │   │ │   background            │ │
│ └─────────────────────┘   │ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Technical Details

### Architecture
- **Hand Detection**: MediaPipe Hands solution
- **Drawing Engine**: OpenCV with custom point management
- **UI Framework**: OpenCV drawing functions with modern styling
- **Coordinate Mapping**: Automatic scaling between camera and canvas

### Key Components
- **Point Management**: Deque-based storage for each color/stroke
- **Drawing Order**: Chronological tracking for proper layering
- **Eraser System**: Real-time point removal with radius detection
- **Pen Styles**: Multiple thickness and style options

### Performance Optimizations
- **Efficient Point Storage**: Limited deque sizes prevent memory issues
- **Smart Redrawing**: Only redraws when necessary
- **Coordinate Scaling**: Optimized mapping between camera and canvas
- **Background Processing**: Separate gradient generation

## Troubleshooting

### Common Issues

**Camera not detected:**
- Ensure your webcam is properly connected
- Check if other applications are using the camera
- Try changing the camera index in `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

**Hand tracking not working:**
- Ensure good lighting conditions
- Keep your hand within the camera frame
- Avoid busy backgrounds that might interfere with detection
- Make sure your hand is clearly visible and not occluded

**Drawing not responsive:**
- Check that your index finger is clearly extended
- Ensure you're pointing in the drawing area (below the control panel)
- Verify the hand landmarks are being detected (yellow circles should be visible)

**Eraser not working:**
- Make sure your pinky finger is clearly extended above other fingers
- The eraser only works in the drawing area
- Look for the red circle indicator when erasing is active

### Performance Tips
- **Lighting**: Use consistent, bright lighting for better hand detection
- **Background**: Use a plain background for optimal tracking
- **Distance**: Maintain 1-2 feet distance from the camera
- **Hand Position**: Keep your hand parallel to the camera for best results

## Customization

### Adding New Colors
```python
colors = [(255, 87, 51), (46, 204, 113), (52, 152, 219), 
          (241, 196, 15), (155, 89, 182), (230, 126, 34)]
# Add your RGB color tuple to the list
```

### Adjusting Pen Thickness
```python
pen_types = [
    {"name": "FINE", "thickness": 2, "style": "fine"},
    {"name": "MARKER", "thickness": 8, "style": "marker"},
    {"name": "BRUSH", "thickness": 15, "style": "brush"}
]
# Modify thickness values as needed
```

### Changing Canvas Size
```python
paintWindow = np.zeros((471, 636, 3), dtype=np.uint8)
# Adjust height and width values
```

## Contributing

Feel free to contribute to this project by:
- Adding new drawing tools or effects
- Improving hand gesture recognition
- Enhancing the user interface
- Optimizing performance
- Adding new features like shape detection or save functionality

## License

This project is open source and available under the MIT License.

## Credits

- **MediaPipe**: Google's MediaPipe for hand tracking
- **OpenCV**: Computer vision and image processing
- **NumPy**: Numerical computing support

---

**Made with ❤️ using Python, OpenCV, and MediaPipe**

*Experience the future of digital art with gesture-based painting!*
