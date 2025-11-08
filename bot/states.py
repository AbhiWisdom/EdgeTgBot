"""
FSM States for the Telegram TTS Bot
"""
from aiogram.fsm.state import State, StatesGroup


class VoiceSelection(StatesGroup):
    """States for voice selection flow"""
    selecting_country = State()
    selecting_language = State()
    selecting_voice = State()
    ready_for_text = State()

