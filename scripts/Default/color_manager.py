"""
Grid Mixer and Launch Control - Color Manager Component
SIMPLE VERSION - Batch updates only
"""
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.SliderElement import SliderElement
from .constants import RED_CHANNEL, GREEN_CHANNEL, BLUE_CHANNEL, COLOR_CC_START, GRID_ROWS, GRID_COLS


class ColorManager:
    """Manages RGB color controls for the clip grid"""
    
    def __init__(self, parent):
        self._parent = parent
        self._color_controls_r = []
        self._color_controls_g = []
        self._color_controls_b = []
        self._setup_color_controls()
    
    def _setup_color_controls(self):
        """
        RGB colors on 3 channels - 2 separate 4×4 modules:
        Module 1: CC 60-75 (4×4 = 16 CCs)
        Module 2: CC 76-91 (4×4 = 16 CCs)
        """
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                # Module 1 (col 0-3): CC 60-75
                # Module 2 (col 4-7): CC 76-91
                if col < 4:
                    # Module 1: 4×4 grid starting at CC 60
                    cc_num = COLOR_CC_START + row * 4 + col
                else:
                    # Module 2: 4×4 grid starting at CC 76
                    cc_num = 76 + row * 4 + (col - 4)
                
                # Red channel
                red_control = SliderElement(MIDI_CC_TYPE, RED_CHANNEL, cc_num)
                self._color_controls_r.append(red_control)
                
                # Green channel
                green_control = SliderElement(MIDI_CC_TYPE, GREEN_CHANNEL, cc_num)
                self._color_controls_g.append(green_control)
                
                # Blue channel
                blue_control = SliderElement(MIDI_CC_TYPE, BLUE_CHANNEL, cc_num)
                self._color_controls_b.append(blue_control)
    
    def send_clip_colors(self, track_offset):
        """
        Send RGB colors for ALL visible clips - uses scene_offset for vertical position
        Ch2 (176): Red
        Ch3 (177): Green
        Ch4 (178): Blue
        """
        tracks = self._parent.song().tracks
        scene_offset = self._parent.scene_offset  # ✅ USE SCENE OFFSET!
        
        for col in range(GRID_COLS):
            track_idx = track_offset + col
            
            for row in range(GRID_ROWS):
                control_idx = row * GRID_COLS + col
                scene_idx = scene_offset + row  # ✅ ABSOLUTE SCENE INDEX!
                
                if control_idx >= len(self._color_controls_r):
                    continue
                
                r_value = 0
                g_value = 0
                b_value = 0
                
                if track_idx < len(tracks):
                    track = tracks[track_idx]
                    
                    if scene_idx < len(track.clip_slots):  # ✅ USE scene_idx!
                        clip_slot = track.clip_slots[scene_idx]
                        
                        if clip_slot.has_clip:
                            clip = clip_slot.clip
                            
                            try:
                                # Raw RGB color value
                                rgb_color = int(clip.color)
                                
                                # Extract R, G, B channels via bit shifting
                                r_value = (rgb_color >> 16) & 0xFF
                                g_value = (rgb_color >> 8) & 0xFF
                                b_value = rgb_color & 0xFF
                                
                            except:
                                pass
                
                # Send on 3 separate channels
                self._color_controls_r[control_idx].send_value(r_value, True)
                self._color_controls_g[control_idx].send_value(g_value, True)
                self._color_controls_b[control_idx].send_value(b_value, True)