import json
import os
from flask import request

class TranslationService:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        for file in os.listdir(translations_dir):
            if file.endswith('.json'):
                lang = file.split('.')[0]
                with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
    
    def get_translation(self, key, lang=None):
        if not lang:
            lang = request.accept_languages.best_match(['en', 'es']) or 'en'
        
        keys = key.split('.')
        value = self.translations.get(lang, {})
        for k in keys:
            value = value.get(k, key)
        return value