import os
import logging
import numpy as np
from pydub import AudioSegment
from scipy.signal import find_peaks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_speed_to_mph(speed, unit):
    """
    Convert speed from different units to miles per hour (MPH).
    
    Args:
        speed (float): Speed value to convert
        unit (str): Unit of measurement ('inches', 'meters', or 'centimeters')
    
    Returns:
        float: Speed in MPH
    """
    if unit == "inches":
        return speed * 0.0000157828283 * 3600
    elif unit == "meters":
        return speed * 0.000621371 * 3600
    elif unit == "centimeters":
        return speed * 0.00000621371 * 3600
    return speed


def calculate_speed_of_sound(distance, audio_file_path, unit="inches"):
    """
    Calculate the speed of sound based on audio file analysis.
    
    Args:
        distance (float): Distance value
        audio_file_path (str): Path to the audio file
        unit (str): Unit of measurement (default: 'inches')
    
    Returns:
        tuple: (speed_in_meters_per_second, speed_unit, speed_in_mph, mph_unit, hits_formatted, amplitude_formatted)
    """
    # Unit conversion dictionary
    unit_conversion = {
        "inches": 0.0254,
        "meters": 1,
        "centimeters": 0.01,
    }
    
    # Convert distance to meters
    distance_in_meters = distance * unit_conversion.get(unit, 1)

    # Check if audio file exists
    if not os.path.exists(audio_file_path):
        logger.error(f"Audio file not found: {audio_file_path}")
        return 0, "m/s", 0, "MPH", [], []

    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        audio_data = np.array(audio.get_array_of_samples())
        
        # Calculate amplitude
        amplitude = np.abs(audio_data)
        threshold = np.percentile(amplitude, 95)
        
        # Find peaks in the audio signal
        hits, _ = find_peaks(amplitude, height=threshold, distance=5000)
        
        # Format amplitude and hits data
        amplitude_formatted = [
            {"value": int(val)} 
            for val in amplitude[amplitude >= 15000]
        ]
        hits_formatted = [{"value": int(val)} for val in hits]

        # Calculate speed if we have at least two peaks
        if len(hits) > 1:
            # Calculate time difference between first two peaks
            time_difference = (hits[1] - hits[0]) / audio.frame_rate
            
            # Calculate speeds
            speed_in_meters_per_second = distance_in_meters / time_difference
            speed_in_mph = speed_in_meters_per_second * 2.23694

            return (
                round(speed_in_meters_per_second, 2),
                "m/s",
                round(speed_in_mph, 2),
                "MPH",
                hits_formatted,
                amplitude_formatted,
            )
        else:
            logger.warning(f"Not enough peaks detected in audio file: {audio_file_path}")
            return 0, "m/s", 0, "MPH", hits_formatted, amplitude_formatted

    except Exception as e:
        logger.error(f"Error processing audio file {audio_file_path}: {str(e)}")
        return 0, "m/s", 0, "MPH", [], []
