from aiogram.fsm.state import StatesGroup, State


class GroupStates(StatesGroup):
    groups = State()
    group = State()
    order = State()
