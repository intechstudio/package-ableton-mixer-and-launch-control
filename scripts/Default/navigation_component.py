"""
Grid Mixer and Launch Control - Navigation Component
Track navigation (left/right) + Scene navigation (up/down) + Optional Bank navigation
"""
from _Framework.InputControlElement import MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from .constants import (TRACK_LEFT_NOTE, TRACK_RIGHT_NOTE, SCENE_UP_NOTE, SCENE_DOWN_NOTE,
                        BANK_LEFT_NOTE, BANK_RIGHT_NOTE)


class NavigationComponent:
    """Handles track (horizontal), scene (vertical), and optional bank navigation"""
    
    def __init__(self, parent, mixer, clip_launcher, color_manager):
        self._parent = parent
        self._mixer = mixer
        self._clip_launcher = clip_launcher
        self._color_manager = color_manager
        self._setup_navigation_buttons()
    
    def _setup_navigation_buttons(self):
        """Setup track, scene, and optional bank navigation buttons"""
        # Track navigation (horizontal) - REQUIRED
        self._track_left_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, TRACK_LEFT_NOTE)
        self._track_right_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, TRACK_RIGHT_NOTE)
        
        # Scene navigation (vertical) - REQUIRED
        self._scene_up_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, SCENE_UP_NOTE)
        self._scene_down_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, SCENE_DOWN_NOTE)
        
        # Bank navigation (4 track jump) - OPTIONAL (only if not -1)
        self._bank_left_button = None
        self._bank_right_button = None
        if BANK_LEFT_NOTE >= 0:
            self._bank_left_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, BANK_LEFT_NOTE)
            self._bank_left_button.add_value_listener(lambda v: v > 0 and self._move_track(-8))
        
        if BANK_RIGHT_NOTE >= 0:
            self._bank_right_button = ButtonElement(True, MIDI_NOTE_TYPE, 0, BANK_RIGHT_NOTE)
            self._bank_right_button.add_value_listener(lambda v: v > 0 and self._move_track(8))
        
        # Connect listeners for required navigation
        self._track_left_button.add_value_listener(lambda v: v > 0 and self._move_track(-1))
        self._track_right_button.add_value_listener(lambda v: v > 0 and self._move_track(1))
        self._scene_up_button.add_value_listener(lambda v: v > 0 and self._move_scene(-1))
        self._scene_down_button.add_value_listener(lambda v: v > 0 and self._move_scene(1))
    
    def _move_track(self, offset):
        """Move track offset (horizontal navigation)"""
        num_tracks = len(self._parent.song().tracks)
        new_offset = max(0, min(num_tracks - 4, self._parent.track_offset + offset))
        
        if new_offset == self._parent.track_offset:
            return  # No change
        
        self._parent.track_offset = new_offset
        
        # Update session highlighting
        self._parent.session.set_offsets(new_offset, self._parent.scene_offset)
        
        # Update mixer
        self._mixer.set_track_offset(new_offset)
        self._mixer.update_mix_leds()
        
        # Update clip grid
        self._clip_launcher.setup_clip_listeners()
        self._color_manager.send_clip_colors(new_offset)
        self._clip_launcher.update_clip_leds()
    
    def _move_scene(self, offset):
        """Move scene offset (vertical navigation)"""
        num_scenes = len(self._parent.song().scenes)
        new_offset = max(0, min(num_scenes - 4, self._parent.scene_offset + offset))
        
        if new_offset == self._parent.scene_offset:
            return  # No change
        
        self._parent.scene_offset = new_offset
        
        # Update session highlighting
        self._parent.session.set_offsets(self._parent.track_offset, new_offset)
        
        # Update clip grid
        self._clip_launcher.setup_clip_listeners()
        self._color_manager.send_clip_colors(self._parent.track_offset)
        self._clip_launcher.update_clip_leds()