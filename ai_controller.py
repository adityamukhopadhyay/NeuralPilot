import Quartz
import time

# Define key mappings (using carbon key codes for Mac)
KEYS = {
    "w": 0x0D,   # kVK_ANSI_W
    "a": 0x00,   # kVK_ANSI_A
    "s": 0x01,   # kVK_ANSI_S
    "d": 0x02,   # kVK_ANSI_D
}

class KeyController:
    @staticmethod
    def press_key(key):
        """
        Simulate a key press on Mac using Quartz EventServices
        
        :param key: String representing the key to press (e.g., 'w', 'a', 's', 'd')
        """
        try:
            key_code = KEYS.get(key.lower())
            if key_code is None:
                print(f"Invalid key: {key}")
                return
            
            event_source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateCombinedSessionState)
            event_down = Quartz.CGEventCreateKeyboardEvent(event_source, key_code, True)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_down)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")

    @staticmethod
    def release_key(key):
        """
        Simulate a key release on Mac using Quartz EventServices
        
        :param key: String representing the key to release (e.g., 'w', 'a', 's', 'd')
        """
        try:
            key_code = KEYS.get(key.lower())
            if key_code is None:
                print(f"Invalid key: {key}")
                return
            
            event_source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateCombinedSessionState)
            event_up = Quartz.CGEventCreateKeyboardEvent(event_source, key_code, False)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event_up)
        except Exception as e:
            print(f"Error releasing key {key}: {e}")

    @staticmethod
    def press_and_release_key(key, duration=0.1):
        """
        Simulate a complete key press and release
        
        :param key: String representing the key to press
        :param duration: Time to hold the key down (default 0.1 seconds)
        """
        KeyController.press_key(key)
        time.sleep(duration)
        KeyController.release_key(key)