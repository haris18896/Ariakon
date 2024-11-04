import os
import numpy as np
import logging
from pydub import AudioSegment
from scipy.signal import find_peaks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_speed_of_sound(distance, audio_file_path, unit="inches"):
    logger.info(f"Distance: {distance}")  # Log to terminal
    logger.info(f"Audio file path: {audio_file_path}")

    # Conversion factors to inches
    unit_conversion = {
        "inches": 1,  # Base unit
        "meters": 39.3701,  # 1 meter = 39.3701 inches
        "centimeters": 0.393701,  # 1 cm = 0.393701 inches
    }
    distance_in_inches = distance * unit_conversion[unit]

    if not os.path.exists(audio_file_path):
        logger.error(f"Audio file not found: {audio_file_path}")
        return "Audio file not found", [], unit

    try:
        # Load audio with pydub
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
        logger.info(f"Loaded audio data with shape: {audio_data.shape}")
    except Exception as e:
        logger.error(f"Error loading audio file with pydub: {e}")
        return "Error loading audio", [], unit

    # Normalize audio data and set a threshold for peak detection
    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)

    logger.info(f"Number of hits detected: {len(hits)}")

    if len(hits) > 1:
        # Calculate time difference between peaks
        time_difference = (hits[1] - hits[0]) / audio.frame_rate  # seconds
        # Speed calculation, distance in inches, time in seconds
        speed_in_inches_per_minute = distance_in_inches / time_difference
        speed = (
            speed_in_inches_per_minute / unit_conversion[unit]
        )  # Convert to requested unit
        logger.info(
            f"distance: {distance_in_inches}, time_difference : {time_difference}, Speed of sound: {speed}, unit: {unit}/min, hits: {hits}"
        )
        return (
            speed,
            unit + "/sec",
            hits.tolist(),
        )  # Return speed as a number and unit separately

    logger.warning("Not enough hits detected")
    return "Not enough hits detected", [], unit
