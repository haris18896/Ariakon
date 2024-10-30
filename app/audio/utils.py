import numpy as np
import librosa
from scipy.signal import find_peaks


def calculate_speed_of_sound(distance, audio_file_path):
    audio_data, sr = librosa.load(audio_file_path, sr=None)
    amplitude = np.abs(audio_data)
    threshold = np.percentile(amplitude, 95)
    hits, _ = find_peaks(amplitude, height=threshold, distance=5000)

    if len(hits) > 1:
        time_difference = (hits[1] - hits[0]) / sr
        speed = distance / time_difference
        return speed, hits.tolist()  # Returning the speed and peaks as a list
    return "Not enough hits detected", []
