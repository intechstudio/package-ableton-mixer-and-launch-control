"""
Grid Mixer and Launch Control - Clip Launcher Component
SIMPLE VERSION - Batch updates only
"""
from _Framework.InputControlElement import MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from .constants import CLIP_NOTE_START, CLIP_LAUNCH_CHANNEL, GRID_ROWS, GRID_COLS, LED_OFF, LED_STOPPED, LED_RECORDING, LED_PLAYING


class ClipLauncher:
    """Manages clip launching and status LEDs"""
    
    def __init__(self, parent, color_manager):
        self._parent = parent
        self._color_manager = color_manager
        self._clip_buttons = []
        self._clip_slot_listeners = []
        self._setup_clip_buttons()
    
    def _setup_clip_buttons(self):
        """Setup button handlers for clip launch on CHANNEL 5 - 2 separate 4×4 modules"""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                # Module 1 (col 0-3): Note 60-75
                # Module 2 (col 4-7): Note 76-91
                if col < 4:
                    # Module 1: 4×4 grid starting at Note 60
                    note = CLIP_NOTE_START + row * 4 + col
                else:
                    # Module 2: 4×4 grid starting at Note 76
                    note = 76 + row * 4 + (col - 4)
                
                # IMPORTANT: Clip launch buttons on Channel 5 (MIDI channel 5)
                btn = ButtonElement(True, MIDI_NOTE_TYPE, CLIP_LAUNCH_CHANNEL, note)
                
                def make_launch_handler(scene_idx, track_col):
                    def handler(value):
                        if value > 0:
                            self._launch_clip(scene_idx, track_col)
                    return handler
                
                btn.add_value_listener(make_launch_handler(row, col))
                self._clip_buttons.append(btn)
    
    def _launch_clip(self, scene_idx, track_col):
        """Launch clip at scene_offset + scene_idx"""
        track_offset = self._parent.track_offset
        scene_offset = self._parent.scene_offset
        track_idx = track_offset + track_col
        scene_idx_abs = scene_offset + scene_idx  # Absolute scene position
        
        if track_idx < len(self._parent.song().tracks):
            track = self._parent.song().tracks[track_idx]
            if scene_idx_abs < len(track.clip_slots):
                clip_slot = track.clip_slots[scene_idx_abs]
                clip_slot.fire()
    
    def update_clip_leds(self):
        """Update ALL clip LEDs - uses scene_offset for vertical position"""
        tracks = self._parent.song().tracks
        track_offset = self._parent.track_offset
        scene_offset = self._parent.scene_offset
        
        for col in range(GRID_COLS):
            track_idx = track_offset + col
            
            for row in range(GRID_ROWS):
                button_idx = row * GRID_COLS + col
                scene_idx = scene_offset + row  # Absolute scene position
                
                if button_idx >= len(self._clip_buttons):
                    continue
                    
                button = self._clip_buttons[button_idx]
                led_value = LED_OFF
                
                if track_idx < len(tracks):
                    track = tracks[track_idx]
                    
                    if scene_idx < len(track.clip_slots):
                        clip_slot = track.clip_slots[scene_idx]
                        
                        if clip_slot.has_clip:
                            clip = clip_slot.clip
                            
                            try:
                                is_rec = False
                                if hasattr(clip, 'is_recording'):
                                    is_rec = clip.is_recording
                                
                                is_play = clip.is_playing
                                
                                if is_rec:
                                    led_value = LED_RECORDING
                                elif is_play:
                                    led_value = LED_PLAYING
                                else:
                                    led_value = LED_STOPPED
                            except:
                                led_value = LED_STOPPED
                
                button.send_value(led_value, True)
    
    def setup_clip_listeners(self):
        """Setup listeners - uses scene_offset for vertical position"""
        self._remove_clip_listeners()
        
        tracks = self._parent.song().tracks
        track_offset = self._parent.track_offset
        scene_offset = self._parent.scene_offset
        
        for col in range(GRID_COLS):
            track_idx = track_offset + col
            
            if track_idx >= len(tracks):
                continue
                
            track = tracks[track_idx]
            
            for row in range(GRID_ROWS):
                scene_idx = scene_offset + row  # Absolute scene position
                
                if scene_idx >= len(track.clip_slots):
                    continue
                    
                clip_slot = track.clip_slots[scene_idx]
                
                # Has clip listener
                def make_has_clip_callback():
                    def callback():
                        self.setup_clip_listeners()
                        self._color_manager.send_clip_colors(self._parent.track_offset)
                        self.update_clip_leds()
                    return callback
                
                has_clip_cb = make_has_clip_callback()
                if not clip_slot.has_clip_has_listener(has_clip_cb):
                    clip_slot.add_has_clip_listener(has_clip_cb)
                    self._clip_slot_listeners.append(('has_clip', clip_slot, has_clip_cb))
                
                if clip_slot.has_clip:
                    clip = clip_slot.clip
                    
                    # Playing status listener
                    def make_playing_callback():
                        return lambda: self.update_clip_leds()
                    
                    playing_cb = make_playing_callback()
                    if not clip.playing_status_has_listener(playing_cb):
                        clip.add_playing_status_listener(playing_cb)
                        self._clip_slot_listeners.append(('playing', clip, playing_cb))
                    
                    # Color listener
                    def make_color_callback():
                        return lambda: self._color_manager.send_clip_colors(self._parent.track_offset)
                    
                    color_cb = make_color_callback()
                    if not clip.color_has_listener(color_cb):
                        clip.add_color_listener(color_cb)
                        self._clip_slot_listeners.append(('color', clip, color_cb))
    
    def _remove_clip_listeners(self):
        """Remove all clip listeners"""
        for listener_info in self._clip_slot_listeners:
            try:
                listener_type, obj, cb = listener_info
                
                if listener_type == 'has_clip':
                    if obj.has_clip_has_listener(cb):
                        obj.remove_has_clip_listener(cb)
                elif listener_type == 'playing':
                    if obj.playing_status_has_listener(cb):
                        obj.remove_playing_status_listener(cb)
                elif listener_type == 'color':
                    if obj.color_has_listener(cb):
                        obj.remove_color_listener(cb)
            except:
                pass
        
        self._clip_slot_listeners = []
    
    def disconnect(self):
        """Cleanup on disconnect"""
        self._remove_clip_listeners()