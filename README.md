# NeuralPilot

An AI-powered application that uses computer vision and hand gesture recognition to transform your hand movements into virtual controls. Using advanced machine learning models, it tracks your hand positions in real-time to create an intuitive virtual steering interface, converting natural gestures into keyboard commands.

## Requirements

- Python 3.10 or higher
- macOS (uses Quartz for key simulation)
- Webcam

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd NeuralPilot
```

2. Create and activate the AI vision environment:
```bash
python -m venv ai_vision_env
source ai_vision_env/bin/activate  # On macOS/Linux
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Activate the AI vision environment if not already activated:
```bash
source ai_vision_env/bin/activate  # On macOS/Linux
```

2. Launch the Neural Pilot:
```bash
python neural_pilot.py
```

3. Control Instructions:
- Use both hands to create a virtual steering interface
- The AI tracks the angle between your hands to determine steering direction
- Single hand gesture activates reverse mode
- No hands detected puts the system in neutral

## Core Components

- `neural_pilot.py`: Core AI vision system for hand tracking and gesture interpretation
- `ai_controller.py`: Intelligent input simulation system for macOS
- `requirements.txt`: Neural network and vision dependencies

## Note

This AI-powered application is optimized for macOS and utilizes the Quartz framework for control simulation. Adaptation required for other operating systems.