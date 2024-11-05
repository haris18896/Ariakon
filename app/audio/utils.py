import os
import numpy as np
import logging
from pydub import AudioSegment
from scipy.signal import find_peaks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_speed_to_mph(speed, unit):
    if unit == "inches":
        return speed * 0.0000157828283 * 3600
    elif unit == "meters":
        return speed * 0.000621371 * 3600
    elif unit == "centimeters":
        return speed * 0.00000621371 * 3600
    return speed


import os
import numpy as np
from pydub import AudioSegment
from scipy.signal import find_peaks

def calculate_speed_of_sound(distance, audio_file_path, unit="inches"):
    unit_conversion = {
        "inches": 0.0254,      # 1 inch = 0.0254 meters
        "meters": 1,           # 1 meter = 1 meter
        "centimeters": 0.01,   # 1 centimeter = 0.01 meters
    }
    # Convert the distance to meters
    distance_in_meters = distance * unit_conversion.get(unit, 1)

    if not os.path.exists(audio_file_path):
        return "Audio file not found", [], "m/s"

    try:
        # Load audio with pydub
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
    except Exception as e:
        return f"Error loading audio: {e}", [], "m/s"

    # Normalize audio data and set a threshold for peak detection
    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)

    if len(hits) > 1:
        # Calculate time difference between peaks
        time_difference = (hits[1] - hits[0]) / audio.frame_rate  # time in seconds
        speed_in_meters_per_second = distance_in_meters / time_difference

        # Convert speed to miles per hour (1 m/s ≈ 2.23694 MPH)
        speed_in_mph = speed_in_meters_per_second * 2.23694

        return (
            speed_in_meters_per_second,
            "m/s",
            speed_in_mph,
            "MPH",
            hits.tolist(),
        )

    return "Not enough hits detected", [], "m/s"

