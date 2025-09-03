"""
Input validation utilities
"""

def validate_symptoms(symptoms):
    """Validate symptoms input"""
    if not isinstance(symptoms, list):
        return False, "Symptoms must be a list"
    
    if len(symptoms) == 0:
        return False, "At least one symptom is required"
    
    if len(symptoms) > 20:
        return False, "Maximum 20 symptoms allowed"
    
    for symptom in symptoms:
        if not isinstance(symptom, str):
            return False, "All symptoms must be strings"
        
        if len(symptom.strip()) == 0:
            return False, "Empty symptoms are not allowed"
    
    return True, "Valid"
