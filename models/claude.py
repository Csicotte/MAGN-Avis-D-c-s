import anthropic


class ClaudeAPI:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_obituary(self, info_dict):
        prompt = f"""
        En tant que rédacteur professionnel d'avis de décès, créez un avis de décès en français pour cette personne.
        
        Utilisez strictement ces informations, sans ajouts ni suppositions:
        
        Nom: {info_dict['name']}
        Age: {info_dict['age']} ans
        Date de décès: {info_dict['date_of_death']}
        Lieu: {info_dict['location']}
        Enfants: {info_dict['children']}
        Petits-enfants: {info_dict['grandchildren']}
        Intérêts/Passions: {info_dict['interests']}
        Profession: {info_dict['profession']}
        Date de la cérémonie: {info_dict['date_of_ceremonie']}

        Directives importantes:
        1. L'avis doit être complet et final, prêt à être publié
        2. Ne pas inclure de mentions de dons ou d'œuvres caritatives
        3. Ne pas ajouter d'informations non fournies
        4. Ne pas inclure de placeholders ou de texte à remplir
        5. Utiliser un ton respectueux et empathique
        6. Structure en 3-4 paragraphes maximum
        7. Mentionner la date de la cérémonie dans le dernier paragraphe

        Format requis:
        - Premier paragraphe: Annonce du décès avec les informations principales
        - Deuxième et troisième paragraphe: Description de la personne (carrière, passions, famille)
        - Dernier paragraphe: Détails de la cérémonie

        Le texte doit être respectueux, émotionnel et personnalisé."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system="You are an expert in writing heartfelt obituaries in French.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        message = response.content[0].text.strip()
        return message