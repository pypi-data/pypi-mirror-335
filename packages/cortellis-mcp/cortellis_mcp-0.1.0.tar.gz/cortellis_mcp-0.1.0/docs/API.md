# Cortellis MCP API Reference

## Functions

### search_drugs

```python
def search_drugs(
    query: str = None,
    company: str = None,
    indication: str = None,
    action: str = None,
    phase: str = None,
    phase_terminated: str = None,
    technology: str = None,
    drug_name: str = None,
    country: str = None,
    offset: int = 0
) -> dict
```

Search for drugs in the Cortellis database.

#### Parameters:
- `query`: Raw search query (optional)
- `company`: Company developing the drug
- `indication`: Active indications (e.g., "obesity")
- `action`: Target specific action (e.g., "glucagon")
- `phase`: Overall highest development status
- `phase_terminated`: Last phase before NDR/Discontinued
- `technology`: Technologies used (e.g., "small molecule")
- `drug_name`: Name of the drug
- `country`: Country of development
- `offset`: Starting position in results (default: 0)

#### Returns:
Dictionary containing search results and metadata.

### explore_ontology

```python
def explore_ontology(
    term: str = None,
    category: str = None,
    action: str = None,
    indication: str = None,
    company: str = None,
    drug_name: str = None,
    target: str = None,
    technology: str = None
) -> dict
```

Explore ontology/taxonomy terms in the Cortellis database.

#### Parameters:
- `term`: Generic search term
- `category`: Category to search within
- `action`: Target specific action
- `indication`: Active indications
- `company`: Company name
- `drug_name`: Drug name
- `target`: Drug target
- `technology`: Technology type

#### Returns:
Dictionary containing matching ontology terms. 