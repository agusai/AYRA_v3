"""
daisy_loader.py - Load Daisy's literary works from JSON files
"""

import json
import os

# Path ke JSON files (adjust ikut folder Abang)
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json_file(filename):
    """Helper to load JSON file"""
    filepath = os.path.join(JSON_PATH, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return empty structure if file not found
        return {}
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

def load_novel():
    """Load novel from daisy_novel.json"""
    data = load_json_file("daisy_novel.json")
    
    # Default structure if file empty
    if not data:
        return {
            "title": "GEMA DI SELEKOH TAKDIR",
            "chapters": [
                {
                    "title": "Prolog: 2:15 AM",
                    "content": "Novel content akan muncul bila JSON disediakan."
                }
            ]
        }
    return data

def load_arkib():
    """Load character archives from daisy_arkib.json"""
    data = load_json_file("daisy_arkib.json")
    
    if not data:
        return {
            "characters": [
                {
                    "name": "Aris",
                    "role": "The Broken Rider",
                    "monologues": [
                        {
                            "title": "Tentang Kehilangan",
                            "content": "Dia tinggalkan lukisan tak siap. Sama macam hidup aku."
                        }
                    ]
                }
            ]
        }
    return data

def load_rahsia():
    """Load writing lessons from daisy_rahsia.json"""
    data = load_json_file("daisy_rahsia.json")
    
    if not data:
        return {
            "lessons": [
                {
                    "title": "The Ink Alchemist: Lesson 1",
                    "content": "Jangan tulis apa yang kau nampak. Tulis apa yang kau rasa."
                }
            ]
        }
    return data

# Optional: Function to get specific chapter
def get_chapter(chapter_index=0):
    """Get specific chapter from novel"""
    novel = load_novel()
    chapters = novel.get("chapters", [])
    if 0 <= chapter_index < len(chapters):
        return chapters[chapter_index]
    return None

# Optional: Function to get character monologue
def get_monologue(character_name):
    """Get monologue for specific character"""
    arkib = load_arkib()
    for char in arkib.get("characters", []):
        if char["name"].lower() == character_name.lower():
            return char.get("monologues", [{}])[0]
    return None