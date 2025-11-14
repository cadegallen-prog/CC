#!/usr/bin/env python3
"""
Product Classification System
Identifies what each product actually IS (e.g., "LED bulb", "ceiling fan", "drill bit")
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class ProductClassifier:
    """
    Identifies product types by analyzing multiple signals:
    - Title keywords
    - Description keywords
    - Technical specifications
    - Product domains
    - Brand patterns
    """

    def __init__(self):
        # Define product type patterns with keywords and confidence weights
        # Each pattern has: keywords (strong indicators), weak keywords (supporting evidence), and domain hints

        self.patterns = {
            # LIGHTING PRODUCTS
            'LED Light Bulb': {
                'strong_keywords': ['light bulb', 'led bulb', 'lamp bulb', 'bulb soft white', 'bulb daylight', 'led light', 'led lamp', 'led tube'],
                'weak_keywords': ['watt equivalent', 'lumens', 'kelvin', 'dimmable', 'a19', 'a21', 'br30', 'par38', 'e26', 'e12', 'b10', 'candelabra'],
                'description_hints': ['watt equivalent', 'color temperature', 'soft white', 'daylight', 'cri', 'bulbs for', 'bulbs take', 'led bulbs'],
                'spec_indicators': {'wattage', 'lumens', 'color_temp', 'base_type', 'dimmable'},
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['sconce', 'pendant', 'fixture', 'wall mount', 'ceiling mount'],
                'spec_boost': True  # Boost score if has bulb-specific specs
            },

            'Ceiling Fan': {
                'strong_keywords': ['ceiling fan', 'indoor ceiling fan', 'outdoor ceiling fan'],
                'weak_keywords': ['blade', 'cfm', 'airflow', 'remote control', 'reversible'],
                'description_hints': ['air circulation', 'ceiling mount', 'fan blades'],
                'spec_indicators': {'fan_blades', 'cfm', 'airflow'},
                'domains': ['hvac', 'lighting', 'electrical'],
                'negative_keywords': ['exhaust', 'bathroom fan', 'range hood']
            },

            'Pendant Light': {
                'strong_keywords': ['pendant light', 'mini-pendant', 'mini pendant', 'pendant with', 'light pendant'],
                'weak_keywords': ['hanging', 'suspension', 'chain', 'adjustable height', 'glass shade', 'metal strap'],
                'description_hints': ['hanging light', 'ceiling mounted', 'decorative lighting', 'pendant is', 'pendant features'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['light bulb']
            },

            'Chandelier': {
                'strong_keywords': ['chandelier', 'light chandelier'],
                'weak_keywords': ['candelabra', 'crystal', 'arms', 'tiered', 'hanging'],
                'description_hints': ['elegant lighting', 'dining room', 'foyer', 'chandelier features'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['light bulb', 'led bulb', 'bulb soft', 'bulb daylight']
            },

            'Recessed Light': {
                'strong_keywords': ['recessed', 'recessed light', 'recessed lighting', 'can light', 'canless', 'downlight'],
                'weak_keywords': ['retrofit', 'slim', 'baffle', 'trim kit', 'color selectable'],
                'description_hints': ['ceiling recess', 'integrated led', 'housing'],
                'spec_indicators': {'dimmable', 'color_temp'},
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'Wall Sconce': {
                'strong_keywords': ['sconce', 'wall sconce', 'wall light', 'vanity sconce', 'sconce light'],
                'weak_keywords': ['wall mount', 'vanity light', 'bath light', 'arm', 'shade', 'glass shade', 'mid-century', 'brushed', 'accent lighting'],
                'description_hints': ['wall mounted', 'bathroom lighting', 'decorative wall', 'sconce features', 'wall fixture', 'wall-mounted light', 'sconce is', 'sconces are'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['switch', 'outlet', 'plate']
            },

            'Track Lighting': {
                'strong_keywords': ['track light', 'track lighting', 'track head'],
                'weak_keywords': ['track system', 'rail', 'adjustable head'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'Flush Mount Light': {
                'strong_keywords': ['flush mount', 'semi-flush', 'semi flush'],
                'weak_keywords': ['close to ceiling', 'low profile', 'integrated led'],
                'description_hints': ['ceiling mounted', 'flush to ceiling', 'mount fixture'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['light bulb', 'recessed light', 'ceiling fan']
            },

            'Landscape Lighting': {
                'strong_keywords': ['landscape light', 'landscape lighting', 'flood light', 'outdoor flood', 'pathway light', 'yard light'],
                'weak_keywords': ['low voltage', 'outdoor', 'waterproof', 'ip65', 'ground stake', 'spotlight'],
                'description_hints': ['outdoor lighting', 'landscape', 'garden', 'pathway', 'yard lighting'],
                'spec_indicators': {'waterproof', 'outdoor_rated'},
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'Troffer Light': {
                'strong_keywords': ['troffer', 'troffer light', 'troffer lighting'],
                'weak_keywords': ['drop ceiling', 'suspended ceiling', 'commercial', 'office lighting'],
                'description_hints': ['commercial lighting', 'office light', 'ceiling grid'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'High Bay Light': {
                'strong_keywords': ['high bay', 'high bay light', 'high bay lighting', 'highbay'],
                'weak_keywords': ['warehouse', 'commercial', 'industrial', 'shop light', 'lumen', 'integrated led'],
                'description_hints': ['warehouse lighting', 'industrial lighting', 'commercial lighting', 'high ceilings', 'mounting height'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'Flashlight': {
                'strong_keywords': ['flashlight', 'flash light', 'handheld light', 'portable light', 'tactical light'],
                'weak_keywords': ['lumens', 'beam', 'rechargeable', 'battery', 'alkaline', 'led light', 'handheld'],
                'description_hints': ['handheld', 'portable lighting', 'beam distance', 'runtime'],
                'domains': ['tools', 'lighting'],
                'negative_keywords': []
            },

            'String Lights': {
                'strong_keywords': ['string light', 'string lights', 'cafe lights', 'bistro lights', 'edison string'],
                'weak_keywords': ['outdoor', 'indoor', 'weatherproof', 'linkable', 'plug-in', 'solar'],
                'description_hints': ['decorative lighting', 'outdoor entertaining', 'patio', 'string of lights'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': ['light bulb', 'led bulb', 'lamp bulb']
            },

            'Shop Light': {
                'strong_keywords': ['shop light', 'work light', 'utility light', 'garage light', 'led shop light'],
                'weak_keywords': ['linkable', 'pull chain', 'integrated led', 'flush mount', 'workshop'],
                'description_hints': ['garage lighting', 'workshop', 'utility area', 'work area'],
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            # ELECTRICAL PRODUCTS
            'Circuit Breaker': {
                'strong_keywords': ['breaker', 'circuit breaker', 'gfci breaker', 'afci breaker'],
                'weak_keywords': ['amp', 'pole', 'ground fault', 'arc fault', 'thermal magnetic'],
                'description_hints': ['electrical panel', 'overcurrent protection', 'circuit protection'],
                'spec_indicators': {'amperage', 'voltage'},
                'domains': ['electrical'],
                'negative_keywords': []
            },

            'Light Switch': {
                'strong_keywords': ['light switch', 'dimmer switch', 'rocker switch', 'toggle switch', 'wall switch'],
                'weak_keywords': ['gang', 'way', '3-way', '4-way', 'decorator', 'switch'],
                'description_hints': ['wall switch', 'control lighting'],
                'domains': ['electrical', 'lighting'],
                'negative_keywords': ['breaker', 'outlet', 'receptacle', 'light bulb', 'led bulb', 'led light', 'lamp', 'flashlight', 'string light']
            },

            'Electrical Outlet': {
                'strong_keywords': ['outlet', 'receptacle', 'gfci outlet', 'usb outlet', 'usb charger', 'in-wall charger'],
                'weak_keywords': ['duplex', 'tamper resistant', 'grounded', 'usb', 'type a', 'type c'],
                'description_hints': ['wall outlet', 'power receptacle', 'usb charging', 'charger devices'],
                'domains': ['electrical'],
                'negative_keywords': ['switch', 'breaker', 'cover plate']
            },

            'Wall Plate': {
                'strong_keywords': ['wall plate', 'cover plate', 'switch plate', 'outlet cover'],
                'weak_keywords': ['decorator', 'gang', 'screwless'],
                'description_hints': ['switch cover', 'outlet cover'],
                'domains': ['electrical'],
                'negative_keywords': []
            },

            'Extension Cord': {
                'strong_keywords': ['extension cord', 'power cord'],
                'weak_keywords': ['gauge', 'feet', 'indoor', 'outdoor', 'grounded'],
                'description_hints': ['electrical cord', 'power extension'],
                'domains': ['electrical'],
                'negative_keywords': []
            },

            # PLUMBING PRODUCTS
            'Faucet': {
                'strong_keywords': ['faucet', 'kitchen faucet', 'bathroom faucet', 'lavatory faucet'],
                'weak_keywords': ['spout', 'handle', 'pulldown', 'pullout', 'spray', 'gpm'],
                'description_hints': ['water flow', 'sink faucet', 'deck mount'],
                'spec_indicators': {'flow_rate', 'gpm'},
                'domains': ['plumbing'],
                'negative_keywords': ['showerhead', 'toilet', 'drain']
            },

            'Faucet Part': {
                'strong_keywords': ['valve stem', 'faucet cartridge', 'faucet stem', 'stem assembly'],
                'weak_keywords': ['replacement', 'assembly', 'ceramic disc', 'repair'],
                'description_hints': ['faucet repair', 'replacement part', 'valve assembly'],
                'domains': ['plumbing'],
                'negative_keywords': []
            },

            'Showerhead': {
                'strong_keywords': ['showerhead', 'shower head', 'rain shower', 'handheld shower'],
                'weak_keywords': ['spray', 'gpm', 'rainfall', 'jets'],
                'description_hints': ['shower system', 'water spray'],
                'spec_indicators': {'flow_rate', 'gpm'},
                'domains': ['plumbing'],
                'negative_keywords': ['faucet']
            },

            'Toilet': {
                'strong_keywords': ['toilet', 'commode', 'water closet'],
                'weak_keywords': ['elongated', 'round', 'flush', 'gpf', 'seat', 'bowl'],
                'description_hints': ['bathroom fixture', 'water closet'],
                'domains': ['plumbing'],
                'negative_keywords': ['seat only', 'tank only']
            },

            'Toilet Seat': {
                'strong_keywords': ['toilet seat'],
                'weak_keywords': ['elongated', 'round', 'soft close', 'bidet'],
                'description_hints': ['seat replacement', 'toilet accessory'],
                'domains': ['plumbing'],
                'negative_keywords': []
            },

            'Sink': {
                'strong_keywords': ['sink', 'bathroom sink', 'kitchen sink', 'utility sink', 'vessel sink', 'drop-in sink', 'undermount sink'],
                'weak_keywords': ['basin', 'bowl', 'undermount', 'drop-in', 'farmhouse', 'stainless steel', 'gauge'],
                'description_hints': ['wash basin', 'kitchen sink', 'bathroom sink'],
                'domains': ['plumbing'],
                'negative_keywords': ['drain assembly', 'drain only', 'faucet only']
            },

            'Vanity Top': {
                'strong_keywords': ['vanity top', 'countertop', 'cultured marble top'],
                'weak_keywords': ['bathroom vanity', 'sink top', 'integrated sink'],
                'description_hints': ['bathroom counter', 'vanity surface'],
                'domains': ['plumbing'],
                'negative_keywords': ['vanity cabinet', 'only cabinet']
            },

            'Bathtub': {
                'strong_keywords': ['bathtub', 'bath tub', 'soaking tub', 'alcove tub'],
                'weak_keywords': ['acrylic', 'fiberglass', 'freestanding'],
                'description_hints': ['bathroom tub', 'bathing'],
                'domains': ['plumbing'],
                'negative_keywords': []
            },

            'Drain': {
                'strong_keywords': ['drain', 'sink drain', 'tub drain', 'shower drain'],
                'weak_keywords': ['pop-up', 'strainer', 'stopper', 'tailpiece'],
                'description_hints': ['drain assembly', 'water drain'],
                'domains': ['plumbing'],
                'negative_keywords': []
            },

            'Water Heater': {
                'strong_keywords': ['water heater', 'tankless water heater'],
                'weak_keywords': ['gallon', 'gpm', 'gas', 'electric', 'thermal'],
                'description_hints': ['hot water', 'heating water'],
                'domains': ['plumbing', 'hvac'],
                'negative_keywords': []
            },

            # HVAC PRODUCTS
            'Thermostat': {
                'strong_keywords': ['thermostat', 'programmable thermostat', 'smart thermostat'],
                'weak_keywords': ['temperature control', 'wifi', 'digital'],
                'description_hints': ['climate control', 'heating cooling'],
                'domains': ['hvac', 'electrical'],
                'negative_keywords': []
            },

            'Exhaust Fan': {
                'strong_keywords': ['exhaust fan', 'bathroom fan', 'ventilation fan'],
                'weak_keywords': ['cfm', 'sone', 'ventilation'],
                'description_hints': ['air exhaust', 'bathroom ventilation'],
                'domains': ['hvac', 'electrical'],
                'negative_keywords': ['ceiling fan']
            },

            'Range Hood': {
                'strong_keywords': ['range hood', 'vent hood', 'kitchen hood'],
                'weak_keywords': ['cfm', 'ducted', 'ductless', 'stove vent'],
                'description_hints': ['kitchen ventilation', 'cooking exhaust'],
                'domains': ['hvac'],
                'negative_keywords': []
            },

            'HVAC Air Filter': {
                'strong_keywords': ['air filter', 'furnace filter', 'hvac filter', 'replacement filter', 'pleated filter'],
                'weak_keywords': ['merv', 'fpr', 'filtration', 'allergen', 'fiberglass', 'pleated'],
                'description_hints': ['indoor air quality', 'dust', 'filter replacement', 'air filtration'],
                'domains': ['hvac'],
                'negative_keywords': ['water filter', 'oil filter', 'vacuum filter']
            },

            # DOOR HARDWARE
            'Door Knob': {
                'strong_keywords': ['door knob', 'knob', 'doorknob'],
                'weak_keywords': ['passage', 'privacy', 'dummy', 'handle', 'lever'],
                'description_hints': ['door handle', 'door hardware'],
                'domains': [],
                'negative_keywords': ['hinge', 'lock only']
            },

            'Door Handle': {
                'strong_keywords': ['door handle', 'lever', 'door lever'],
                'weak_keywords': ['passage', 'privacy', 'dummy', 'handle set'],
                'description_hints': ['door hardware', 'lever handle'],
                'domains': [],
                'negative_keywords': ['knob', 'hinge']
            },

            'Door Lock': {
                'strong_keywords': ['door lock', 'deadbolt', 'smart lock', 'keyless entry'],
                'weak_keywords': ['keyed', 'keypad', 'electronic', 'grade'],
                'description_hints': ['door security', 'locking mechanism'],
                'domains': [],
                'negative_keywords': ['knob only', 'handle only']
            },

            'Door Hinge': {
                'strong_keywords': ['hinge', 'door hinge'],
                'weak_keywords': ['pin', 'removable', 'spring'],
                'description_hints': ['door hardware'],
                'domains': [],
                'negative_keywords': []
            },

            # TOOLS & HARDWARE
            'Drill Bit': {
                'strong_keywords': ['drill bit', 'bit set', 'driver bit'],
                'weak_keywords': ['titanium', 'cobalt', 'impact rated', 'philips', 'torx'],
                'description_hints': ['drilling', 'screw driving'],
                'domains': ['tools'],
                'negative_keywords': ['drill only', 'saw']
            },

            'Specialty Cutter': {
                'strong_keywords': ['rebar cutter', 'bolt cutter', 'wire cutter', 'cable cutter', 'tile cutter'],
                'weak_keywords': ['sds', 'sds-plus', 'cutting', 'hardened steel', 'reinforced'],
                'description_hints': ['cutting rebar', 'cutting wire', 'specialty cutting'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Drill': {
                'strong_keywords': ['drill', 'cordless drill', 'hammer drill', 'impact driver'],
                'weak_keywords': ['volt', 'battery', 'chuck', 'brushless'],
                'description_hints': ['power tool', 'drilling tool'],
                'domains': ['tools'],
                'negative_keywords': ['bit only', 'accessory']
            },

            'Saw': {
                'strong_keywords': ['saw', 'circular saw', 'miter saw', 'jigsaw', 'reciprocating saw', 'table saw'],
                'weak_keywords': ['blade', 'teeth', 'cutting'],
                'description_hints': ['cutting tool'],
                'domains': ['tools'],
                'negative_keywords': ['blade only']
            },

            'Saw Blade': {
                'strong_keywords': ['saw blade', 'blade', 'cutting blade'],
                'weak_keywords': ['teeth', 'tpi', 'carbide', 'diameter'],
                'description_hints': ['replacement blade', 'cutting accessory'],
                'domains': ['tools'],
                'negative_keywords': ['saw only']
            },

            'Screwdriver': {
                'strong_keywords': ['screwdriver', 'screwdriver set'],
                'weak_keywords': ['philips', 'flathead', 'torx', 'precision'],
                'description_hints': ['hand tool', 'screw driving'],
                'domains': ['tools'],
                'negative_keywords': ['bit only', 'drill']
            },

            'Wrench': {
                'strong_keywords': ['wrench', 'socket wrench', 'adjustable wrench', 'torque wrench'],
                'weak_keywords': ['ratchet', 'socket', 'sae', 'metric'],
                'description_hints': ['hand tool', 'fastening'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Hammer': {
                'strong_keywords': ['hammer', 'claw hammer', 'framing hammer'],
                'weak_keywords': ['ounce', 'fiberglass handle', 'steel'],
                'description_hints': ['hand tool', 'striking'],
                'domains': ['tools'],
                'negative_keywords': ['drill']
            },

            'Tape Measure': {
                'strong_keywords': ['tape measure', 'measuring tape'],
                'weak_keywords': ['feet', 'metric', 'retractable', 'blade'],
                'description_hints': ['measuring tool'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Level': {
                'strong_keywords': ['level', 'spirit level', 'torpedo level'],
                'weak_keywords': ['bubble', 'magnetic', 'vial'],
                'description_hints': ['leveling tool', 'measuring tool'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Tool Kit': {
                'strong_keywords': ['tune-up kit', 'tuneup kit', 'maintenance kit', 'repair kit', 'tool kit'],
                'weak_keywords': ['replacement parts', 'chainsaw', 'mower', 'engine', 'service'],
                'description_hints': ['kit includes', 'replacement', 'maintenance'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Fastener': {
                'strong_keywords': ['screw', 'nail', 'bolt', 'nut', 'washer', 'anchor'],
                'weak_keywords': ['pack', 'assortment', 'zinc', 'stainless'],
                'description_hints': ['hardware', 'fastening'],
                'domains': ['tools'],
                'negative_keywords': ['driver', 'wrench', 'drill']
            },

            'Spring': {
                'strong_keywords': ['spring', 'compression spring', 'extension spring'],
                'weak_keywords': ['assortment', 'kit', 'steel'],
                'description_hints': ['hardware', 'mechanical'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            # CLEANING PRODUCTS
            'Cleaning Pad': {
                'strong_keywords': ['sweeping pad', 'cleaning pad', 'mop pad', 'refill'],
                'weak_keywords': ['swiffer', 'dry', 'wet', 'disposable'],
                'description_hints': ['floor cleaning', 'cleaning refill'],
                'domains': [],
                'negative_keywords': ['mop only']
            },

            'Cleaning Solution': {
                'strong_keywords': ['cleaner', 'cleaning solution', 'disinfectant'],
                'weak_keywords': ['spray', 'gallon', 'concentrate'],
                'description_hints': ['cleaning product', 'cleaning agent'],
                'domains': [],
                'negative_keywords': ['pad', 'mop', 'tool']
            },

            # PAINT & SUPPLIES
            'Paint': {
                'strong_keywords': ['paint', 'interior paint', 'exterior paint'],
                'weak_keywords': ['gallon', 'semi-gloss', 'matte', 'eggshell', 'primer'],
                'description_hints': ['wall paint', 'coating'],
                'domains': [],
                'negative_keywords': ['brush', 'roller', 'sprayer']
            },

            'Paint Brush': {
                'strong_keywords': ['paint brush', 'brush'],
                'weak_keywords': ['bristle', 'angled', 'trim'],
                'description_hints': ['painting tool'],
                'domains': ['tools'],
                'negative_keywords': ['paint only']
            },

            'Paint Roller': {
                'strong_keywords': ['paint roller', 'roller cover', 'roller frame'],
                'weak_keywords': ['nap', 'foam', 'painting'],
                'description_hints': ['painting tool', 'roller for paint'],
                'domains': ['tools'],
                'negative_keywords': ['paint only']
            },

            # ADDITIONAL PRODUCTS
            'Wire': {
                'strong_keywords': ['wire', 'electrical wire', 'copper wire', 'thhn wire'],
                'weak_keywords': ['gauge', 'copper', 'stranded', 'solid', 'awg'],
                'description_hints': ['electrical wiring', 'building wire'],
                'domains': ['electrical'],
                'negative_keywords': []
            },

            'Cable': {
                'strong_keywords': ['cable', 'romex', 'electrical cable'],
                'weak_keywords': ['gauge', 'copper', 'jacket', 'nm-b'],
                'description_hints': ['electrical cable', 'building wire'],
                'domains': ['electrical'],
                'negative_keywords': ['extension cord']
            },

            'Tape': {
                'strong_keywords': ['tape', 'duct tape', 'masking tape', 'electrical tape', 'painter tape'],
                'weak_keywords': ['adhesive', 'roll', 'yards', 'width'],
                'description_hints': ['tape for', 'adhesive tape'],
                'domains': [],
                'negative_keywords': ['tape measure']
            },

            'Adhesive': {
                'strong_keywords': ['adhesive', 'glue', 'epoxy', 'construction adhesive'],
                'weak_keywords': ['bond', 'stick', 'tube', 'cartridge'],
                'description_hints': ['bonding', 'sticks to'],
                'domains': [],
                'negative_keywords': ['tape', 'stair', 'nosing', 'trim', 'transition']
            },

            'Plumbing Fitting': {
                'strong_keywords': ['fitting', 'elbow', 'coupling', 'tee', 'push-to-connect', 'backflow preventer', 'check valve'],
                'weak_keywords': ['pvc', 'copper', 'brass', 'compression', 'threaded', 'backflow', 'preventer', 'adapter', 'connector'],
                'description_hints': ['pipe fitting', 'plumbing connection', 'backflow', 'prevent backflow'],
                'domains': ['plumbing'],
                'negative_keywords': ['faucet', 'showerhead', 'toilet', 'electrical', 'usb', 'outlet']
            },

            'Under Cabinet Light': {
                'strong_keywords': ['under cabinet', 'under-cabinet lighting'],
                'weak_keywords': ['linkable', 'led strip', 'puck light'],
                'description_hints': ['cabinet lighting', 'task lighting'],
                'spec_indicators': {'lumens', 'color_temp'},
                'domains': ['lighting', 'electrical'],
                'negative_keywords': []
            },

            'Smoke Detector': {
                'strong_keywords': ['smoke detector', 'smoke alarm', 'carbon monoxide detector'],
                'weak_keywords': ['battery', 'ionization', 'photoelectric', 'alarm'],
                'description_hints': ['fire safety', 'smoke sensing'],
                'domains': [],
                'negative_keywords': []
            },

            'Door': {
                'strong_keywords': ['door panel', 'interior door', 'exterior door', 'barn door', 'bifold door'],
                'weak_keywords': ['prehung', 'slab', 'panel door'],
                'description_hints': ['door slab', 'door system'],
                'domains': [],
                'negative_keywords': ['door knob', 'door handle', 'door lock', 'hinge', 'hardware only']
            },

            'Load Center': {
                'strong_keywords': ['load center', 'panel box', 'breaker panel', 'electrical panel'],
                'weak_keywords': ['circuit', 'space', 'main breaker', 'main lug'],
                'description_hints': ['circuit panel', 'breaker box'],
                'domains': ['electrical'],
                'negative_keywords': []
            },

            'Skylight': {
                'strong_keywords': ['skylight'],
                'weak_keywords': ['curb mount', 'deck mount', 'tempered glass', 'venting'],
                'description_hints': ['roof window', 'natural light'],
                'domains': [],
                'negative_keywords': []
            },

            'Shop Vacuum': {
                'strong_keywords': ['shop vac', 'shop vacuum', 'wet dry vac', 'wet/dry vacuum'],
                'weak_keywords': ['gallon', 'peak hp', 'filter'],
                'description_hints': ['wet and dry', 'vacuum cleaner'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Work Gloves': {
                'strong_keywords': ['work gloves', 'gloves'],
                'weak_keywords': ['nitrile', 'latex', 'leather', 'grip', 'cut resistant'],
                'description_hints': ['hand protection', 'safety gloves'],
                'domains': [],
                'negative_keywords': []
            },

            'Ladder': {
                'strong_keywords': ['ladder', 'step ladder', 'extension ladder', 'multi-position ladder'],
                'weak_keywords': ['feet', 'reach', 'aluminum', 'fiberglass', 'type ia', 'type iaa', 'load capacity'],
                'description_hints': ['climb', 'climbing', 'height access', 'reach height'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Window': {
                'strong_keywords': ['window', 'double-hung window', 'single-hung window', 'casement window', 'sliding window'],
                'weak_keywords': ['low-e', 'glass', 'vinyl', 'wood', 'clad', 'sash', 'insulated glass'],
                'description_hints': ['window features', 'energy efficient', 'window construction'],
                'domains': [],
                'negative_keywords': ['window film', 'window treatment', 'window covering']
            },

            'Bathroom Towel Bar': {
                'strong_keywords': ['towel bar', 'towel rack', 'towel holder', 'towel ring'],
                'weak_keywords': ['brushed nickel', 'chrome', 'bronze', 'bathroom', 'wall mount'],
                'description_hints': ['bathroom accessory', 'bath hardware', 'towel storage'],
                'domains': [],
                'negative_keywords': []
            },

            'Surge Protector': {
                'strong_keywords': ['surge protector', 'surge suppressor', 'power strip'],
                'weak_keywords': ['outlet', 'joules', 'usb', 'protection', 'grounded'],
                'description_hints': ['surge protection', 'electrical protection', 'power outlets'],
                'domains': ['electrical'],
                'negative_keywords': ['extension cord', 'breaker']
            },

            'Safety Respirator': {
                'strong_keywords': ['respirator', 'respirator cartridge', 'vapor cartridge', 'n95', 'p100'],
                'weak_keywords': ['replacement', 'filter', 'organic vapor', 'breathing', 'face mask'],
                'description_hints': ['respiratory protection', 'breathing protection', 'air filter'],
                'domains': [],
                'negative_keywords': []
            },

            'Disposable Earplugs': {
                'strong_keywords': ['earplugs', 'ear plugs', 'hearing protection'],
                'weak_keywords': ['disposable', 'foam', 'nrr', 'noise reduction', 'decibel', 'pack'],
                'description_hints': ['hearing protection', 'noise reduction', 'ear protection'],
                'domains': [],
                'negative_keywords': ['earmuffs']
            },

            'Speaker Mount': {
                'strong_keywords': ['speaker mount', 'speaker bracket', 'bookshelf speaker mount', 'speaker wall mount'],
                'weak_keywords': ['wall mount', 'swivel', 'tilt', 'adjustable', 'audio', 'speakers'],
                'description_hints': ['speaker installation', 'audio mount', 'mount speakers', 'speaker display'],
                'domains': [],
                'negative_keywords': ['light']
            },

            'Curtain Rod': {
                'strong_keywords': ['curtain rod', 'drapery rod', 'window rod'],
                'weak_keywords': ['telescoping', 'finials', 'decorative', 'adjustable', 'double rod'],
                'description_hints': ['window treatment', 'curtain hanging', 'drapery hardware'],
                'domains': [],
                'negative_keywords': []
            },

            'Shelf Bracket': {
                'strong_keywords': ['shelf bracket', 'bracket'],
                'weak_keywords': ['decorative', 'support', 'mounting', 'steel', 'nickel'],
                'description_hints': ['shelf support', 'shelving', 'wall bracket'],
                'domains': ['hardware'],
                'negative_keywords': ['speaker bracket', 'light bracket']
            },

            'Radon Detector': {
                'strong_keywords': ['radon detector', 'radon monitor', 'radon sensor'],
                'weak_keywords': ['battery', 'smart', 'digital', 'lung cancer'],
                'description_hints': ['radon monitoring', 'air quality', 'indoor air'],
                'domains': [],
                'negative_keywords': []
            },

            'Paint Sprayer': {
                'strong_keywords': ['paint sprayer', 'hvlp sprayer', 'airless sprayer', 'spray gun'],
                'weak_keywords': ['hvlp', 'psi', 'gpm', 'nozzle', 'spray pattern'],
                'description_hints': ['spray painting', 'paint application', 'finishing'],
                'domains': ['tools'],
                'negative_keywords': ['spray paint', 'paint can']
            },

            'Window Shade': {
                'strong_keywords': ['window shade', 'roller shade', 'solar shade', 'outdoor shade'],
                'weak_keywords': ['cordless', 'light filtering', 'blackout', 'uv protection'],
                'description_hints': ['window covering', 'sun protection', 'privacy'],
                'domains': [],
                'negative_keywords': []
            },

            'Metal Folding Tool': {
                'strong_keywords': ['folding tool', 'sheet metal folder', 'bending tool'],
                'weak_keywords': ['seam', 'bend', 'metal', 'hvac'],
                'description_hints': ['metal fabrication', 'sheet metal', 'folding seam'],
                'domains': ['tools'],
                'negative_keywords': []
            },

            'Shower Pan': {
                'strong_keywords': ['shower pan', 'shower base', 'shower tray'],
                'weak_keywords': ['alcove', 'acrylic', 'fiberglass', 'threshold'],
                'description_hints': ['shower floor', 'shower receptor'],
                'domains': ['plumbing'],
                'negative_keywords': []
            },

            'Voltage Tester': {
                'strong_keywords': ['voltage tester', 'non-contact voltage', 'electrical tester'],
                'weak_keywords': ['volt', 'detect', 'test', 'led'],
                'description_hints': ['voltage detection', 'electrical testing'],
                'domains': ['electrical', 'tools'],
                'negative_keywords': []
            },
        }

    def normalize_text(self, text: str) -> str:
        """
        Convert text to lowercase and remove extra spaces
        Handles non-string inputs gracefully by converting to string first
        """
        if not text:
            return ""

        # Handle non-string inputs gracefully
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return ""

        return " ".join(text.lower().split())

    def contains_keyword(self, text: str, keyword: str) -> bool:
        """
        Check if keyword exists in text with word boundary awareness
        Prevents false matches like 'brush' matching 'brushed nickel'
        """
        # For multi-word keywords, just check if they're in the text
        if ' ' in keyword:
            return keyword in text

        # For single words, check word boundaries
        # Add spaces around text to catch start/end matches
        padded_text = ' ' + text + ' '

        # Check if keyword appears with word boundaries
        import re
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, padded_text))

    def is_false_positive_block(self, text: str, negative_kw: str, pattern: Dict, location: str = 'title') -> bool:
        """
        Determine if negative keyword match is a false positive.
        Returns True if we should NOT block (false positive detected).

        Context-aware analysis to distinguish:
        - USE CASE mentions ("bulb for chandelier") from PRODUCT TYPE ("chandelier fixture")
        - MODIFIERS ("chandelier bulb") from HEAD NOUNS ("chandelier with bulbs")
        - INTEGRATED COMPONENTS ("faucet with drain") from STANDALONE PRODUCTS
        """

        # Rule 0: Check if negative keyword has a MODIFIER before it
        # Pattern: "chandelier led light bulb" - "chandelier" modifies "light bulb"
        # This catches cases where the negative keyword IS the product type, not a disqualifier

        # Common modifiers that appear before product type keywords
        fixture_modifiers = ['chandelier', 'pendant', 'sconce', 'ceiling fan', 'track', 'vanity']
        use_case_modifiers = ['replacement', 'compatible', 'accessory', 'for use']

        # Check if any modifier appears before the negative keyword
        for modifier in fixture_modifiers + use_case_modifiers:
            # Pattern: "[modifier] ... [negative_kw]"
            # e.g., "chandelier led light bulb" where "chandelier" modifies "light bulb"
            if modifier in text:
                # Find positions
                mod_pos = text.find(modifier)
                neg_pos = text.find(negative_kw)

                if mod_pos < neg_pos:
                    # Modifier comes before negative keyword
                    # Check if they're close (within 5 words)
                    between_text = text[mod_pos:neg_pos]
                    word_count = len(between_text.split())

                    if word_count <= 6:  # Close enough to be related
                        return True  # False positive - modifier + product type

        # Rule 1: Strong Keyword After Negative Keyword (Compound Product Names)
        # Pattern: "chandelier led light bulb" - "chandelier" modifies "led light bulb"
        for strong_kw in pattern.get('strong_keywords', []):
            # Direct adjacency: "chandelier bulb"
            if f"{negative_kw} {strong_kw}" in text:
                return True  # False positive - don't block

            # With one intervening word: "chandelier led bulb"
            # Split and check if strong keyword appears within 3 words after negative keyword
            words = text.split()
            for i, word in enumerate(words):
                if negative_kw in word:
                    # Create window of next 3 words
                    window_end = min(i + 4, len(words))
                    window = ' '.join(words[i:window_end])

                    # Check if any strong keyword appears in this window
                    for sk in pattern.get('strong_keywords', []):
                        # For multi-word strong keywords, check the full phrase
                        if sk in window:
                            return True  # False positive

        # Rule 2: Prepositional Phrases Indicating Use Case
        # "for chandelier", "compatible with sconce", "replacement for pendant"
        # Handle both singular and plural forms
        use_case_phrases = [
            f"for {negative_kw}",
            f"for {negative_kw}s",  # plural form
            f"for use with {negative_kw}",
            f"for use in {negative_kw}",
            f"in {negative_kw}",  # e.g., "use in fixture", "in any fixture"
            f"in any {negative_kw}",
            f"in a {negative_kw}",
            f"compatible with {negative_kw}",
            f"replacement for {negative_kw}",
            f"accessory for {negative_kw}",
            f"works with {negative_kw}",
            f"use with {negative_kw}",
            f"use in {negative_kw}",
            f"ideal for {negative_kw}",
        ]

        if any(phrase in text for phrase in use_case_phrases):
            return True  # Use case mention - don't block

        # Enhanced check for use case with intervening words
        # e.g., "ideal for sconces, chandeliers or damp rated fixture"
        # Check if use case indicators appear before negative keyword within reasonable distance
        use_case_indicators = ['ideal for', 'suitable for', 'compatible with', 'works with',
                               'use with', 'for use', 'can be used', 'utilized with',
                               'such as', 'like']

        for indicator in use_case_indicators:
            if indicator in text and negative_kw in text:
                # Find ALL occurrences of the indicator, not just the first
                import re
                neg_pos = text.find(negative_kw)

                for match in re.finditer(re.escape(indicator), text):
                    indicator_pos = match.start()

                    if indicator_pos < neg_pos:
                        # Calculate distance in words
                        between = text[indicator_pos:neg_pos]
                        word_count = len(between.split())

                        # If negative keyword appears within 15 words after use case indicator, it's likely a use case
                        if word_count <= 15:
                            return True  # Use case mention with intervening words

        # Also check for patterns like "for LED and [other] bulbs" where negative_kw="led bulb"
        # This handles cases where the text says "for LED bulbs" or "for LED and Incandescent bulbs"
        if ' ' in negative_kw:
            # Multi-word negative keyword - try variations
            parts = negative_kw.split()
            if len(parts) == 2:
                # Try "for [part1] ... [part2]s" pattern
                # e.g., "for led ... bulbs" matches negative_kw="led bulb"
                first_part, second_part = parts

                # Look for "for [first_part]" and "[second_part]s" in proximity
                if f"for {first_part}" in text and f"{second_part}s" in text:
                    # Check if they're close together (within 10 words)
                    for_pos = text.find(f"for {first_part}")
                    plural_pos = text.find(f"{second_part}s")
                    if for_pos != -1 and plural_pos != -1:
                        between_words = text[for_pos:plural_pos].split()
                        if len(between_words) <= 10:
                            return True  # Use case with plural form

        # Rule 3: Product Type Compound Names
        # Common patterns where negative keyword is a modifier, not the product type
        # Also handles cases where negative keyword is PART OF product type
        bulb_compounds = [
            f"{negative_kw} bulb",
            f"{negative_kw} led",
            f"{negative_kw} light bulb",
            f"{negative_kw} led bulb",
            f"{negative_kw} led light",
            f"{negative_kw} lamp",
        ]

        if any(compound in text for compound in bulb_compounds):
            return True  # Compound product name - don't block

        # Special handling for multi-word negative keywords that ARE product types
        # e.g., negative_kw = "light bulb", check if it's part of "led light bulb"
        if ' ' in negative_kw:
            # This is a multi-word negative keyword
            # Check if product type indicators appear just before it
            product_type_prefixes = ['led', 'halogen', 'incandescent', 'cfl', 'fluorescent',
                                    'candelabra', 'chandelier', 'pendant', 'sconce',
                                    'a19', 'a21', 'br30', 'par38', 'g16', 'e26', 'e12']

            for prefix in product_type_prefixes:
                if f"{prefix} {negative_kw}" in text:
                    return True  # e.g., "led light bulb" where negative_kw = "light bulb"

        # Handle compound negative keywords like "bulb soft", "bulb daylight"
        # These are fragments, check if they're part of a bulb product
        if negative_kw in ['bulb soft', 'bulb daylight']:
            # These only appear in bulb products
            if 'watt' in text or 'led' in text or 'lumens' in text:
                return True  # This is clearly a bulb product

        # Rule 4: Integrated Components in Products with Strong Keywords
        # Example: "Faucet with Push & Seal Drain" - drain is integrated, not the product
        has_strong_keyword = any(
            self.contains_keyword(text, kw)
            for kw in pattern.get('strong_keywords', [])
        )

        # Check for integration patterns regardless of strong keyword presence
        # This catches cases like "Sink with Drain Assembly" even when testing Faucet pattern
        integration_patterns = [
            f"with {negative_kw}",
            f"includes {negative_kw}",
            f"including {negative_kw}",
            f"featuring {negative_kw}",
            f"features {negative_kw}",
            f"and {negative_kw}",
            f"w/ {negative_kw}",
            f"w {negative_kw}",
            f"{negative_kw} included",
            f"{negative_kw} assembly",  # e.g., "drain assembly"
        ]

        if any(pat in text for pat in integration_patterns):
            return True  # Integrated component - don't block

        # Also check for "for [negative_kw]" which indicates compatibility/use case
        if f"for {negative_kw}" in text:
            return True  # Use case - don't block

        # Rule 5: Position-Based Analysis for Accessories
        # If strong keyword appears BEFORE negative keyword in title, it's the main product
        # Example: "Door Handle Set with Knob" - "handle" before "knob"
        if has_strong_keyword and location == 'title':
            words = text.split()
            strong_kw_position = None
            neg_kw_position = None

            # Find positions
            for i in range(len(words)):
                # Check for strong keyword in window starting at i
                window = ' '.join(words[i:min(i+5, len(words))])
                for sk in pattern.get('strong_keywords', []):
                    if sk in window and strong_kw_position is None:
                        strong_kw_position = i

                # Check for negative keyword
                if negative_kw in words[i]:
                    neg_kw_position = i

            # If strong keyword appears first, it's the primary product
            if strong_kw_position is not None and neg_kw_position is not None:
                if strong_kw_position < neg_kw_position:
                    return True  # Strong keyword is primary - don't block

        # Rule 6: Specific Pattern Overrides
        # Some negative keywords need special handling based on pattern type

        # For lighting patterns: check for fixture-specific compounds
        if negative_kw in ['chandelier', 'sconce', 'pendant', 'ceiling fan']:
            # These are often used as modifiers for bulbs/lights
            fixture_bulb_patterns = [
                f"{negative_kw} base",
                f"{negative_kw} sized",
                f"{negative_kw} style",
                f"{negative_kw} type",
                f"for {negative_kw}s",  # plural form
            ]

            if any(pattern in text for pattern in fixture_bulb_patterns):
                return True  # Modifier usage - don't block

        # For component keywords: check if describing what's included
        if negative_kw in ['drain', 'faucet', 'showerhead']:
            # If product clearly has the pattern's strong keyword
            if has_strong_keyword:
                # Check description for "included" or "comes with"
                inclusion_words = ['included', 'comes with', 'sold with', 'ships with']
                if any(word in text for word in inclusion_words):
                    return True  # Included component - don't block

        return False  # Not a false positive - proceed with block

    def calculate_match_score(self, product: Dict, product_type: str) -> Tuple[float, List[str]]:
        """
        Calculate how well a product matches a product type pattern
        Returns (confidence_score, reasons_list)
        """
        pattern = self.patterns[product_type]
        score = 0.0
        reasons = []

        # Get product text fields
        title = self.normalize_text(product.get('title', ''))
        description = self.normalize_text(product.get('description', ''))
        brand = self.normalize_text(product.get('brand', ''))
        specs = product.get('structured_specifications', {})

        # Check for negative keywords with context-aware analysis
        for neg_kw in pattern.get('negative_keywords', []):
            # Check title
            if neg_kw in title:
                # Use context-aware analysis
                if not self.is_false_positive_block(title, neg_kw, pattern, location='title'):
                    return 0.0, [f'Disqualified by negative keyword: {neg_kw} (in title)']

            # Check description
            if neg_kw in description:
                # Use context-aware analysis
                if not self.is_false_positive_block(description, neg_kw, pattern, location='description'):
                    return 0.0, [f'Disqualified by negative keyword: {neg_kw} (in description)']

        # Strong keywords in title (highest weight)
        for kw in pattern['strong_keywords']:
            if self.contains_keyword(title, kw):
                score += 80  # Increased from 40 to 80 - title is primary signal
                reasons.append(f'Title contains "{kw}"')
                break  # Only count once

        # Strong keywords in description
        for kw in pattern['strong_keywords']:
            if self.contains_keyword(description, kw) and not self.contains_keyword(title, kw):
                score += 50  # Increased from 25 to 50 - strong description signals matter
                reasons.append(f'Description contains "{kw}"')
                break

        # Weak keywords (supporting evidence)
        weak_matches = 0
        for kw in pattern.get('weak_keywords', []):
            if self.contains_keyword(title, kw) or self.contains_keyword(description, kw):
                weak_matches += 1

        if weak_matches > 0:
            weak_score = min(weak_matches * 5, 30)  # Max 30 points for weak keywords (increased from 20)
            score += weak_score
            reasons.append(f'Found {weak_matches} supporting keywords')

        # Special boost for products with highly specific specs (like bulbs)
        if pattern.get('spec_boost') and specs:
            spec_count = sum(1 for spec_key in pattern.get('spec_indicators', set()) if spec_key in specs)
            if spec_count >= 3:
                score += 10
                reasons.append('Has product-specific specifications')

        # Description hints
        hint_matches = 0
        for hint in pattern.get('description_hints', []):
            if hint in description:
                hint_matches += 1

        if hint_matches > 0:
            hint_score = min(hint_matches * 3, 10)  # Max 10 points
            score += hint_score
            reasons.append(f'Found {hint_matches} description hints')

        # Check specifications
        spec_matches = 0
        for spec_key in pattern.get('spec_indicators', set()):
            if spec_key in specs:
                spec_matches += 1

        if spec_matches > 0:
            spec_score = min(spec_matches * 5, 15)  # Max 15 points
            score += spec_score
            reasons.append(f'Has {spec_matches} matching specifications')

        # Domain matching
        product_domains = specs.get('product_domains', [])
        pattern_domains = pattern.get('domains', [])

        if pattern_domains and product_domains:
            domain_overlap = len(set(product_domains) & set(pattern_domains))
            if domain_overlap > 0:
                domain_score = min(domain_overlap * 3, 10)  # Max 10 points
                score += domain_score
                reasons.append(f'Matches {domain_overlap} product domains')

        # Normalize to 0-100 scale
        score = min(score, 100)

        return score, reasons

    def classify_product(self, product: Dict) -> Dict:
        """
        Classify a single product
        Returns: {
            'product_type': str,
            'confidence': float (0-100),
            'confidence_level': str (High/Medium/Low/Very Low),
            'reasons': list of strings,
            'alternate_types': list of (type, score) tuples
        }
        """
        # Handle products with missing data
        # Check both raw and normalized values to catch whitespace-only strings
        title_normalized = self.normalize_text(product.get('title', ''))
        description_normalized = self.normalize_text(product.get('description', ''))

        if not title_normalized and not description_normalized:
            return {
                'product_type': 'Unknown - Missing Data',
                'confidence': 0,
                'confidence_level': 'No Data',
                'reasons': ['Product has no title or description'],
                'alternate_types': []
            }

        # Calculate scores for all product types
        scores = {}
        all_reasons = {}

        for product_type in self.patterns.keys():
            score, reasons = self.calculate_match_score(product, product_type)
            scores[product_type] = score
            all_reasons[product_type] = reasons

        # Get top matches
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        best_type, best_score = sorted_scores[0]

        # Determine confidence level
        if best_score >= 70:
            confidence_level = 'High'
        elif best_score >= 50:
            confidence_level = 'Medium'
        elif best_score >= 30:
            confidence_level = 'Low'
        elif best_score >= 20:
            confidence_level = 'Very Low'
        else:
            confidence_level = 'No Match'

        # Get alternate types (other high-scoring matches)
        alternates = [(t, s) for t, s in sorted_scores[1:6] if s >= 20]

        return {
            'product_type': best_type if best_score >= 15 else 'Unknown - Unable to Classify',
            'confidence': round(best_score, 1),
            'confidence_level': confidence_level,
            'reasons': all_reasons[best_type],
            'alternate_types': alternates
        }

    def classify_all_products(self, products: List[Dict]) -> List[Dict]:
        """
        Classify all products
        Returns list of classification results
        """
        results = []

        for i, product in enumerate(products):
            classification = self.classify_product(product)

            # Add product metadata
            result = {
                'index': i,
                'title': product.get('title', '')[:100],  # Truncate for readability
                'brand': product.get('brand', ''),
                'price': product.get('price', 0),
                **classification
            }

            results.append(result)

        return results

    def generate_statistics(self, results: List[Dict]) -> Dict:
        """Generate statistics about classification results"""

        # Count by product type
        type_counts = Counter([r['product_type'] for r in results])

        # Count by confidence level
        confidence_counts = Counter([r['confidence_level'] for r in results])

        # Average confidence
        avg_confidence = sum(r['confidence'] for r in results) / len(results)

        # Low confidence products
        low_confidence = [r for r in results if r['confidence'] < 50]

        return {
            'total_products': len(results),
            'product_types_found': len(type_counts),
            'type_distribution': dict(type_counts.most_common()),
            'confidence_distribution': dict(confidence_counts),
            'average_confidence': round(avg_confidence, 1),
            'low_confidence_count': len(low_confidence),
            'low_confidence_products': sorted(low_confidence, key=lambda x: x['confidence'])[:20]
        }


def main():
    """Main execution function"""
    import sys

    print("Loading products from data/scraped_data_output.json...")

    # Load data
    data_file = Path(__file__).parent.parent / 'data' / 'scraped_data_output.json'
    with open(data_file, 'r') as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products")
    print("\nInitializing classifier...")

    # Create classifier
    classifier = ProductClassifier()

    print(f"Classifier knows {len(classifier.patterns)} product types")
    print("\nClassifying all products...")

    # Classify all products
    results = classifier.classify_all_products(products)

    print("Classification complete!")
    print("\nGenerating statistics...")

    # Generate statistics
    stats = classifier.generate_statistics(results)

    # Print summary
    print(f"\n{'='*60}")
    print("CLASSIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Products: {stats['total_products']}")
    print(f"Product Types Found: {stats['product_types_found']}")
    print(f"Average Confidence: {stats['average_confidence']}%")
    print(f"Low Confidence Products: {stats['low_confidence_count']}")

    print(f"\n{'='*60}")
    print("CONFIDENCE DISTRIBUTION")
    print(f"{'='*60}")
    for level, count in sorted(stats['confidence_distribution'].items()):
        print(f"  {level}: {count} products")

    print(f"\n{'='*60}")
    print("TOP 15 PRODUCT TYPES")
    print(f"{'='*60}")
    for i, (ptype, count) in enumerate(list(stats['type_distribution'].items())[:15], 1):
        print(f"{i:2}. {ptype:40} {count:3} products")

    # Save results
    print("\nSaving results...")

    # Full classification results
    with open('/home/user/CC/outputs/product_classifications.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("  ✓ outputs/product_classifications.json")

    # Statistics
    with open('/home/user/CC/outputs/classification_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("  ✓ outputs/classification_statistics.json")

    # CSV for analysis
    import csv
    with open('/home/user/CC/outputs/classification_confidence.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Title', 'Brand', 'Product Type', 'Confidence', 'Confidence Level'])
        for r in results:
            writer.writerow([
                r['index'],
                r['title'],
                r['brand'],
                r['product_type'],
                r['confidence'],
                r['confidence_level']
            ])
    print("  ✓ outputs/classification_confidence.csv")

    # Taxonomy (unique product types)
    taxonomy = {
        'product_types': sorted(list(set(r['product_type'] for r in results))),
        'type_counts': stats['type_distribution'],
        'total_types': stats['product_types_found']
    }
    with open('/home/user/CC/data/product_taxonomy.json', 'w') as f:
        json.dump(taxonomy, f, indent=2)
    print("  ✓ data/product_taxonomy.json")

    print("\n✓ Classification complete!")

    return results, stats


if __name__ == '__main__':
    results, stats = main()
