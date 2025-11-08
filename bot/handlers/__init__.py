"""
Handlers package - imports all routers
"""
from .start_handler import router as start_router
from .country_handler import router as country_router
from .language_handler import router as language_router
from .voice_handler import router as voice_router
from .navigation_handler import router as navigation_router
from .tts_handler import router as tts_router
from .media_handler import router as media_router
from .broadcast_handler import router as broadcast_router

# List of all routers in the order they should be registered
all_routers = [
    broadcast_router,      # Owner commands first
    start_router,
    country_router,
    language_router,
    voice_router,
    navigation_router,
    tts_router,
    media_router,
]

__all__ = ['all_routers']

