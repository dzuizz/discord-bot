from random import choice, randint


motivating_sentences = [
    "You are stronger than you think.",
    "This too shall pass.",
    "You are enough just as you are.",
    "Your presence in this world matters.",
    "Believe in yourself and all that you are.",
    "You have the power to create change.",
    "Embrace the beauty of your uniqueness.",
    "Your story is still being written.",
    "You are capable of amazing things.",
    "You deserve love and happiness.",
    "Each day is a new beginning.",
    "You are worthy of all good things.",
    "Keep moving forward, one step at a time.",
    "Your feelings are valid.",
    "You have the strength to overcome any challenge.",
    "Focus on the present and cherish every moment.",
    "You are never truly alone.",
    "Believe in the power of hope.",
    "Your resilience is inspiring.",
    "Find joy in the little things.",
    "You are a work of art in progress.",
    "Keep your head up and your heart strong.",
    "Every storm eventually runs out of rain.",
    "Your journey is unique and beautiful.",
    "You have the ability to make a difference.",
    "Self-love is the best kind of love.",
    "You are braver than you believe.",
    "Embrace your inner strength.",
    "The best is yet to come.",
    "You are a beacon of light in the darkness.",
    "Find comfort in your own company.",
    "You have the courage to face your fears.",
    "Your potential is limitless.",
    "Trust the process of life.",
    "You are a source of inspiration.",
    "Cherish your own companionship.",
    "Your future is full of possibilities.",
    "You have a beautiful heart.",
    "You are deserving of peace and serenity.",
    "Keep believing in your dreams.",
    "You are a masterpiece in the making.",
    "Your presence brings joy to others.",
    "You are a treasure worth finding.",
    "Embrace the journey of self-discovery.",
    "You have the power to write your own story.",
    "Your inner light shines brightly.",
    "Take pride in how far you’ve come.",
    "You are an important piece of this world.",
    "You have the strength to keep going.",
    "Believe in the beauty of your dreams."
]


def lonely_chat(user_input: str) -> str:
    user_input = user_input.lower()

    return choice(motivating_sentences) if "help" in user_input else "womp womp"
