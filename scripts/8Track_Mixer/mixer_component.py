"""
Grid Mixer and Launch Control - Mixer Component
Handles volume, pan, sends, mute, solo, arm controls
8-TRACK MIXER: 2 modules × 4 tracks
"""
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.MixerComponent import MixerComponent as FrameworkMixer
from .constants import (MAIN_CHANNEL, NUM_TRACKS, GRID_COLS,
                      VOLUME_CC_START, PAN_CC_START, SEND_A_CC_START, SEND_B_CC_START,
                      MUTE_NOTE_START, SOLO_NOTE_START, ARM_NOTE_START,
                      VOLUME_CC_START_2, PAN_CC_START_2, SEND_A_CC_START_2, SEND_B_CC_START_2,
                      MUTE_NOTE_START_2, SOLO_NOTE_START_2, ARM_NOTE_START_2)


class MixerComponent:
    """Manages mixer controls for volume, pan, sends, mute, solo, arm"""
    
    def __init__(self, parent):
        self._parent = parent
        self._mixer = None
        self._vol_sliders = []
        self._pan_sliders = []
        self._sendA = []
        self._sendB = []
        self._mute_buttons = []
        self._solo_buttons = []
        self._arm_buttons = []
        self._listener_refs = []
        self._track_state_listeners = []
        self._last_selected_track = None  # Track debounce
        self._last_selection_time = 0  # Timestamp of last selection
        
        self._setup_mixer()
        self._setup_mix_controls()
        self._setup_control_listeners()
    
    def _setup_mixer(self):
        """Setup framework mixer component for NUM_TRACKS tracks"""
        self._mixer = FrameworkMixer(NUM_TRACKS, 2)  # NUM_TRACKS tracks, 2 sends
        
        # Module 1: Tracks 0-3
        for i in range(min(4, NUM_TRACKS)):
            vol = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, VOLUME_CC_START + i)
            pan = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, PAN_CC_START + i)
            sendA = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, SEND_A_CC_START + i)
            sendB = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, SEND_B_CC_START + i)
            
            self._vol_sliders.append(vol)
            self._pan_sliders.append(pan)
            self._sendA.append(sendA)   
            self._sendB.append(sendB)
            
            strip = self._mixer.channel_strip(i)
            strip.set_volume_control(vol)
            strip.set_pan_control(pan)
            strip.set_send_controls((sendA, sendB))
        
        # Module 2: Tracks 4-7 (only if NUM_TRACKS > 4)
        if NUM_TRACKS > 4:
            for i in range(NUM_TRACKS - 4):
                vol = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, VOLUME_CC_START_2 + i)
                pan = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, PAN_CC_START_2 + i)
                sendA = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, SEND_A_CC_START_2 + i)
                sendB = SliderElement(MIDI_CC_TYPE, MAIN_CHANNEL, SEND_B_CC_START_2 + i)
                
                self._vol_sliders.append(vol)
                self._pan_sliders.append(pan)
                self._sendA.append(sendA)
                self._sendB.append(sendB)
                
                strip = self._mixer.channel_strip(i + 4)
                strip.set_volume_control(vol)
                strip.set_pan_control(pan)
                strip.set_send_controls((sendA, sendB))
    
    def _setup_mix_controls(self):
        """Setup mute, solo, arm buttons for NUM_TRACKS tracks"""
        # Module 1: Tracks 0-3
        for i in range(min(4, NUM_TRACKS)):
            mute = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, MUTE_NOTE_START + i)
            solo = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, SOLO_NOTE_START + i)
            arm = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, ARM_NOTE_START + i)
            
            mute.add_value_listener(lambda v, i=i: v > 0 and self._toggle_track(i, "mute"))
            solo.add_value_listener(lambda v, i=i: v > 0 and self._toggle_track(i, "solo"))
            arm.add_value_listener(lambda v, i=i: v > 0 and self._toggle_track(i, "arm"))
            
            self._mute_buttons.append(mute)
            self._solo_buttons.append(solo)
            self._arm_buttons.append(arm)
        
        # Module 2: Tracks 4-7 (only if NUM_TRACKS > 4)
        if NUM_TRACKS > 4:
            for i in range(NUM_TRACKS - 4):
                mute = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, MUTE_NOTE_START_2 + i)
                solo = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, SOLO_NOTE_START_2 + i)
                arm = ButtonElement(True, MIDI_NOTE_TYPE, MAIN_CHANNEL, ARM_NOTE_START_2 + i)
                
                track_idx = i + 4
                mute.add_value_listener(lambda v, idx=track_idx: v > 0 and self._toggle_track(idx, "mute"))
                solo.add_value_listener(lambda v, idx=track_idx: v > 0 and self._toggle_track(idx, "solo"))
                arm.add_value_listener(lambda v, idx=track_idx: v > 0 and self._toggle_track(idx, "arm"))
                
                self._mute_buttons.append(mute)
                self._solo_buttons.append(solo)
                self._arm_buttons.append(arm)
    
    def _setup_control_listeners(self):
        """Setup listeners on sliders to select tracks"""
        import time
        for i in range(NUM_TRACKS):
            for control in [self._vol_sliders[i], self._pan_sliders[i], self._sendA[i], self._sendB[i]]:
                def make_handler(idx):
                    def handler(v, sender=None):
                        t = self._parent.track_offset + idx
                        if t < len(self._parent.song().tracks):
                            # Only select if 1 second has passed or different track
                            current_time = time.time()
                            if current_time - self._last_selection_time >= 0.4:
                                self._last_selected_track = t
                                self._last_selection_time = current_time
                                self._parent.song().view.selected_track = self._parent.song().tracks[t]
                    return handler
                
                h = make_handler(i)
                control.add_value_listener(h, False)
                self._listener_refs.append((control, h))
    
    def _toggle_track(self, index, attr):
        """Toggle mute/solo/arm on track"""
        idx = self._parent.track_offset + index
        if idx >= len(self._parent.song().tracks):
            return
        
        track = self._parent.song().tracks[idx]
        
        if attr == "mute":
            track.mute = not track.mute
            self._mute_buttons[index].send_value(127 if track.mute else 0, True)
        elif attr == "solo":
            track.solo = not track.solo
            self._solo_buttons[index].send_value(127 if track.solo else 0, True)
        elif attr == "arm" and track.can_be_armed:
            track.arm = not track.arm
            self._arm_buttons[index].send_value(127 if track.arm else 0, True)
    
    def update_mix_leds(self):
        """Update all mix control LEDs for 8 tracks"""
        for i in range(NUM_TRACKS):
            idx = self._parent.track_offset + i
            if idx >= len(self._parent.song().tracks):
                continue
            
            track = self._parent.song().tracks[idx]
            
            self._mute_buttons[i].send_value(127 if track.mute else 0, True)
            self._solo_buttons[i].send_value(127 if track.solo else 0, True)
            
            if track.can_be_armed:
                self._arm_buttons[i].send_value(127 if track.arm else 0, True)
            else:
                self._arm_buttons[i].send_value(0, True)
    
    def set_track_offset(self, offset):
        """Update mixer track offset"""
        self._mixer.set_track_offset(offset)
    
    def send_full_state(self):
        """Send current values of all mixer controls for 8 tracks"""
        for i in range(NUM_TRACKS):
            idx = self._parent.track_offset + i
            if idx >= len(self._parent.song().tracks):
                continue
            
            track = self._parent.song().tracks[idx]
            
            self._vol_sliders[i].send_value(int(track.mixer_device.volume.value * 127), True)
            pan = track.mixer_device.panning.value
            self._pan_sliders[i].send_value(int((pan + 1.0) * 63.5), True)
            
            sends = track.mixer_device.sends
            if len(sends) > 0:
                self._sendA[i].send_value(int(sends[0].value * 127), True)
            if len(sends) > 1:
                self._sendB[i].send_value(int(sends[1].value * 127), True)
        
        self.update_mix_leds()
    
    def setup_track_listeners(self):
        """Setup track listeners for mute/solo/arm changes"""
        for track in self._parent.song().tracks:
            def make_mute_cb():
                return lambda: self.update_mix_leds()
            
            def make_solo_cb():
                return lambda: self.update_mix_leds()
            
            def make_arm_cb():
                return lambda: self.update_mix_leds()
            
            mute_cb = make_mute_cb()
            solo_cb = make_solo_cb()
            arm_cb = make_arm_cb()
            
            if not track.mute_has_listener(mute_cb):
                track.add_mute_listener(mute_cb)
                self._track_state_listeners.append((track, 'mute', mute_cb))
            
            if not track.solo_has_listener(solo_cb):
                track.add_solo_listener(solo_cb)
                self._track_state_listeners.append((track, 'solo', solo_cb))
            
            # Add ARM listener (for audio/MIDI tracks)
            if track.can_be_armed and not track.arm_has_listener(arm_cb):
                track.add_arm_listener(arm_cb)
                self._track_state_listeners.append((track, 'arm', arm_cb))
    
    def disconnect(self):
        """Cleanup on disconnect"""
        for listener_info in self._track_state_listeners:
            try:
                track, listener_type, cb = listener_info
                
                if listener_type == 'mute' and track.mute_has_listener(cb):
                    track.remove_mute_listener(cb)
                elif listener_type == 'solo' and track.solo_has_listener(cb):
                    track.remove_solo_listener(cb)
                elif listener_type == 'arm' and track.arm_has_listener(cb):
                    track.remove_arm_listener(cb)
            except:
                pass