# GTFS Ontology

A comprehensive RDF/OWL ontology for the [General Transit Feed Specification (GTFS)](https://gtfs.org/). This project provides a semantic representation of GTFS static schedule data, enabling graph-based analysis, validation, and querying of public transit data.

## Features

- **Complete GTFS Coverage**: Mappings for all standard GTFS `schedule.txt` tables including `agency`, `stops`, `routes`, `trips`, `stop_times`, Fares V2, and more.
- **SHACL Validation**: Built-in SHACL shapes to enforce GTFS constraints, data types, and enumerations (e.g., `route_type`, `pickup_type`).
- **Multilingual Support**: Ontology labels and comments provided in multiple languages via an overlay pattern:
  - English (`en`)
  - Spanish (`es`)
  - Portuguese (`pt`)
- **Semantic Linking**: Uses Object Properties to strictly link entities (e.g., `gtfs:route` links a `Trip` to a `Route`), improving upon simple foreign key strings.

## Project Structure

```
├── assets/             # Reference materials (e.g., GTFS spec markdown)
├── docs/               # Generated HTML documentation (Ontospy)
├── ontologies/         # Ontology source files
│   ├── schedule.ttl    # Core structure and SHACL shapes
│   └── i18n/           # Localization overlays
│       ├── en.ttl
│       ├── es.ttl
│       └── pt.ttl
├── main.py             # Script to generate documentation
└── README.md
```

## Getting Started

### Prerequisites

- [Python 3.12+](https://www.python.org/) & [uv](https://github.com/astral-sh/uv) (for generating docs)

### Generating Documentation

We use [Ontospy](https://github.com/lambdamusic/Ontospy) to generate static HTML documentation for the ontology.

1.  **Install dependencies and run**:
    ```bash
    uv run python main.py
    ```

2.  **View Docs**:
    Open `docs/index.html` in your web browser.

## Namespace

- **Prefix**: `gtfs`
- **URI**: `http://ontology.gtfs.org/reference#`

```turtle
@prefix gtfs: <http://ontology.gtfs.org/reference#> .
```

## Contributing

### Adding a New Language
1.  Create a new `.ttl` file in `ontologies/i18n/` (e.g., `fr.ttl`).
2.  Add `rdfs:label` and `rdfs:comment` annotations for existing classes and properties using the new language tag (e.g., `@fr`).
3.  Register the new file in `main.py` to include it in documentation generation.

### Modifying the Ontology
- Edit `ontologies/schedule.ttl` to add classes, properties, or SHACL shapes.
- Verify changes by regenerating documentation.
