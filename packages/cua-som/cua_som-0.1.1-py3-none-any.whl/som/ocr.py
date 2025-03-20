from typing import List, Dict, Any, Tuple
import logging
import signal
from contextlib import contextmanager
from pathlib import Path
import easyocr
from PIL import Image
import numpy as np
import torch

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds: int):
    def timeout_handler(signum, frame):
        raise TimeoutException("OCR process timed out")

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


class OCRProcessor:
    """Class for handling OCR text detection."""

    _shared_reader = None  # Class-level shared reader instance

    def __init__(self):
        """Initialize the OCR processor."""
        self.reader = None
        # Determine best available device
        self.device = "cpu"
        if torch.cuda.is_available():
            self.device = "cuda"
        elif (
            hasattr(torch, "backends")
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            self.device = "mps"
        logger.info(f"OCR processor initialized with device: {self.device}")

    def _ensure_reader(self):
        """Ensure EasyOCR reader is initialized.

        Uses a class-level cached reader to avoid reinitializing on every instance.
        """
        # First check if we already have a class-level reader
        if OCRProcessor._shared_reader is not None:
            self.reader = OCRProcessor._shared_reader
            return

        # Otherwise initialize a new one
        if self.reader is None:
            try:
                logger.info("Initializing EasyOCR reader...")
                import easyocr

                # Use GPU if available
                use_gpu = self.device in ["cuda"]  # MPS not directly supported by EasyOCR

                # If using MPS, add warnings to explain why CPU is used
                if self.device == "mps":
                    logger.warning("EasyOCR doesn't support MPS directly. Using CPU instead.")
                    logger.warning(
                        "To silence this warning, set environment variable: PYTORCH_ENABLE_MPS_FALLBACK=1"
                    )

                self.reader = easyocr.Reader(["en"], gpu=use_gpu)

                # Verify reader initialization
                if self.reader is None:
                    raise ValueError("Failed to initialize EasyOCR reader")

                # Cache the reader at class level
                OCRProcessor._shared_reader = self.reader

                logger.info(f"EasyOCR reader initialized successfully with GPU={use_gpu}")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {str(e)}")
                # Set to a placeholder that will be checked
                self.reader = None
                raise RuntimeError(f"EasyOCR initialization failed: {str(e)}") from e

    def detect_text(
        self, image: Image.Image, confidence_threshold: float = 0.5, timeout_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """Detect text in an image using EasyOCR.

        Args:
            image: PIL Image to process
            confidence_threshold: Minimum confidence for text detection
            timeout_seconds: Maximum time to wait for OCR

        Returns:
            List of text detection dictionaries
        """
        try:
            # Try to initialize reader, catch any exceptions
            try:
                self._ensure_reader()
            except Exception as e:
                logger.error(f"Failed to initialize OCR reader: {str(e)}")
                return []

            # Ensure reader was properly initialized
            if self.reader is None:
                logger.error("OCR reader is None after initialization")
                return []

            # Convert PIL Image to numpy array
            image_np = np.array(image)

            try:
                with timeout(timeout_seconds):
                    results = self.reader.readtext(
                        image_np, paragraph=False, text_threshold=confidence_threshold
                    )
            except TimeoutException:
                logger.warning("OCR timed out")
                return []
            except Exception as e:
                logger.warning(f"OCR failed: {str(e)}")
                return []

            detections = []
            img_width, img_height = image.size

            for box, text, conf in results:
                if conf < confidence_threshold:
                    continue

                # Convert box format to [x1, y1, x2, y2]
                x1 = min(point[0] for point in box) / img_width
                y1 = min(point[1] for point in box) / img_height
                x2 = max(point[0] for point in box) / img_width
                y2 = max(point[1] for point in box) / img_height

                detections.append(
                    {
                        "type": "text",
                        "bbox": [x1, y1, x2, y2],
                        "content": text,
                        "confidence": conf,
                        "interactivity": False,  # Text is typically non-interactive
                    }
                )

            return detections
        except Exception as e:
            logger.error(f"Unexpected error in OCR processing: {str(e)}")
            return []
