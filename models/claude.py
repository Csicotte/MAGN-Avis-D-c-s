import anthropic


class ClaudeAPI:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_tone_instructions(self, tone):
        tone_instructions = {
            "Formel et respectueux": """
                Le ton doit être formel et solennel, utilisant un langage soutenu et des formulations traditionnelles.
                Privilégiez des expressions respectueuses.
                Évitez toute familiarité ou légèreté dans le texte.
            """,
            "Chaleureux et empathique": """
                Le ton doit être chaleureux et réconfortant, mettant l'accent sur l'aspect humain et les émotions.
                Utilisez un langage empathique qui touche le cœur des lecteurs.
                Mettez en valeur les relations humaines et les moments de joie partagés.
            """,
            "Traditionnel": """
                Le ton doit suivre les conventions traditionnelles des avis de décès.
                Utilisez des formulations classiques et des structures conventionnelles.
                Respectez les formats standard tout en maintenant une touche personnelle.
            """,
            "Narratif": """
                Le ton doit être narratif, racontant l'histoire de la vie de la personne.
                Créez un récit fluide qui célèbre le parcours unique du défunt.
                Mettez l'accent sur les moments marquants et les accomplissements.
            """
        }
        return tone_instructions.get(tone, tone_instructions["Formel et respectueux"])

    def generate_obituary(self, info_dict):
        tone_instruction = self.get_tone_instructions(info_dict['tone'])
        
        prompt = f"""
        En tant que rédacteur professionnel d'avis de décès, créez un avis de décès en français pour cette personne.
        
        Utilisez strictement ces informations, sans ajouts ni suppositions:
        
        Nom: {info_dict['title']} {info_dict['name']}
        Age: {info_dict['age']} ans
        Date de décès: {info_dict['date_of_death']}
        Enfants: {info_dict['children']}
        Petits-enfants: {info_dict['grandchildren']}
        Intérêts/Passions: {info_dict['interests']}
        Profession: {info_dict['profession']}
        Date de la cérémonie: {info_dict['date_of_ceremonie']}

        Instructions de ton:
        {tone_instruction}

        Notes supplémentaires: {info_dict['notes']}

        Directives importantes:
        1. L'avis doit être complet et final, prêt à être publié
        2. Ne pas inclure de mentions de dons ou d'œuvres caritatives s'il n'est pas indiqué.
        3. Ne pas ajouter d'informations non fournies
        4. Ne pas inclure de placeholders ou de texte à remplir
        5. Structure en 4 paragraphes maximum
        6. Mentionner la date de la cérémonie dans le dernier paragraphe

        Format requis:
        - Premier paragraphe: Annonce du décès avec les informations principales
        - Deuxième et troisième paragraphe: Description de la personne (carrière, passions, famille)
        - Dernier paragraphe: Détails de la cérémonie
        """
        print(prompt)
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.5,
            system="Vous êtes un expert de la rédaction d'avis de décès, capable d'adapter votre style d'écriture à différents tons tout en conservant professionnalisme et respect.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        message = response.content[0].text.strip()
        return message