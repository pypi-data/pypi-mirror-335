# Email Reverse Engine

Een geavanceerde applicatie voor het zoeken, analyseren en valideren van email-adressen op sociale platforms.

## Architectuur en Structuur

Dit project volgt een 3-lagen architectuur volgens SOLID-principes:

### 1. Data Layer

Verantwoordelijk voor databeheer en persistentie:

- `data_layer/models/`: Datamodellen zoals EmailProfile en EmailValidationResult
- `data_layer/repositories/`: Repository-interfaces en implementaties voor dataopslag
- `data_layer/sources/`: Databronnen voor externe informatie

### 2. Service Layer

Implementeert de business logica:

- `service_layer/controllers/`: Controllers voor orchestratie van businessoperaties
- `service_layer/email_service.py`: Servicelaag voor emailvalidatie en -verwerking
- `service_layer/search_service.py`: Servicelaag voor zoekoperaties
- `service_layer/analyzers/`: Analytische componenten voor dataverwerking
- `service_layer/scrapers/`: Web scraping functionaliteit

### 3. Presentation Layer

Implementeert de gebruikersinterface:

- `web_layer/gui/`: PyQt5-gebaseerde GUI componenten
- `web_layer/api/`: REST API voor externe toegang
- `web_layer/cli/`: Command-line interface

### 4. Core

Algemene functionaliteit:

- `core/config_manager.py`: Configuratiebeheer
- `core/email_validation_service.py`: Factory voor emailvalidatieservices

## SOLID Principes

1. **Single Responsibility Principle**: Elke klasse heeft één verantwoordelijkheid
2. **Open/Closed Principle**: Open voor uitbreiding, gesloten voor wijziging
3. **Liskov Substitution Principle**: Subtypes zijn verwisselbaar met hun basis
4. **Interface Segregation Principle**: Specifieke interfaces in plaats van algemene
5. **Dependency Inversion Principle**: Afhankelijk van abstracties, niet implementaties

## Gebruik

### Installatie

```bash
# Clone de repository
git clone https://github.com/yourusername/email_reverse_engine.git
cd email_reverse_engine

# Installeer dependencies
pip install -r requirements.txt
```

### Opstarten

```bash
# Start de applicatie (GUI)
python start_app.py

# Start in command-line modus
python start_app.py --no-gui

# Start met aangepaste configuratie
python start_app.py --config my_config.yaml
```

## Features

- Email validatie met diverse checks (syntax, MX records, wegwerp-emails)
- Zoeken naar email profielen op sociale platforms
- Caching van zoekresultaten voor snelle herhaalde queries
- Visualisatie van zoekresultaten
- Exportmogelijkheden voor rapportage

## Ontwikkeling

### Tests uitvoeren

```bash
# Alle tests uitvoeren
python -m unittest discover src/tests

# Specifieke test uitvoeren
python -m src.tests.test_service_layer_email_controller
```

### Code-structuur behouden

Nieuwe code moet de bestaande architectuur volgen:
- Datamodellen in data_layer
- Business logica in service_layer
- UI componenten in web_layer

Interface-first ontwikkeling toepassen voor betere testbaarheid.

## Licentie

Dit project is beschikbaar onder [licentie informatie invoegen]. 