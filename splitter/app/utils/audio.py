"""
Audio utility functions for the splitter service.
"""
import os
import logging
import tempfile
import shutil
from pathlib import Path
import uuid
import numpy as np
import soundfile as sf

logger = logging.getLogger("splitter.audio")

# Define directories
TEMP_DIR = os.environ.get("TEMP_DIR", "/tmp/splitter_temp")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/splitter_output")
UPLOADS_DIR = os.path.join(TEMP_DIR, "uploads")
PROCESSED_DIR = os.path.join(TEMP_DIR, "processed")


def setup_processing_dirs():
    """
    Create necessary directories for processing.
    """
    for directory in [TEMP_DIR, OUTPUT_DIR, UPLOADS_DIR, PROCESSED_DIR]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory created/verified: {directory}")


def get_temp_filepath(filename=None, prefix="audio_", suffix=".wav"):
    """
    Get a temporary file path for processing.

    Args:
        filename: Optional base filename
        prefix: Prefix for temporary filename
        suffix: File extension

    Returns:
        Path to temporary file
    """
    if filename:
        basename = os.path.splitext(filename)[0]
        temp_filename = f"{basename}_{uuid.uuid4().hex[:8]}{suffix}"
    else:
        temp_filename = f"{prefix}{uuid.uuid4().hex}{suffix}"

    return os.path.join(UPLOADS_DIR, temp_filename)


def convert_to_44100hz(input_file, output_file=None):
    """
    Convert any audio file to 44.1kHz sample rate.

    Args:
        input_file: Path to input audio file
        output_file: Path to output file (optional)

    Returns:
        Path to the converted file
    """
    try:
        # Check if file needs conversion
        info = sf.info(input_file)

        # If already 44.1kHz, return the original file path
        if abs(info.samplerate - 44100) < 100:
            logger.info(f"File {input_file} already at 44.1kHz, skipping conversion")
            return input_file

        if output_file is None:
            # Create new file in temp directory
            output_file = get_temp_filepath(os.path.basename(input_file))

        logger.info(f"Converting {input_file} from {info.samplerate}Hz to 44.1kHz")

        # Read the audio data
        data, samplerate = sf.read(input_file)

        # Write with new samplerate
        sf.write(output_file, data, 44100, subtype='PCM_24')

        logger.info(f"Successfully converted to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error converting sample rate: {str(e)}")
        # Return original file if conversion fails
        return input_file


def adjust_volume(input_file, output_file, db_change):
    """
    Adjust the volume of an audio file by a certain number of decibels.

    Args:
        input_file: Path to input audio file
        output_file: Path to output file
        db_change: dB change (positive=louder, negative=quieter)

    Returns:
        True if successful, False otherwise
    """
    try:
        data, samplerate = sf.read(input_file)

        # Convert dB to amplitude factor
        factor = np.power(10, db_change / 20)

        # Adjust volume
        adjusted_data = data * factor

        # Write output
        sf.write(output_file, adjusted_data, samplerate, subtype='FLOAT')

        logger.info(f"Audio volume adjusted by {db_change}dB and saved to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error adjusting volume: {str(e)}")
        return False


def invert_phase_and_mix(original_file, stems_files, output_file):
    """
    Invert phase of stems and mix with original for EE stems.

    Args:
        original_file: Path to original audio file
        stems_files: List of paths to stems files to invert
        output_file: Path to output file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the original input file
        original_data, samplerate = sf.read(original_file)

        # Initialize a numpy array for the sum of selected stems
        summed_stems_data = None

        # Sum the selected stems
        for stem_file in stems_files:
            data, _ = sf.read(stem_file)
            if summed_stems_data is None:
                summed_stems_data = np.zeros_like(data)
            summed_stems_data += data

        # Invert phase of the summed stems
        inverted_stems_data = summed_stems_data * -1

        # Check for shape mismatch and handle it
        if original_data.shape != inverted_stems_data.shape:
            logger.warning(f"Shape mismatch: original={original_data.shape}, stems={inverted_stems_data.shape}")

            # Resize to the smaller of the two lengths
            min_length = min(original_data.shape[0], inverted_stems_data.shape[0])
            original_data = original_data[:min_length]
            inverted_stems_data = inverted_stems_data[:min_length]
            logger.info(f"Resized both arrays to length {min_length}")

        # Mix inverted phase stems with the original track
        mixed_data = original_data + inverted_stems_data

        # Write the result to the output file
        sf.write(output_file, mixed_data, samplerate, subtype='FLOAT')

        logger.info(f"Mixed and saved EE track to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error creating EE mix: {str(e)}")
        return False


def normalize_audio(audio_data, target_db=-1.0):
    """
    Normalize audio to a target dB level.

    Args:
        audio_data: Numpy array of audio data
        target_db: Target peak dB level (0 = maximum without clipping)

    Returns:
        Normalized audio data
    """
    # Find the peak amplitude
    peak = np.max(np.abs(audio_data))

    # Calculate the current dB level
    current_db = 20 * np.log10(peak) if peak > 0 else -96.0

    # Calculate the gain needed
    gain_db = target_db - current_db
    gain_factor = np.power(10, gain_db / 20)

    # Apply the gain
    return audio_data * gain_factor


def cleanup_temp_files(file_paths):
    """
    Clean up temporary files after processing.

    Args:
        file_paths: List of file paths to clean up
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                logger.debug(f"Removed temporary file: {path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {path}: {str(e)}")