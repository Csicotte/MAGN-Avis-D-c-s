from deep_translator import GoogleTranslator

class Translator:
    def __init__(self):
        self.available_languages = {
            'Anglais': 'en',
            'Espagnol': 'es',
            'Italien': 'it',
            'Portugais': 'pt',
        }

    def translate_text(self, text, target_language):
        translator = GoogleTranslator(source='fr', target=target_language)
        return translator.translate(text)