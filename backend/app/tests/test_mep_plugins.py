import pytest
import json
import os
from unittest.mock import patch, MagicMock

from app.plugins.mep.electrical_plugin import ElectricalSystemsPlugin
from app.plugins.mep.plumbing_plugin import PlumbingSystemsPlugin
from app.plugins.mep.hvac_plugin import HVACSystemsPlugin
from app.plugins.registry import get_plugin_by_id

# Sample test document text
SAMPLE_TEXT = """
ELECTRICAL SPECIFICATIONS:
- Service: 1000A, 480V/277V, 3-phase, 4-wire
- Main Distribution: Panel MDP-1, 1000A, 480V/277V
- Lighting: LED lighting fixtures with dimming controls, total of 200 fixtures
- Power: GFCI receptacles in all wet locations, standard receptacles in offices
- Low Voltage: Cat6 data cabling, security system with card readers, fire alarm system
- Emergency: 150kW diesel generator for emergency power

PLUMBING SPECIFICATIONS:
- Domestic Water: Copper piping, 3" main, 40-80 PSI, with recirculation for hot water
- Sanitary: Cast iron piping, 6" main, with floor drains in mechanical rooms
- Fixtures: 20 toilets, 15 urinals, 25 lavatories, 5 showers, 3 drinking fountains
- Water Heating: Gas-fired water heater, 100-gallon capacity, 199,000 BTU

HVAC SPECIFICATIONS:
- Heating: Two hot water boilers, 2,000 MBH each, natural gas-fired
- Cooling: Water-cooled chiller, 300 tons, R-134a refrigerant
- Air Handling: Four AHUs, 15,000 CFM each, VAV system
- Ventilation: Energy recovery ventilator for exhaust/makeup air, 5,000 CFM
- Ductwork: Galvanized steel, insulated where required
- Controls: BMS with DDC controls, BACnet protocol
"""

@pytest.mark.asyncio
async def test_electrical_plugin_analyze():
    """Test the electrical plugin analysis capability."""
    plugin = ElectricalSystemsPlugin()
    
    # Mock the OpenAI API call
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "electrical_service": {
            "size": "1000A",
            "voltage": "480V/277V",
            "phases": "3-phase"
        },
        "distribution": [
            {
                "type": "panel",
                "rating": "1000A",
                "location": "main electrical room"
            }
        ],
        "lighting": [
            {
                "type": "LED",
                "quantity": 200,
                "control_type": "dimming"
            }
        ]
    })
    
    with patch("openai.ChatCompletion.create", return_value=mock_response):
        result = await plugin.analyze(SAMPLE_TEXT)
    
    # Check if analysis was successful
    assert "electrical_service" in result
    assert result["electrical_service"]["size"] == "1000A"
    assert "distribution" in result
    assert len(result["distribution"]) == 1
    assert "lighting" in result
    assert result["lighting"][0]["quantity"] == 200

@pytest.mark.asyncio
async def test_plumbing_plugin_analyze():
    """Test the plumbing plugin analysis capability."""
    plugin = PlumbingSystemsPlugin()
    
    # Mock the OpenAI API call
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "water_supply": {
            "domestic_cold": {
                "pipe_material": "copper",
                "main_size": "3\""
            },
            "domestic_hot": {
                "recirculation": True
            }
        },
        "fixtures": [
            {
                "type": "toilet",
                "quantity": 20
            },
            {
                "type": "urinal",
                "quantity": 15
            }
        ]
    })
    
    with patch("openai.ChatCompletion.create", return_value=mock_response):
        result = await plugin.analyze(SAMPLE_TEXT)
    
    # Check if analysis was successful
    assert "water_supply" in result
    assert result["water_supply"]["domestic_cold"]["pipe_material"] == "copper"
    assert "fixtures" in result
    assert len(result["fixtures"]) == 2
    assert result["fixtures"][0]["quantity"] == 20

@pytest.mark.asyncio
async def test_hvac_plugin_analyze():
    """Test the HVAC plugin analysis capability."""
    plugin = HVACSystemsPlugin()
    
    # Mock the OpenAI API call
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "heating_systems": [
            {
                "type": "boiler",
                "capacity": "2,000 MBH",
                "fuel": "natural gas",
                "quantity": 2
            }
        ],
        "cooling_systems": [
            {
                "type": "chiller",
                "capacity": "300 tons",
                "refrigerant": "R-134a"
            }
        ],
        "air_handling": [
            {
                "type": "AHU",
                "cfm": "15,000 CFM",
                "quantity": 4
            }
        ]
    })
    
    with patch("openai.ChatCompletion.create", return_value=mock_response):
        result = await plugin.analyze(SAMPLE_TEXT)
    
    # Check if analysis was successful
    assert "heating_systems" in result
    assert result["heating_systems"][0]["capacity"] == "2,000 MBH"
    assert "cooling_systems" in result
    assert result["cooling_systems"][0]["capacity"] == "300 tons"
    assert "air_handling" in result
    assert result["air_handling"][0]["cfm"] == "15,000 CFM"

def test_plugin_registry():
    """Test that the plugins are correctly registered."""
    electrical_plugin = get_plugin_by_id("mep.electrical_systems")
    plumbing_plugin = get_plugin_by_id("mep.plumbing_systems")
    hvac_plugin = get_plugin_by_id("mep.hvac_systems")
    
    assert electrical_plugin is not None
    assert electrical_plugin.__name__ == "ElectricalSystemsPlugin"
    
    assert plumbing_plugin is not None
    assert plumbing_plugin.__name__ == "PlumbingSystemsPlugin"
    
    assert hvac_plugin is not None
    assert hvac_plugin.__name__ == "HVACSystemsPlugin"

def test_plugin_metadata():
    """Test that the plugins have the correct metadata."""
    electrical_plugin = ElectricalSystemsPlugin()
    plumbing_plugin = PlumbingSystemsPlugin()
    hvac_plugin = HVACSystemsPlugin()
    
    # Check electrical plugin metadata
    assert electrical_plugin.id == "mep.electrical_systems"
    assert electrical_plugin.name == "Electrical Systems Estimator"
    assert electrical_plugin.category == "mep"
    assert electrical_plugin.price == 199.0
    
    # Check plumbing plugin metadata
    assert plumbing_plugin.id == "mep.plumbing_systems"
    assert plumbing_plugin.name == "Plumbing Systems Estimator"
    assert plumbing_plugin.category == "mep"
    assert plumbing_plugin.price == 199.0
    
    # Check HVAC plugin metadata
    assert hvac_plugin.id == "mep.hvac_systems"
    assert hvac_plugin.name == "HVAC & Mechanical Estimator"
    assert hvac_plugin.category == "mep"
    assert hvac_plugin.price == 249.0
