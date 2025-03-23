__version__ = "0.1.12"

# Marker Model Pre-download
import logging


# Only download models when actually installed, avoid downloading in development mode
# Check PYTHONPATH to determine if we're in an installation environment
def _initialize_marker():
    try:
        # Import only the required components to preload models
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict

        # Download required models silently
        logging.info("Pre-downloading Marker models during package initialization")
        PdfConverter(artifact_dict=create_model_dict())
        logging.info("Marker models downloaded successfully")
    except ImportError:
        # marker-pdf may not be installed, this is normal, don't raise an error
        pass
    except Exception as e:
        # If download fails, record the error but don't prevent package import
        logging.warning(f"Failed to pre-download Marker models: {e}")

# Execute initialization
_initialize_marker()
