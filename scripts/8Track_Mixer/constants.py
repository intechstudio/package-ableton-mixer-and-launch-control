"""
Grid Mixer and Launch Control - Constants
Configuration values, MIDI mappings, and timing
"""

# Grid configuration
GRID_ROWS = 4  # scenes
GRID_COLS = 8  # tracks

# Mixer configuration
NUM_TRACKS = 8

# MIDI channels
MAIN_CHANNEL = 0
RED_CHANNEL = 1
GREEN_CHANNEL = 2
BLUE_CHANNEL = 3
TRIGGER_CHANNEL = 0
CLIP_LAUNCH_CHANNEL = 4  # Clip launch buttons on channel 5 (0-indexed, so 4 = MIDI Ch 5)

# Clip launch notes - 2 separate 4×4 modules
# Module 1: Note 60-75 (col 0-3)
# Module 2: Note 76-91 (col 4-7)
CLIP_NOTE_START = 60  # First module starts at Note 60

# Mixer CCs - Module 1 (Tracks 0-3)
VOLUME_CC_START = 44
PAN_CC_START = 40
SEND_A_CC_START = 32
SEND_B_CC_START = 36

# Mixer buttons - Module 1 (Tracks 0-3)
MUTE_NOTE_START = 32
SOLO_NOTE_START = 36
ARM_NOTE_START = 40

# Mixer CCs - Module 2 (Tracks 4-7)
VOLUME_CC_START_2 = 60
PAN_CC_START_2 = 56
SEND_A_CC_START_2 = 48
SEND_B_CC_START_2 = 52

# Mixer buttons - Module 2 (Tracks 4-7)
MUTE_NOTE_START_2 = 48
SOLO_NOTE_START_2 = 52
ARM_NOTE_START_2 = 56

# Color CCs - 2 separate 4×4 modules (32 clips total)
# Module 1: CC 60-75 (col 0-3)
# Module 2: CC 76-91 (col 4-7)
COLOR_CC_START = 60  # First module starts at CC 60

# Navigation buttons
TRACK_LEFT_NOTE = 44      # 1 track left
TRACK_RIGHT_NOTE = 45     # 1 track right
SCENE_UP_NOTE = 46        # Scene up (clips fel)
SCENE_DOWN_NOTE = 47      # Scene down (clips le)
BANK_LEFT_NOTE = 60       # 4 tracks left (Channel 0)
BANK_RIGHT_NOTE = 61      # 4 tracks right (Channel 0)

# Trigger CC
TRIGGER_CC = 127

# LED values
LED_OFF = 0
LED_STOPPED = 1
LED_PLAYING = 127
LED_RECORDING = 120

# Timing
INIT_DELAY = 20