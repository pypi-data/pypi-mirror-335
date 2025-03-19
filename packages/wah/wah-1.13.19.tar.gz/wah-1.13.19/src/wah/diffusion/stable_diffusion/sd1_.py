from diffusers import StableDiffusionPipeline

from ..utils import is_valid_version
from .scheduler import load_scheduler

__all__ = [
    "load_pipeline",
]

model_ids = {
    "1.1": "CompVis/stable-diffusion-v1-1",
    "1.2": "CompVis/stable-diffusion-v1-2",
    "1.3": "CompVis/stable-diffusion-v1-3",
    "1.4": "CompVis/stable-diffusion-v1-4",
    "1.5": "sd-legacy/stable-diffusion-v1-5",
}


def load_pipeline(
    version: str,
    scheduler: str,
    **kwargs,
) -> StableDiffusionPipeline:
    assert is_valid_version(version, model_ids)
    pipeline = StableDiffusionPipeline.from_pretrained(
        model_ids[version],
        scheduler=load_scheduler(version, model_ids, scheduler),
        **kwargs,
    )
    pipeline.safety_checker = None
    return pipeline
