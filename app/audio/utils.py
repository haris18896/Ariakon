import os
import numpy as np
import logging
from pydub import AudioSegment
from scipy.signal import find_peaks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_speed_to_mph(speed, unit):
    """Convert speed from m/s to mph based on the distance unit."""
    if unit == "inches":
        # 1 m/s = 0.0000157828283 miles; therefore for inches:
        return speed * 0.0000157828283 * 3600
    elif unit == "meters":
        # 1 m/s = 0.000621371 miles; therefore for meters:
        return speed * 0.000621371 * 3600
    elif unit == "centimeters":
        # 1 m/s = 0.00000621371 miles; therefore for centimeters:
        return speed * 0.00000621371 * 3600
    return speed  # Return the original speed if unit is unknown

def calculate_speed_of_sound(distance, audio_file_path, unit="inches"):
    unit_conversion = {
        "inches": 1,  # Base unit
        "meters": 39.3701,  # 1 meter = 39.3701 inches
        "centimeters": 0.393701  # 1 cm = 0.393701 inches
    }
    distance_in_inches = distance * unit_conversion[unit]

    if not os.path.exists(audio_file_path):
        # logger.error(f"Audio file not found: {audio_file_path}")
        return "Audio file not found", [], unit + "/sec"

    try:
        # Load audio with pydub
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
        # logger.info(f"Loaded audio data with shape: {audio_data.shape}")
    except Exception as e:
        # logger.error(f"Error loading audio file with pydub: {e}")
        return "Error loading audio", [], unit + "/sec"

    # Normalize audio data and set a threshold for peak detection
    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)
    # logger.info(f"Number of hits detected: {len(hits)}")

    if len(hits) > 1:
        # Calculate time difference between peaks
        time_difference = (hits[1] - hits[0]) / audio.frame_rate  # time in seconds
        speed_in_inches_per_second = distance_in_inches / time_difference
        speed = speed_in_inches_per_second / unit_conversion[unit]
        speed_unit = unit + "/sec"  # e.g., meters/sec, centimeters/sec

        # logger.info(
        #     f"distance: {distance_in_inches}, time_difference: {time_difference}, "
        #     f"Speed of sound: {speed}, unit: {speed_unit}, hits: {hits}"
        # )
        return speed, speed_unit, hits.tolist()  # Return speed as a number and unit separately


    return "Not enough hits detected", [], unit + "/sec"


