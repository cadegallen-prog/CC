#!/usr/bin/env python3
"""
Product Classification System
Identifies what each product actually IS (e.g., "LED bulb", "ceiling fan", "drill bit")
"""

import json
import re
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
                'strong_keywords': ['light bulb', 'led bulb', 'lamp bulb', 'bulb soft white', 'bulb daylight'],
                'weak_keywords': ['watt equivalent', 'lumens', 'kelvin', 'dimmable', 'a19', 'a21', 'br30', 'par38', 'e26', 'e12', 'b10', 'candelabra'],
                'description_hints': ['watt equivalent', 'color temperature', 'soft white', 'daylight', 'cri', 'bulbs for', 'bulbs take', 'led bulbs'],
                'spec_indicators': {'wattage', 'lumens', 'color_temp', 'base_type', 'dimmable'},
                'domains': ['lighting', 'electrical'],
                'negative_keywords': [],  # Remove negative keywords - bulbs are often described as "for chandelier", etc
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
                'strong_keywords': ['pendant light', 'mini-pendant', 'pendant with', 'light pendant'],
                'weak_keywords': ['hanging', 'suspension', 'chain', 'adjustable height', 'glass shade'],
                'description_hints': ['hanging light', 'ceiling mounted', 'decorative lighting', 'pendant is'],
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
                'strong_keywords': ['sconce', 'wall sconce', 'wall light'],
                'weak_keywords': ['wall mount', 'vanity light', 'bath light'],
                'description_hints': ['wall mounted', 'bathroom lighting', 'decorative wall'],
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
                'strong_keywords': ['switch', 'light switch', 'dimmer switch', 'rocker switch', 'toggle switch'],
                'weak_keywords': ['gang', 'way', '3-way', '4-way', 'decorator'],
                'description_hints': ['wall switch', 'control lighting'],
                'domains': ['electrical', 'lighting'],
                'negative_keywords': ['breaker', 'outlet', 'receptacle']
            },

            'Electrical Outlet': {
                'strong_keywords': ['outlet', 'receptacle', 'gfci outlet', 'usb outlet'],
                'weak_keywords': ['duplex', 'tamper resistant', 'grounded'],
                'description_hints': ['wall outlet', 'power receptacle'],
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
                'strong_keywords': ['sink', 'bathroom sink', 'kitchen sink', 'utility sink', 'vessel sink'],
                'weak_keywords': ['basin', 'bowl', 'undermount', 'drop-in', 'farmhouse'],
                'description_hints': ['wash basin'],
                'domains': ['plumbing'],
                'negative_keywords': ['faucet', 'drain only']
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
                'negative_keywords': ['tape']
            },

            'Plumbing Fitting': {
                'strong_keywords': ['fitting', 'elbow', 'coupling', 'tee', 'adapter', 'connector', 'push-to-connect'],
                'weak_keywords': ['pvc', 'copper', 'brass', 'compression', 'threaded'],
                'description_hints': ['pipe fitting', 'plumbing connection'],
                'domains': ['plumbing'],
                'negative_keywords': ['faucet', 'showerhead', 'toilet']
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
        """Convert text to lowercase and remove extra spaces"""
        if not text:
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

        # Check for negative keywords first (disqualifiers)
        for neg_kw in pattern.get('negative_keywords', []):
            if neg_kw in title or neg_kw in description:
                return 0.0, ['Disqualified by negative keyword: ' + neg_kw]

        # Strong keywords in title (highest weight)
        for kw in pattern['strong_keywords']:
            if self.contains_keyword(title, kw):
                score += 40
                reasons.append(f'Title contains "{kw}"')
                break  # Only count once

        # Strong keywords in description
        for kw in pattern['strong_keywords']:
            if self.contains_keyword(description, kw) and not self.contains_keyword(title, kw):
                score += 25
                reasons.append(f'Description contains "{kw}"')
                break

        # Weak keywords (supporting evidence)
        weak_matches = 0
        for kw in pattern.get('weak_keywords', []):
            if self.contains_keyword(title, kw) or self.contains_keyword(description, kw):
                weak_matches += 1

        if weak_matches > 0:
            weak_score = min(weak_matches * 5, 20)  # Max 20 points for weak keywords
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
        if not product.get('title') and not product.get('description'):
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
        else:
            confidence_level = 'Very Low'

        # Get alternate types (other high-scoring matches)
        alternates = [(t, s) for t, s in sorted_scores[1:6] if s >= 20]

        return {
            'product_type': best_type if best_score >= 30 else 'Unknown - Unable to Classify',
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
    with open('/home/user/CC/data/scraped_data_output.json', 'r') as f:
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
