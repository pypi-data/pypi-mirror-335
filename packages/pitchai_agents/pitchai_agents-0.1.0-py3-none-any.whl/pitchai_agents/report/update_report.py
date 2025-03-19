
from agent.report.relevant_headers import get_relevant_header
from agent.report.integrate_text import integrate
from agent.report.md_headers import get_text_under_header, header_identifier_to_markdown, get_markdown_header_from_number
import logging
import os

logger = logging.getLogger(__name__)


async def update_report(new_text_md: str, global_goal: str = "", report_path: str = 'agent/report/code_agent_report.md'):

    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            current_report_md = f.read()
    else:
        current_report_md = '# Report\n\n'

    relevant_header = await get_relevant_header(current_report_md, new_text_md)
    if not relevant_header:
        return


    # Ensure parent path exists
    parent_path = os.path.dirname(report_path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    
    relevant_header_as_md = header_identifier_to_markdown(relevant_header)

    text_under_header = get_text_under_header(current_report_md, relevant_header_as_md)

    extra_info = f"\n#### Theme: {relevant_header_as_md}\n\n#### Context of this report: '''{global_goal}'''\n\n"

    # If header has text, integrate the new text
    if text_under_header.strip() != "":
        logger.info(f"Updating text under header")
        integrated_text = await integrate(text_under_header, new_text_md, extra_info=extra_info)
        if text_under_header not in current_report_md:
            raise ValueError(f"Header {text_under_header} not found in report")
        current_report_md = current_report_md.replace(text_under_header, integrated_text)

    # If empty header just add the new text
    elif text_under_header.strip() == "" and relevant_header_as_md in current_report_md:
        logger.info(f"Adding new text under header")
        integrated_text = await integrate('Please just summarize and condense the other text and throw away all fluff.', new_text_md, extra_info=extra_info)
        if relevant_header_as_md not in current_report_md:
            raise ValueError(f"Header {relevant_header_as_md} not found in report")
        current_report_md = current_report_md.replace(relevant_header_as_md, f"{relevant_header_as_md}\n\n{integrated_text}")

    # If the header not in the report find the parent header
    elif text_under_header.strip() == "" and not relevant_header_as_md in current_report_md:
        logger.info(f"Adding new text under parent header")
        header_number = relevant_header.split(' ')[0]
        parent_header_number = header_number.split('.')[:-1]
        parent_header_number = '.'.join(parent_header_number)
        parent_md_header = get_markdown_header_from_number(markdown_string=current_report_md, number_identifier=parent_header_number)
        
        # If parent header exists, add the new header under it
        text_under_parent_header = get_text_under_header(current_report_md, parent_md_header)

        # If parent header is not without text
        if text_under_parent_header.strip() != "":
            logger.info(f"Adding new text under parent header that has text")
            integrated_text = await integrate('Please just summarize and condense the other text and throw away all fluff.', new_text_md, extra_info=extra_info)
            if text_under_parent_header not in current_report_md:
                raise ValueError(f"Parent header {text_under_parent_header} not found in report")
            current_report_md = current_report_md.replace(text_under_parent_header, f"{text_under_parent_header}\n\n{relevant_header_as_md}\n\n{integrated_text}")

        
        # If parent header is without text
        else:
            logger.info(f"Adding new text under parent header that has no text")
            integrated_text = await integrate('Please just summarize and condense the other text and throw away all fluff.', new_text_md, extra_info=extra_info)
            if parent_md_header not in current_report_md:
                raise ValueError(f"Parent header {parent_md_header} not found in report")
            current_report_md = current_report_md.replace(parent_md_header, f"{parent_md_header}\n\n{relevant_header_as_md}\n\n{integrated_text}")
    
    
        

    # Save the updated report   
    with open(report_path, 'w') as f:
        f.write(current_report_md)


if __name__ == '__main__':
    new_text = '''
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
'''

    new_text = """
Grote stappen naar een duurzamer wagenpark
Elektrische mobiliteit biedt op korte termijn een oplossing voor de reductie van de milieu-impact van het gemotoriseerd personenvervoer. Al met al bieden elektrische auto's belangrijke voordelen ten opzichte van conventionele auto's, zowel qua CO2-uitstoot als qua rijervaring en operationele kost, en dragen ze bij aan de overgang naar duurzame mobiliteit. Het is dan ook logisch dat het aandeel van volledig elektrische personenwagens blijft stijgen op de weg. Terwijl het aantal voertuigen stijgt, gaat het met de laadinfrastructuur iets langzamer vooruit. Daarom is het belangrijk om ook naar de toekomst te kijken en laadopties te voorzien.

Volvo Trucks Gent heeft het begrepen!
Ook bij onze klanten is er een duidelijke weerspiegeling van de energietransitie. Een goed  voorbeeld hiervan is de succesvolle uitrol van laadinfrastructuur bij Volvo Trucks in Gent. Hierdoor kunnen ze hun elektrische wagenpark verder laten groeien en dat is positief voor de verduurzaming van de bedrijfswereld.

Met de installatie van 28 laadpunten in een eerste fase, zijn ze goed van start gegaan. Dit helpt de huidige vloot om opgeladen op bestemming te arriveren. Afhankelijk van de groeiende vraag naar laadpalen zal dit aantal in de toekomst uitgebreid worden tot minstens 168 laadpunten.

Dankzij onze expertise hebben we geholpen bij het optimaliseren van de locatie en het bepalen van het aantal laadpunten. Ervoor zorgen dat de bestaande elektrische infrastructuur niet overbelast raakt en dat het opladen gebeurt met stroom uit hernieuwbare energiebronnen is een belangrijk aspect van het verduurzamen van de laadinfrastructuur.

De installatie en optimalisatie van de infrastructuur bij Volvo Trucks Gent zorgt voor het optimaal gebruik van de eigen opgewekte energie. Dit hele project geeft een fijn perspectief voor de toekomst van het elektrisch wagenpark met een future-proof plan voor eventuele uitbereiding. Dit is een goed voorbeeld van hoe we kunnen bijdragen aan een duurzamere wereld!

Wil je meer weten over hoe je best jouw wagenpark duurzaam oplaadt? Neem dan zeker contact met ons op via info@encon.eu."""

    new_text = '''
redcent hebben we ook een deal met mercedes opgezet
'''

    import asyncio
    asyncio.run(update_report(new_text))