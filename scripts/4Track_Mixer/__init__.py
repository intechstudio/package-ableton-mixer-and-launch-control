"""
Grid Mixer and Launch Control Surface
8×4 CLIP GRID VERSION - v2.0
"""
from __future__ import absolute_import, print_function, unicode_literals
from _Framework.ControlSurface import ControlSurface
from _Framework.SessionComponent import SessionComponent
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.SliderElement import SliderElement

from .constants import TRIGGER_CC, TRIGGER_CHANNEL, INIT_DELAY, GRID_ROWS, GRID_COLS, NUM_TRACKS
from .clip_launcher import ClipLauncher
from .mixer_component import MixerComponent
from .navigation_component import NavigationComponent


class Grid_mixer_and_launch_control(ControlSurface):
    """Main control surface - 8×4 CLIP GRID"""
    
    def __init__(self, c_instance):
        super(Grid_mixer_and_launch_control, self).__init__(c_instance)
        
        self.track_offset = 0
        self.scene_offset = 0  # Scene offset for vertical clip navigation
        self.session = None
        
        # Components
        self._clip_launcher = None
        self._mixer_component = None
        self._navigation = None
        self._trigger_control = None
        
        with self.component_guard():
            self._setup_session()
        
        self.schedule_message(INIT_DELAY, self._delayed_setup)
        self.show_message("Grid Mixer & Launch Control v2.0 - 8x4 GRID")
        self.log_message("=== 8x4 CLIP GRID VERSION LOADED ===")
    
    def _delayed_setup(self):
        """Setup all components after initialization"""
        with self.component_guard():
            # Create components
            self._clip_launcher = ClipLauncher(self)
            self._mixer_component = MixerComponent(self)
            self._navigation = NavigationComponent(self, self._mixer_component, 
                                                   self._clip_launcher)
            
            # Setup listeners
            self._setup_trigger_listener()
            self._setup_track_list_listener()  # NEW: Watch for track add/delete
            self._clip_launcher.setup_clip_listeners()
            self._mixer_component.setup_track_listeners()
            
            # Update mixer (works immediately)
            self._mixer_component.update_mix_leds()
        
        self.show_message("Grid Mixer & Launch Control ready")
        self.show_message("Navigate: Track L/R (44/45), Scene Up/Down (46/47)")
    
    def _setup_track_list_listener(self):
        """Listen for track add/remove/duplicate"""
        song = self.song()
        if not song.tracks_has_listener(self._on_tracks_changed):
            song.add_tracks_listener(self._on_tracks_changed)
        
        # Also listen for scene changes
        if not song.scenes_has_listener(self._on_scenes_changed):
            song.add_scenes_listener(self._on_scenes_changed)
    
    def _on_tracks_changed(self):
        """Called when tracks are added, deleted, or duplicated"""
        self.log_message("Track list changed - rebuilding listeners")
        
        # Adjust track offset if needed (in case tracks were deleted)
        num_tracks = len(self.song().tracks)
        if self.track_offset > max(0, num_tracks - NUM_TRACKS):
            self.track_offset = max(0, num_tracks - NUM_TRACKS)
        
        # Update session highlighting
        self.session.set_offsets(self.track_offset, self.scene_offset)
        
        # Rebuild all listeners
        self._clip_launcher.setup_clip_listeners()
        self._mixer_component.setup_track_listeners()
        
        # Update MIDI feedback
        self._mixer_component.set_track_offset(self.track_offset)
        self._mixer_component.update_mix_leds()
        self._clip_launcher.update_clip_leds()
    
    def _on_scenes_changed(self):
        """Called when scenes are added or deleted"""
        self.log_message("Scene list changed - rebuilding clip listeners")
        
        # Adjust scene offset if needed (in case scenes were deleted)
        num_scenes = len(self.song().scenes)
        if self.scene_offset > max(0, num_scenes - 4):
            self.scene_offset = max(0, num_scenes - 4)
        
        # Update session highlighting
        self.session.set_offsets(self.track_offset, self.scene_offset)
        
        # Rebuild clip listeners
        self._clip_launcher.setup_clip_listeners()
        
        # Update clip MIDI feedback
        self._clip_launcher.update_clip_leds()
    
    def _setup_session(self):
        self.session = SessionComponent(GRID_COLS, GRID_ROWS)
        self.session.set_offsets(0, 0)
        
        try:
            self.set_highlighting_session_component(self.session)
            self.session.set_highlighting_enabled(True)
            self.log_message("SessionComponent 8×4 ACTIVE - Red box should be 8 wide!")
        except:
            pass
    
    def _setup_trigger_listener(self):
        """Setup trigger CC for full state refresh"""
        self._trigger_control = SliderElement(MIDI_CC_TYPE, TRIGGER_CHANNEL, TRIGGER_CC)
        self._trigger_control.add_value_listener(self._trigger_handler, True)
    
    def _trigger_handler(self, value, sender=None):
        """Handle trigger CC to send full state"""
        if value == 127:
            self._send_full_state()
            self.show_message("Full state sent")
    
    def _send_full_state(self):
        """Send complete state to controller"""
        self._mixer_component.send_full_state()
        self._clip_launcher.update_clip_leds()
    
    def disconnect(self):
        """Cleanup on disconnect"""
        # Remove track/scene list listeners
        song = self.song()
        if song.tracks_has_listener(self._on_tracks_changed):
            song.remove_tracks_listener(self._on_tracks_changed)
        if song.scenes_has_listener(self._on_scenes_changed):
            song.remove_scenes_listener(self._on_scenes_changed)
        
        # Cleanup components
        if self._clip_launcher:
            self._clip_launcher.disconnect()
        if self._mixer_component:
            self._mixer_component.disconnect()
        
        super(Grid_mixer_and_launch_control, self).disconnect()


def create_instance(c_instance):
    """Factory function for Live to create the control surface"""
    return Grid_mixer_and_launch_control(c_instance)