"""
HTDemucs runner for audio source separation.
"""
import os
import logging
import subprocess
import tempfile
from pathlib import Path

from app.utils.audio import PROCESSED_DIR, convert_to_44100hz, adjust_volume

logger = logging.getLogger("splitter.demucs")


class HTDemucsRunner:
    """
    Runner for HTDemucs model to separate audio sources.
    """

    def __init__(
            self,
            model_name="htdemucs",
            device="cuda",
            model_dir=None,
            stems=None,
            shifts=1,
            split=True,
            overlap=0.25,
            float32=True
    ):
        """
        Initialize HTDemucs runner.

        Args:
            model_name: Name of the model to use
            device: Device to use for inference (cuda, cpu)
            model_dir: Directory containing the model
            stems: List of stems to extract (default: all)
            shifts: Number of random shifts for equivariant stabilization
            split: Whether to split audio in chunks
            overlap: Overlap between chunks
            float32: Whether to use 32-bit float output
        """
        self.model_name = model_name
        self.device = device
        self.model_dir = model_dir
        self.stems = stems
        self.shifts = shifts
        self.split = split
        self.overlap = overlap
        self.float32 = float32

    def separate(self, input_file, output_dir=None, filename_prefix=None):
        """
        Separate audio sources using HTDemucs.

        Args:
            input_file: Path to input audio file
            output_dir: Directory to save separated stems (default: PROCESSED_DIR)
            filename_prefix: Prefix for output filenames

        Returns:
            Dictionary with paths to separated stems
        """
        try:
            # Convert to 44.1kHz if needed
            logger.info(f"Checking sample rate of {input_file}")
            converted_input = convert_to_44100hz(input_file)
            logger.info(f"Using file {converted_input} for processing")

            # Prepare temporary directories
            if output_dir is None:
                output_dir = PROCESSED_DIR

            # Create output directory
            os.makedirs(output_dir, exist_ok=True)

            # Prepare filename prefix
            if filename_prefix is None:
                filename_prefix = Path(input_file).stem

            # Create a copy of the input file with reduced volume
            temp_input_file = os.path.join(output_dir, f"{filename_prefix}_temp.wav")
            adjust_volume(converted_input, temp_input_file, -10)

            # Build command for Demucs
            cmd = [
                "python", "-m", "demucs.separate",
                "--out", str(output_dir),
                "--name", self.model_name,
                "-d", self.device,
                "--shifts", str(self.shifts)
            ]

            # Add optional arguments
            if self.float32:
                cmd.append("--float32")

            if not self.split:
                cmd.append("--no-split")
            else:
                cmd.append(f"--overlap={self.overlap}")

            if self.stems:
                cmd.append("--stems")
                cmd.append(",".join(self.stems))

            # Add input file
            cmd.append(str(temp_input_file))

            # Run Demucs
            logger.info(f"Running HTDemucs with command: {' '.join(cmd)}")
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            # Get paths to separated stems
            model_output_dir = os.path.join(output_dir, self.model_name)
            track_output_dir = os.path.join(model_output_dir, os.path.splitext(os.path.basename(temp_input_file))[0])

            if not os.path.exists(track_output_dir):
                # Try with _temp removed
                alt_dir_name = os.path.splitext(os.path.basename(input_file))[0]
                track_output_dir = os.path.join(model_output_dir, alt_dir_name)

            if not os.path.exists(track_output_dir):
                logger.error(f"Output directory not found: {track_output_dir}")
                return None

            # Get list of stem files
            stem_files = {}
            for stem_file in os.listdir(track_output_dir):
                if stem_file.endswith(".wav"):
                    stem_name = stem_file.split(".")[-2]  # Get the stem name (drums, bass, etc.)
                    stem_files[stem_name] = os.path.join(track_output_dir, stem_file)

            logger.info(f"Separation complete. Found stems: {', '.join(stem_files.keys())}")

            # Clean up temporary files
            try:
                if os.path.exists(temp_input_file):
                    os.remove(temp_input_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")

            return stem_files

        except Exception as e:
            logger.error(f"Error during source separation: {str(e)}")
            return None