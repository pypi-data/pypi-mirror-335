import os
import logging

logger = logging.getLogger(__name__)

def get_test_delay():
    """Get delay time based on environment"""
    if os.getenv('TEST_MODE') == 'true':
        base_delay = int(os.getenv('TEST_DELAY', '60'))  # Base delay in seconds
        step_increment = int(os.getenv('TEST_STEP_INCREMENT', '30'))  # Increment between steps
        return {
            'base_delay': base_delay,
            'step_increment': step_increment
        }
    return None
