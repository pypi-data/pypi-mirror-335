from agent.report.md_headers import get_headers
from chat.ui_msg_actions import UIMsgActions
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from typing import List


async def integrate(text_1: str, text_2: str, extra_info:str = '', msg_actions:UIMsgActions = None, conversation_id:str='test', headless: bool=True) -> List[str]:
    """
    Integrates previous and existing text.
    """
    

    # Create msg actions if not given
    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    response = await msg_actions.run_action(action_id=f'integrate', prompt_path='integrate', prompt_format_kwargs={'text_1': text_1, 'text_2': text_2, 'extra_info': extra_info}, model='gemini-2.0-flash', silent=False)

    response = try_splitoff_code_w_fallbacks(response, ['```md', '```markdown', '```md```'], '```')

    return response



if __name__ == '__main__':
    import asyncio
    text1 = """
    encon.eu
Duurzaamheid biedt een oplossing voor de huidige bedrijfsuitdagingen
Duurzaamheid is niet langer weg te denken en heeft een impact op elk onderdeel van de bedrijfsvoering. Of het nu gaat over de toenemende druk op de operationele marges, de nood aan meer rendabele investeringen of de uitdaging om te blijven voldoen aan de kritische vragen van medewerkers en consumenten.
Lean operations
Door op een creatieve manier te kijken naar opportuniteiten voor energie-efficiëntie of hernieuwbare energie kunnen er belangrijke kostenbesparingen worden gerealiseerd.
Ontdek
Customer centricity
In de concurrentiële wereldwijde markt geven consumenten aan een voorkeur te hebben voor duurzame producten, diensten en bedrijven.
Ontdek
Employer branding
In de war for talent geven werknemers aan een voorkeur te hebben voor bedrijven met een duidelijke purpose.
Ontdek
Rendabel investeren
In deze onzekere en veranderlijke tijden laten de cijfers zien dat duurzame investeringen op lange termijn stabiel zijn.
Ontdek
    """
    

    text2 = """
Grote stappen naar een duurzamer wagenpark
Elektrische mobiliteit biedt op korte termijn een oplossing voor de reductie van de milieu-impact van het gemotoriseerd personenvervoer. Al met al bieden elektrische auto's belangrijke voordelen ten opzichte van conventionele auto's, zowel qua CO2-uitstoot als qua rijervaring en operationele kost, en dragen ze bij aan de overgang naar duurzame mobiliteit. Het is dan ook logisch dat het aandeel van volledig elektrische personenwagens blijft stijgen op de weg. Terwijl het aantal voertuigen stijgt, gaat het met de laadinfrastructuur iets langzamer vooruit. Daarom is het belangrijk om ook naar de toekomst te kijken en laadopties te voorzien.

Volvo Trucks Gent heeft het begrepen!
Ook bij onze klanten is er een duidelijke weerspiegeling van de energietransitie. Een goed  voorbeeld hiervan is de succesvolle uitrol van laadinfrastructuur bij Volvo Trucks in Gent. Hierdoor kunnen ze hun elektrische wagenpark verder laten groeien en dat is positief voor de verduurzaming van de bedrijfswereld.

Met de installatie van 28 laadpunten in een eerste fase, zijn ze goed van start gegaan. Dit helpt de huidige vloot om opgeladen op bestemming te arriveren. Afhankelijk van de groeiende vraag naar laadpalen zal dit aantal in de toekomst uitgebreid worden tot minstens 168 laadpunten.

Dankzij onze expertise hebben we geholpen bij het optimaliseren van de locatie en het bepalen van het aantal laadpunten. Ervoor zorgen dat de bestaande elektrische infrastructuur niet overbelast raakt en dat het opladen gebeurt met stroom uit hernieuwbare energiebronnen is een belangrijk aspect van het verduurzamen van de laadinfrastructuur.

De installatie en optimalisatie van de infrastructuur bij Volvo Trucks Gent zorgt voor het optimaal gebruik van de eigen opgewekte energie. Dit hele project geeft een fijn perspectief voor de toekomst van het elektrisch wagenpark met een future-proof plan voor eventuele uitbereiding. Dit is een goed voorbeeld van hoe we kunnen bijdragen aan een duurzamere wereld!

Wil je meer weten over hoe je best jouw wagenpark duurzaam oplaadt? Neem dan zeker contact met ons op via info@encon.eu."""

    print(asyncio.run(integrate(text1, text2)))