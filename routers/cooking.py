import logging
from fastapi import APIRouter, Response, HTTPException, status
from pydantic import BaseModel, Field

from services import tabpfn_service
from services import gemma_service
from services import voice_service

logger = logging.getLogger("sloth_cooking_router")
logging.basicConfig(level=logging.INFO)

router = APIRouter(tags=["Cooking"])


class SlothCookRequest(BaseModel):
    ingredients: str = Field(
        default="2 eggs, stale bread, curd, cheese slice",
        description="Random expiring ingredients found in fridge or pantry"
    )
    heat_source: str = Field(
        default="skillet",
        description="Heat source preference: microwave, skillet, or stove"
    )
    sloth_level: int = Field(
        default=2,
        ge=1,
        le=3,
        description="1 = Minimal Effort, 2 = Mug/Microwave Only, 3 = Maximum Couch Potato"
    )


class AudioSpeechRequest(BaseModel):
    script: str = Field(
        ...,
        description="Text script for deadpan, slow audio narration"
    )


@router.post("/cook")
async def cook_sloth_meal(request: SlothCookRequest):
    """
    Receives user ingredients, heat preference, and sloth level.
    Evaluates cleanup fatigue and standing time via TabPFN,
    then synthesizes an unapologetically lazy recipe via Gemma 2.
    """
    try:
        # Step 1: Evaluate fatigue telemetry using TabPFN
        telemetry = tabpfn_service.evaluate_sloth_fatigue(
            ingredients_list=request.ingredients,
            heat_source_str=request.heat_source,
            sloth_level=request.sloth_level
        )

        # Step 2: Synthesize lazy recipe with Gemma 2
        recipe = gemma_service.synthesize_sloth_recipe(
            ingredients=request.ingredients,
            fatigue_info=telemetry,
            sloth_level=request.sloth_level
        )

        return {
            "status": "success",
            "data": {
                "telemetry": telemetry,
                "recipe": recipe
            }
        }
    except Exception as e:
        logger.error(f"Error handling /cook request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couch Potato Engine encountered an error: {str(e)}"
        )


@router.post("/speak")
async def speak_sloth_script(request: AudioSpeechRequest):
    """
    Converts sleepy narration script into slow, deadpan MP3 audio via ElevenLabs.
    """
    try:
        audio_bytes = voice_service.stream_sloth_audio(request.script)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error handling /speak request: {e}", exc_info=True)
        return Response(content=b"", media_type="audio/mpeg")
