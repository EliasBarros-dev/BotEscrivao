"""
Stub module for audioop to support Python 3.13+ where audioop was removed from stdlib.
This is a minimal implementation sufficient for discord.py to import.
"""

def mul(fragment, width, factor):
    """Multiply audio samples by a factor."""
    return fragment

def add(fragment1, fragment2, width):
    """Add audio fragments."""
    return fragment1 + fragment2

def bias(fragment, width, bias):
    """Apply bias to audio samples."""
    return fragment

def reverse(fragment, width):
    """Reverse audio fragment."""
    return fragment[::-1]

def tomono(fragment, width, lfactor, rfactor):
    """Convert stereo to mono."""
    return fragment

def tostring(fragment):
    """Convert audio to string."""
    return fragment

def fromstring(data, width, nchannels):
    """Convert string to audio."""
    return data

def getsample(fragment, width, index):
    """Get a sample from audio fragment."""
    return 0

def avgpp(data, width):
    """Get average power of audio."""
    return 0

def maxpp(data, width):
    """Get maximum power of audio."""
    return 0

def avg(data, width):
    """Get average of audio."""
    return 0

def max(data, width):
    """Get maximum of audio."""
    return 0

def rms(data, width):
    """Get RMS of audio."""
    return 0

def findfit(data, stamp):
    """Find fit."""
    return 0, 0

def findmax(data, length):
    """Find maximum."""
    return 0

def findfactor(data, stamp):
    """Find factor."""
    return 0, 0

def cross(data, length):
    """Find cross."""
    return 0

def minmax(data, length):
    """Find min/max."""
    return 0, 0

