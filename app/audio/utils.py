import os
import numpy as np
import logging
from pydub import AudioSegment
from scipy.signal import find_peaks


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_speed_of_sound(distance, audio_file_path):
    logger.info(f"Distance: {distance}")  # Log to terminal
    logger.info(f"Audio file path: {audio_file_path}")

    if not os.path.exists(audio_file_path):
        logger.error(f"Audio file not found: {audio_file_path}")
        return "Audio file not found", []

    try:
        # Load audio with pydub
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
        logger.info(f"Loaded audio data with shape: {audio_data}")
    except Exception as e:
        logger.error(f"Error loading audio file with pydub: {e}")
        return "Error loading audio", []

    # Normalize audio data
    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)

    logger.info(f"Number of hits detected: {len(hits)}")

    if len(hits) > 1:
        time_difference = (
            hits[1] - hits[0]
        ) / audio.frame_rate  # Use the sample rate of pydub audio
        speed = distance / (time_difference * 60)
        logger.info(f"distance: {distance} time_difference : {time_difference}, Speed of sound: {speed}, hits: {hits}")
        return speed, hits.tolist()  # Returning the speed and peaks as a list

    logger.warning("Not enough hits detected")
    return "Not enough hits detected", []
