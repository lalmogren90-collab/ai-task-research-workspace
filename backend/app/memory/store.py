from collections import defaultdict


conversation_memory = defaultdict(list)


def get_history(conversation_id: str):
    return conversation_memory[conversation_id]


def add_message(conversation_id: str, message: dict):
    conversation_memory[conversation_id].append(message)


def clear_history(conversation_id: str):
    conversation_memory[conversation_id] = []