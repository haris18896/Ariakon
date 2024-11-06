import os
import logging
import numpy as np
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


def calculate_speed_of_sound(distance, audio_file_path, unit="inches"):
    unit_conversion = {
        "inches": 0.0254,
        "meters": 1,
        "centimeters": 0.01,
    }
    distance_in_meters = distance * unit_conversion.get(unit, 1)

    if not os.path.exists(audio_file_path):
        return "Audio file not found", [], "m/s"

    try:
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
    except Exception as e:
        return f"Error loading audio: {e}", [], "m/s"

    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)
    amplitude_formatted = [{"value": int(val)} for val in amplitude[amplitude >= 15000]]
    hits_formatted = [{"value": int(val)} for val in hits]

    if len(hits) > 1:
        time_difference = (hits[1] - hits[0]) / audio.frame_rate
        speed_in_meters_per_second = distance_in_meters / time_difference
        speed_in_mph = speed_in_meters_per_second * 2.23694

        return (
            speed_in_meters_per_second,
            "m/s",
            speed_in_mph,
            "MPH",
            hits_formatted,
            amplitude_formatted,
        )

    return "Not enough hits detected", [], "m/s"
