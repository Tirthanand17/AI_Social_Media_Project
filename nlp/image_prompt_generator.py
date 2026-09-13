"""Backward-compatible image-prompt entry points.

The canonical implementation lives in nlp.image_generator. This module exists
because earlier project documentation referenced image_prompt_generator.py.
"""

try:
    from .image_generator import (
        detect_category,
        generate_image_prompt,
        generate_prompt_package,
        generate_video_prompt,
        keywords,
    )
except ImportError:  # supports direct script/sys.path based startup
    from image_generator import (
        detect_category,
        generate_image_prompt,
        generate_prompt_package,
        generate_video_prompt,
        keywords,
    )

__all__ = [
    "detect_category",
    "generate_image_prompt",
    "generate_prompt_package",
    "generate_video_prompt",
    "keywords",
]
