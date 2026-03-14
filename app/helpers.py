"""
helpers.py

This module contains helper utilities used by the GUI automation layer.
Its primary responsibility is to generate human-like timing values
based on configurable profiles.

The TimeConroller class centralizes all delay, typing speed, and waiting
behavior so that timing logic is:
- Consistent
- Easily configurable
- Reusable across the application
"""


import random

class TimeConroller:
    """
    Timing controller responsible for generating randomized delays
    based on predefined time profiles.

    Each timing method returns a float value that simulates variability
    in human behavior (typing speed, pauses, mouse movement, etc.).

    Attributes:
        profile (dict):
            Dictionary containing base timing values such as:
            - fast
            - normal
            - slow
            - distracted
        e (float or int):
            Error margin applied to timing values to introduce randomness.
    """

    def __init__(self, profile):
        """
        Initialize the time controller with a timing profile and margin.

        Args:
            profile (dict):
                A dictionary containing base timing values.
                Example:
                {
                    "fast": 0.2,
                    "normal": 0.5,
                    "slow": 1.2,
                    "distracted": 2.5
                }
        """
        self.profile = profile
        self.e = random.uniform(0.1, 5.0)

    def fast(self):
        """
        Generate a fast delay value.

        Typically used for quick typing or short pauses.

        Returns:
            float:
                Randomized fast timing value rounded to 3 decimals.
        """
        # Make sure the  lower number is postitve to keep the output positive
        return float(f"{random.uniform(max(self.profile['fast'] - self.e, 0), self.profile['fast'] + self.e):.3f}")
    
    def slow(self):
        """
        Generate a slow delay value.

        Typically used for longer pauses or deliberate waiting.

        Returns:
            float:
                Randomized slow timing value rounded to 3 decimals.
        """
        # Make sure the  lower number is postitve to keep the output positive
        return float(f"{random.uniform(max(self.profile['slow'] - self.e, 0), self.profile['slow']  + self.e):.3f}")
    
    def normal(self):
        """
        Generate a normal (average) delay value.

        Used for most standard interactions such as moderate typing
        or common UI response waits.

        Returns:
            float:
                Randomized normal timing value rounded to 3 decimals.
        """
        # Make sure the  lower number is postitve to keep the output positive
        return float(f"{random.uniform(max(self.profile['normal'] - self.e, 0), self.profile['normal'] + self.e):.3f}") 
       
    def distracted(self):
        """
        Generate a distracted delay value.

        Simulates longer, inconsistent pauses that may occur
        when a user is momentarily distracted.

        Returns:
            float:
                Randomized distracted timing value rounded to 3 decimals.
        """
        # Make sure the  lower number is postitve to keep the output positive
        return float(f"{random.uniform(max(self.profile['distracted'] - self.e, 0), self.profile['distracted'] + self.e):.3f}")

    def mouse_move(self):
        """
        Generate a mouse movement duration.

        This value represents how long the mouse takes to move
        to a target position.

        Returns:
            float:
                Randomized mouse movement duration (0.00-1.00 seconds),
                rounded to 2 decimals.
        """
        return float(f"{random.uniform(0.1, 1):.2f}")
    
    def pick_typing(self):
        """
        Randomly select a typing speed function.

        This method returns a function reference, not a value.
        The caller is expected to execute the returned function.

        Returns:
            callable:
                Either self.fast or self.normal.
        """
        return random.choice([self.fast, self.normal])
    
    def pick_waiting(self):
        """
        Randomly select a waiting behavior function.

        Used when the application needs to pause for UI responses
        or between actions.

        Returns:
            callable:
                One of:
                - self.normal
                - self.slow
                - self.distracted
        """
        return random.choice([self.normal, self.slow, self.distracted])
    
