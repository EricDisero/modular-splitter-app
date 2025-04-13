"""
Advanced stems processor for hybrid processing of HTDemucs outputs.
"""
import os
import logging
from pathlib import Path
import uuid
import soundfile as sf
import numpy as np

from app.utils.audio import (
    adjust_volume,
    invert_phase_and_mix,
    PROCESSED_DIR
)

logger = logging.getLogger("splitter.stems")


class StemsProcessor:
    """
    Processor for creating enhanced stems from HTDemucs outputs.
    """

    def __init__(self, output_dir=None):
        """
        Initialize stems processor.

        Args:
            output_dir: Directory to save processed stems
        """
        self.output_dir = output_dir or PROCESSED_DIR

    def process_stems(self, input_file, stem_files, output_prefix=None):
        """
        Process stems to create a complete stem package including EE track.

        Args:
            input_file: Original input file
            stem_files: Dictionary mapping stem names to file paths
            output_prefix: Prefix for output filenames

        Returns:
            Dictionary mapping stem types to output file paths
        """
        try:
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)

            # Set up output prefix
            if output_prefix is None:
                output_prefix = Path(input_file).stem

            # Process outputs directory
            outputs_dir = os.path.join(self.output_dir, f"{output_prefix}_stems")
            os.makedirs(outputs_dir, exist_ok=True)

            # Process each stem
            output_files = {}
            selected_files = []  # For EE processing

            for stem_name, stem_file in stem_files.items():
                # Skip processing if the stem doesn't exist
                if not os.path.exists(stem_file):
                    logger.warning(f"Stem file not found: {stem_file}")
                    continue

                # Set output filename
                output_filename = f"{output_prefix} {stem_name.capitalize()}.wav"
                output_path = os.path.join(outputs_dir, output_filename)

                # Adjust volume (increase by 10dB to compensate for earlier reduction)
                adjust_volume(stem_file, output_path, 10)

                # Track output files
                output_files[stem_name] = output_path

                # Add to selected files for EE processing if it's drums, bass, or vocals
                if stem_name.lower() in ['drums', 'bass', 'vocals']:
                    selected_files.append(output_path)

            # Create "EE" (everything else) track if we have the necessary stems
            if len(selected_files) > 0 and os.path.exists(input_file):
                ee_output_path = os.path.join(outputs_dir, f"{output_prefix} EE.wav")
                invert_phase_and_mix(input_file, selected_files, ee_output_path)
                output_files['ee'] = ee_output_path

            # Remove "other" stem if "ee" stem was created successfully
            if 'ee' in output_files and 'other' in output_files:
                other_path = output_files['other']
                if os.path.exists(other_path):
                    try:
                        os.remove(other_path)
                        logger.info(f"Removed 'other' stem as 'ee' stem was created: {other_path}")
                        del output_files['other']
                    except Exception as e:
                        logger.warning(f"Failed to remove 'other' stem: {e}")

            return {
                'output_dir': outputs_dir,
                'stems': output_files
            }

        except Exception as e:
            logger.error(f"Error processing stems: {str(e)}")
            return None

    def create_track_preview(self, stem_file, duration=30.0):
        """
        Create a preview clip from a stem file.

        Args:
            stem_file: Path to the stem file
            duration: Duration of the preview in seconds

        Returns:
            Path to the preview file
        """
        try:
            # Read the stem file
            data, samplerate = sf.read(stem_file)

            # Calculate sample count for the preview
            preview_samples = int(duration * samplerate)

            # If file is shorter than requested duration, use the whole file
            if data.shape[0] <= preview_samples:
                return stem_file

            # Find a good starting point (1/4 into the file)
            start_sample = min(int(data.shape[0] * 0.25), data.shape[0] - preview_samples)

            # Extract the preview segment
            preview_data = data[start_sample:start_sample + preview_samples]

            # Create a preview filename
            preview_path = f"{os.path.splitext(stem_file)[0]}_preview.wav"

            # Write the preview file
            sf.write(preview_path, preview_data, samplerate, subtype='FLOAT')

            logger.info(f"Created preview clip: {preview_path}")
            return preview_path

        except Exception as e:
            logger.error(f"Error creating preview clip: {str(e)}")
            return None

    def create_mp3_version(self, wav_file, bitrate=320):
        """
        Create an MP3 version of a WAV file.

        Args:
            wav_file: Path to the WAV file
            bitrate: MP3 bitrate in kbps

        Returns:
            Path to the MP3 file
        """
        try:
            # Import lameenc for MP3 encoding
            import lameenc

            # Read the WAV file
            data, samplerate = sf.read(wav_file)

            # Create an MP3 filename
            mp3_path = f"{os.path.splitext(wav_file)[0]}.mp3"

            # Set up the encoder
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(bitrate)
            encoder.set_in_sample_rate(samplerate)
            encoder.set_channels(data.shape[1] if len(data.shape) > 1 else 1)
            encoder.set_quality(2)  # High quality

            # Convert data to the format expected by lameenc
            if len(data.shape) > 1:
                # Stereo
                data = data.T  # lameenc expects channels-first format
            else:
                # Mono
                data = data.reshape(1, -1)

            # Ensure data is in the correct format (16-bit PCM)
            if data.dtype.kind == 'f':
                data = (data * 32767).astype(np.int16)

            # Encode to MP3
            mp3_data = encoder.encode(data.tobytes())
            mp3_data += encoder.flush()

            # Write the MP3 file
            with open(mp3_path, 'wb') as f:
                f.write(mp3_data)

            logger.info(f"Created MP3 version: {mp3_path}")
            return mp3_path

        except ImportError:
            logger.error("lameenc not installed, cannot create MP3")
            return None
        except Exception as e:
            logger.error(f"Error creating MP3 version: {str(e)}")
            return None

    def create_zip_package(self, output_dir, format="wav"):
        """
        Create a ZIP package containing all stems in the specified format.

        Args:
            output_dir: Directory containing the stems
            format: Output format ("wav" or "mp3")

        Returns:
            Path to the ZIP file
        """
        try:
            import zipfile

            # Create ZIP filename
            zip_path = f"{output_dir}.zip"

            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add files to ZIP
                for file in os.listdir(output_dir):
                    # Check if the file is in the requested format or needs conversion
                    file_path = os.path.join(output_dir, file)
                    _, ext = os.path.splitext(file)

                    # If MP3 is requested but file is WAV, convert it
                    if format == "mp3" and ext.lower() == ".wav":
                        mp3_path = self.create_mp3_version(file_path)
                        if mp3_path:
                            # Add MP3 file to ZIP using the original filename but with .mp3 extension
                            mp3_filename = os.path.basename(mp3_path)
                            zipf.write(mp3_path, mp3_filename)
                    else:
                        # Add file to ZIP as is
                        zipf.write(file_path, file)

            logger.info(f"Created ZIP package: {zip_path}")
            return zip_path

        except Exception as e:
            logger.error(f"Error creating ZIP package: {str(e)}")
            return None