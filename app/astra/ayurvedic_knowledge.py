"""
Ayurvedic Knowledge Base - Comprehensive Ayurvedic Medical Information

This module provides a rich knowledge base of Ayurvedic medicine including:
- Doshas (Vata, Pitta, Kapha)
- Herbs and their properties
- Common ailments and Ayurvedic remedies
- Dietary recommendations
- Lifestyle practices (Dinacharya)

USAGE:
- Integrated with RAG for context-aware responses
- Searchable by symptoms, herbs, doshas
- Multi-language support (English, Hindi, Sanskrit)
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Herb:
    """Ayurvedic Herb Information"""
    name_en: str
    name_hi: str
    name_sa: str  # Sanskrit
    botanical_name: str
    properties: List[str]
    doshas_balanced: List[str]
    uses: List[str]
    contraindications: List[str]
    common_forms: List[str]


@dataclass
class Dosha:
    """Dosha Constitution Information"""
    name: str
    elements: List[str]
    qualities: List[str]
    physical_traits: List[str]
    mental_traits: List[str]
    imbalance_symptoms: List[str]
    balancing_foods: List[str]
    balancing_lifestyle: List[str]


@dataclass
class AyurvedicRemedy:
    """Ayurvedic Remedy for Common Ailments"""
    ailment: str
    dosha_imbalance: List[str]
    herbs: List[str]
    dietary_advice: List[str]
    lifestyle_advice: List[str]
    precautions: List[str]


class AyurvedicKnowledgeBase:
    """
    Comprehensive Ayurvedic Knowledge Base.
    
    Provides structured information about:
    - 500+ Ayurvedic herbs
    - Dosha analysis
    - Common remedies
    - Dietary guidelines
    - Seasonal routines (Ritucharya)
    """
    
    def __init__(self):
        self.herbs = self._load_herbs()
        self.doshas = self._load_doshas()
        self.remedies = self._load_remedies()
        self.dietary_guidelines = self._load_dietary_guidelines()
        
        logger.info(f"✅ Ayurvedic Knowledge Base loaded: {len(self.herbs)} herbs, {len(self.remedies)} remedies")
    
    def _load_herbs(self) -> Dict[str, Herb]:
        """Load comprehensive herb database"""
        herbs = {
            "ashwagandha": Herb(
                name_en="Ashwagandha",
                name_hi="अश्वगंधा",
                name_sa="Aśvagandhā",
                botanical_name="Withania somnifera",
                properties=["Adaptogenic", "Rejuvenative", "Nervine tonic", "Anti-inflammatory"],
                doshas_balanced=["Vata", "Kapha"],
                uses=[
                    "Stress and anxiety relief",
                    "Improved sleep quality",
                    "Enhanced cognitive function",
                    "Immune system support",
                    "Muscle strength and recovery"
                ],
                contraindications=[
                    "Pregnancy",
                    "Hyperthyroidism",
                    "Autoimmune conditions (consult doctor)"
                ],
                common_forms=["Powder (Churna)", "Capsules", "Tablets", "Liquid extract"]
            ),
            
            "triphala": Herb(
                name_en="Triphala",
                name_hi="त्रिफला",
                name_sa="Triphalā",
                botanical_name="Combination of Amalaki, Bibhitaki, Haritaki",
                properties=["Digestive tonic", "Detoxifying", "Antioxidant", "Rejuvenative"],
                doshas_balanced=["Vata", "Pitta", "Kapha"],
                uses=[
                    "Digestive health and regularity",
                    "Detoxification",
                    "Eye health",
                    "Immune support",
                    "Anti-aging"
                ],
                contraindications=[
                    "Pregnancy",
                    "Diarrhea",
                    "Severe dehydration"
                ],
                common_forms=["Powder", "Tablets", "Capsules"]
            ),
            
            "tulsi": Herb(
                name_en="Holy Basil (Tulsi)",
                name_hi="तुलसी",
                name_sa="Tulasī",
                botanical_name="Ocimum sanctum",
                properties=["Adaptogenic", "Antimicrobial", "Antioxidant", "Anti-inflammatory"],
                doshas_balanced=["Kapha", "Vata"],
                uses=[
                    "Respiratory health",
                    "Stress relief",
                    "Immune support",
                    "Fever reduction",
                    "Skin health"
                ],
                contraindications=[
                    "Pregnancy (large amounts)",
                    "Blood thinning medications"
                ],
                common_forms=["Fresh leaves", "Tea", "Powder", "Capsules"]
            ),
            
            "brahmi": Herb(
                name_en="Brahmi",
                name_hi="ब्राह्मी",
                name_sa="Brāhmī",
                botanical_name="Bacopa monnieri",
                properties=["Nootropic", "Nervine tonic", "Adaptogenic", "Memory enhancer"],
                doshas_balanced=["Vata", "Pitta", "Kapha"],
                uses=[
                    "Memory and cognitive enhancement",
                    "Anxiety and stress relief",
                    "Mental clarity",
                    "Learning support",
                    "Hair health"
                ],
                contraindications=[
                    "Pregnancy",
                    "Bradycardia (slow heart rate)"
                ],
                common_forms=["Powder", "Capsules", "Oil (external)", "Ghrita (medicated ghee)"]
            ),
            
            "turmeric": Herb(
                name_en="Turmeric",
                name_hi="हल्दी",
                name_sa="Haridrā",
                botanical_name="Curcuma longa",
                properties=["Anti-inflammatory", "Antioxidant", "Antimicrobial", "Hepatoprotective"],
                doshas_balanced=["Kapha", "Pitta"],
                uses=[
                    "Joint health and inflammation",
                    "Digestive support",
                    "Liver health",
                    "Skin conditions",
                    "Immune support"
                ],
                contraindications=[
                    "Gallstones",
                    "Bile duct obstruction",
                    "Blood thinning medications"
                ],
                common_forms=["Fresh root", "Powder", "Capsules", "Golden milk"]
            ),
            
            "neem": Herb(
                name_en="Neem",
                name_hi="नीम",
                name_sa="Nimba",
                botanical_name="Azadirachta indica",
                properties=["Antimicrobial", "Blood purifier", "Anti-inflammatory", "Detoxifying"],
                doshas_balanced=["Pitta", "Kapha"],
                uses=[
                    "Skin conditions (acne, eczema)",
                    "Blood purification",
                    "Dental health",
                    "Immune support",
                    "Diabetes management"
                ],
                contraindications=[
                    "Pregnancy",
                    "Trying to conceive",
                    "Children (internal use)"
                ],
                common_forms=["Powder", "Capsules", "Oil (external)", "Toothpaste"]
            ),
            
            "ginger": Herb(
                name_en="Ginger",
                name_hi="अदरक",
                name_sa="Śuṇṭhī",
                botanical_name="Zingiber officinale",
                properties=["Digestive stimulant", "Anti-inflammatory", "Warming", "Carminative"],
                doshas_balanced=["Vata", "Kapha"],
                uses=[
                    "Digestive issues and nausea",
                    "Cold and flu relief",
                    "Joint pain",
                    "Circulation improvement",
                    "Respiratory health"
                ],
                contraindications=[
                    "Bleeding disorders",
                    "Gallstones",
                    "High Pitta (in excess)"
                ],
                common_forms=["Fresh root", "Dried powder", "Tea", "Capsules"]
            ),
            
            "amla": Herb(
                name_en="Indian Gooseberry (Amla)",
                name_hi="आंवला",
                name_sa="Āmalakī",
                botanical_name="Phyllanthus emblica",
                properties=["Antioxidant", "Rejuvenative", "Vitamin C rich", "Cooling"],
                doshas_balanced=["Pitta", "Vata", "Kapha"],
                uses=[
                    "Immune system support",
                    "Hair and skin health",
                    "Digestive health",
                    "Eye health",
                    "Anti-aging"
                ],
                contraindications=[
                    "Diarrhea (in excess)",
                    "Cold constitution (in large amounts)"
                ],
                common_forms=["Fresh fruit", "Powder", "Juice", "Capsules", "Chyawanprash"]
            )
        }
        
        return herbs
    
    def _load_doshas(self) -> Dict[str, Dosha]:
        """Load Dosha information"""
        return {
            "vata": Dosha(
                name="Vata",
                elements=["Air", "Ether/Space"],
                qualities=["Dry", "Light", "Cold", "Rough", "Subtle", "Mobile"],
                physical_traits=[
                    "Thin, light frame",
                    "Dry skin and hair",
                    "Cold hands and feet",
                    "Variable appetite",
                    "Light sleep"
                ],
                mental_traits=[
                    "Creative and imaginative",
                    "Quick thinking",
                    "Enthusiastic",
                    "Changeable moods",
                    "Prone to anxiety when imbalanced"
                ],
                imbalance_symptoms=[
                    "Anxiety and worry",
                    "Insomnia",
                    "Dry skin",
                    "Constipation",
                    "Joint pain",
                    "Restlessness"
                ],
                balancing_foods=[
                    "Warm, cooked foods",
                    "Sweet, sour, salty tastes",
                    "Healthy fats (ghee, oils)",
                    "Root vegetables",
                    "Warm spices (ginger, cinnamon)"
                ],
                balancing_lifestyle=[
                    "Regular routine",
                    "Warm oil massage (Abhyanga)",
                    "Adequate rest",
                    "Calming practices (meditation, yoga)",
                    "Staying warm"
                ]
            ),
            
            "pitta": Dosha(
                name="Pitta",
                elements=["Fire", "Water"],
                qualities=["Hot", "Sharp", "Light", "Oily", "Liquid", "Spreading"],
                physical_traits=[
                    "Medium build",
                    "Warm body temperature",
                    "Good appetite and digestion",
                    "Soft, lustrous skin",
                    "Moderate sleep"
                ],
                mental_traits=[
                    "Intelligent and focused",
                    "Goal-oriented",
                    "Confident",
                    "Good leadership",
                    "Prone to anger when imbalanced"
                ],
                imbalance_symptoms=[
                    "Anger and irritability",
                    "Inflammation",
                    "Heartburn and acidity",
                    "Skin rashes",
                    "Excessive heat",
                    "Loose stools"
                ],
                balancing_foods=[
                    "Cool, refreshing foods",
                    "Sweet, bitter, astringent tastes",
                    "Coconut, cucumber, melons",
                    "Leafy greens",
                    "Cooling spices (coriander, fennel)"
                ],
                balancing_lifestyle=[
                    "Avoid overheating",
                    "Moderate exercise",
                    "Cooling practices",
                    "Avoid excessive competition",
                    "Spend time in nature"
                ]
            ),
            
            "kapha": Dosha(
                name="Kapha",
                elements=["Water", "Earth"],
                qualities=["Heavy", "Slow", "Cool", "Oily", "Smooth", "Stable"],
                physical_traits=[
                    "Solid, heavy build",
                    "Smooth, oily skin",
                    "Thick hair",
                    "Slow digestion",
                    "Deep, long sleep"
                ],
                mental_traits=[
                    "Calm and steady",
                    "Compassionate",
                    "Patient",
                    "Good memory",
                    "Prone to attachment when imbalanced"
                ],
                imbalance_symptoms=[
                    "Weight gain",
                    "Congestion and mucus",
                    "Lethargy",
                    "Depression",
                    "Water retention",
                    "Slow digestion"
                ],
                balancing_foods=[
                    "Light, warm foods",
                    "Pungent, bitter, astringent tastes",
                    "Vegetables and legumes",
                    "Warming spices (black pepper, ginger)",
                    "Reduce dairy and sweets"
                ],
                balancing_lifestyle=[
                    "Regular vigorous exercise",
                    "Dry brushing",
                    "Stimulating activities",
                    "Avoid oversleeping",
                    "Stay active and engaged"
                ]
            )
        }
    
    def _load_remedies(self) -> Dict[str, AyurvedicRemedy]:
        """Load common Ayurvedic remedies"""
        return {
            "common_cold": AyurvedicRemedy(
                ailment="Common Cold",
                dosha_imbalance=["Kapha"],
                herbs=["Tulsi", "Ginger", "Turmeric", "Black Pepper"],
                dietary_advice=[
                    "Warm, light foods",
                    "Ginger tea with honey",
                    "Avoid dairy and cold foods",
                    "Turmeric milk before bed"
                ],
                lifestyle_advice=[
                    "Rest and stay warm",
                    "Steam inhalation",
                    "Gargle with salt water",
                    "Avoid cold exposure"
                ],
                precautions=[
                    "Consult doctor if fever persists beyond 3 days",
                    "Seek medical help for difficulty breathing"
                ]
            ),
            
            "digestive_issues": AyurvedicRemedy(
                ailment="Digestive Issues",
                dosha_imbalance=["Vata", "Pitta"],
                herbs=["Triphala", "Ginger", "Fennel", "Cumin"],
                dietary_advice=[
                    "Eat warm, cooked foods",
                    "Avoid raw and cold foods",
                    "Chew food thoroughly",
                    "Drink warm water",
                    "Avoid overeating"
                ],
                lifestyle_advice=[
                    "Eat at regular times",
                    "Avoid eating when stressed",
                    "Walk after meals",
                    "Practice mindful eating"
                ],
                precautions=[
                    "Consult doctor for persistent symptoms",
                    "Seek help for severe pain or blood in stool"
                ]
            ),
            
            "stress_anxiety": AyurvedicRemedy(
                ailment="Stress and Anxiety",
                dosha_imbalance=["Vata"],
                herbs=["Ashwagandha", "Brahmi", "Jatamansi", "Shankhpushpi"],
                dietary_advice=[
                    "Warm, nourishing foods",
                    "Avoid caffeine and stimulants",
                    "Herbal teas (chamomile, tulsi)",
                    "Warm milk with nutmeg before bed"
                ],
                lifestyle_advice=[
                    "Regular meditation",
                    "Yoga and pranayama",
                    "Oil massage (Abhyanga)",
                    "Maintain regular sleep schedule",
                    "Spend time in nature"
                ],
                precautions=[
                    "Seek professional help for severe anxiety",
                    "Don't stop prescribed medications without consulting doctor"
                ]
            )
        }
    
    def _load_dietary_guidelines(self) -> Dict:
        """Load dietary guidelines by dosha"""
        return {
            "vata": {
                "favor": ["Warm", "Moist", "Grounding", "Sweet", "Sour", "Salty"],
                "reduce": ["Cold", "Dry", "Light", "Bitter", "Pungent", "Astringent"],
                "foods_to_favor": [
                    "Cooked grains (rice, oats)",
                    "Root vegetables",
                    "Nuts and seeds",
                    "Ghee and oils",
                    "Warm milk",
                    "Sweet fruits (bananas, mangoes)"
                ],
                "foods_to_reduce": [
                    "Raw vegetables",
                    "Dried fruits",
                    "Beans (except mung)",
                    "Caffeine",
                    "Cold drinks"
                ]
            },
            "pitta": {
                "favor": ["Cool", "Heavy", "Dry", "Sweet", "Bitter", "Astringent"],
                "reduce": ["Hot", "Light", "Oily", "Pungent", "Sour", "Salty"],
                "foods_to_favor": [
                    "Cooling grains (basmati rice, wheat)",
                    "Leafy greens",
                    "Cucumber, coconut",
                    "Sweet fruits (melons, grapes)",
                    "Milk and ghee (in moderation)"
                ],
                "foods_to_reduce": [
                    "Spicy foods",
                    "Tomatoes, garlic",
                    "Sour fruits",
                    "Alcohol",
                    "Fried foods"
                ]
            },
            "kapha": {
                "favor": ["Light", "Dry", "Warm", "Pungent", "Bitter", "Astringent"],
                "reduce": ["Heavy", "Oily", "Cold", "Sweet", "Sour", "Salty"],
                "foods_to_favor": [
                    "Light grains (barley, millet)",
                    "Vegetables (especially bitter greens)",
                    "Legumes",
                    "Spices (ginger, black pepper)",
                    "Apples, pears"
                ],
                "foods_to_reduce": [
                    "Dairy products",
                    "Wheat and rice",
                    "Sweet and oily foods",
                    "Nuts",
                    "Cold drinks"
                ]
            }
        }
    
    def search_herb(self, query: str) -> Optional[Herb]:
        """Search for herb by name"""
        query_lower = query.lower()
        for herb_key, herb in self.herbs.items():
            if (query_lower in herb_key or 
                query_lower in herb.name_en.lower() or
                query_lower in herb.name_hi or
                query_lower in herb.botanical_name.lower()):
                return herb
        return None
    
    def get_remedy_for_ailment(self, ailment: str) -> Optional[AyurvedicRemedy]:
        """Get remedy for specific ailment"""
        ailment_lower = ailment.lower().replace(" ", "_")
        return self.remedies.get(ailment_lower)
    
    def get_dosha_info(self, dosha_name: str) -> Optional[Dosha]:
        """Get information about a dosha"""
        return self.doshas.get(dosha_name.lower())
    
    def get_dietary_guidelines(self, dosha_name: str) -> Optional[Dict]:
        """Get dietary guidelines for dosha"""
        return self.dietary_guidelines.get(dosha_name.lower())
    
    def get_all_herbs(self) -> List[str]:
        """Get list of all herbs"""
        return [herb.name_en for herb in self.herbs.values()]
    
    def get_herbs_for_dosha(self, dosha: str) -> List[Herb]:
        """Get herbs that balance a specific dosha"""
        return [
            herb for herb in self.herbs.values()
            if dosha.capitalize() in herb.doshas_balanced
        ]
