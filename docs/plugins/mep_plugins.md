# MEP Plugins Documentation

## Overview

The MEP (Mechanical, Electrical, Plumbing) plugins are specialized components designed to analyze building specifications and extract structured data about MEP systems. These plugins can process plain text specifications, drawings, or other construction documents to identify key components, parameters, and requirements.

## Available Plugins

### 1. Electrical Systems Estimator (`mep.electrical_systems`)

This plugin analyzes electrical specifications and extracts structured data about electrical systems, including:

- Electrical service details (size, voltage, phases)
- Distribution equipment (panels, switchgear)
- Lighting systems (types, quantities, controls)
- Power systems (receptacles, circuits)
- Low voltage systems (data, security, fire alarm)
- Emergency power systems

**Price**: $199.00

### 2. Plumbing Systems Estimator (`mep.plumbing_systems`)

This plugin analyzes plumbing specifications and extracts structured data about plumbing systems, including:

- Domestic water supply (pipe materials, sizes, pressure)
- Sanitary systems (pipe materials, sizes)
- Fixtures (types, quantities)
- Water heating systems (type, capacity, fuel)

**Price**: $199.00

### 3. HVAC & Mechanical Estimator (`mep.hvac_systems`)

This plugin analyzes HVAC and mechanical specifications and extracts structured data about these systems, including:

- Heating systems (boilers, furnaces, capacity, fuel)
- Cooling systems (chillers, condensers, capacity, refrigerant)
- Air handling units (types, CFM, quantity)
- Ventilation systems (energy recovery, makeup air)
- Ductwork (materials, insulation)
- Control systems (BMS, DDC, protocols)

**Price**: $249.00

## Usage

All MEP plugins implement a common interface with the following methods:

### `analyze(text: str) -> dict`

Analyzes the provided text and returns a structured dictionary containing the extracted MEP system data.

```python
from app.plugins.registry import get_plugin_by_id

# Get the plugin instance
plugin = get_plugin_by_id("mep.electrical_systems")

# Analyze a specification document
result = await plugin.analyze(specification_text)

# Process the structured output
print(result["electrical_service"]["size"])  # Example: "1000A"
```

## Integration

MEP plugins can be integrated with other platform features:

- Cost estimation based on extracted components
- Automated specification checking
- BIM model integration
- Energy usage calculations
- Regulatory compliance verification

## Error Handling

If the plugin cannot extract valid data from the provided text, it will return an appropriate error message in the result dictionary. Always check for error keys in the returned data.
