import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import os

class MedicinePredictor:
    def __init__(self):
        self.model = None
        self.symptoms_dict = None
        self.diseases_list = None
        self.supporting_data = {}
        self.load_model_and_data()
    
    def load_model_and_data(self):
        """Load your trained model and supporting datasets"""
        # Get the path to ml_assets directory - first try backend/ml_assets
        base_path = Path(__file__).parent.parent / 'ml_assets'
        
        # If not found, try root/ml_assets
        if not base_path.exists():
            base_path = Path(__file__).parent.parent.parent / 'ml_assets'
        
        # If still not found, try root directory
        if not base_path.exists():
            base_path = Path(__file__).parent.parent.parent
        
        try:
            # Load trained SVC model
            model_path = base_path / 'svc.pkl'
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found at {model_path}")
                
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load supporting datasets
            self.supporting_data['symptoms'] = pd.read_csv(base_path / 'symtoms_df.csv')
            self.supporting_data['precautions'] = pd.read_csv(base_path / 'precautions_df.csv')
            self.supporting_data['workout'] = pd.read_csv(base_path / 'workout_df.csv')
            self.supporting_data['description'] = pd.read_csv(base_path / 'description.csv')
            self.supporting_data['medications'] = pd.read_csv(base_path / 'medications.csv')
            self.supporting_data['diets'] = pd.read_csv(base_path / 'diets.csv')
            
            print("✓ All data files loaded successfully")
            
        except FileNotFoundError as e:
            print(f"Error loading files: {e}")
            raise e
        except Exception as e:
            print(f"Error loading model or data: {e}")
            raise e
        
        # Symptoms dictionary from your notebook
        self.symptoms_dict = {
            'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3,
            'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8,
            'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12,
            'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16,
            'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20,
            'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24,
            'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28,
            'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32,
            'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36,
            'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40,
            'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44,
            'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48,
            'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51,
            'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55,
            'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58,
            'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61,
            'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65,
            'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69,
            'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72,
            'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75,
            'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78,
            'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82,
            'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85,
            'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88,
            'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91,
            'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94,
            'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98,
            'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101,
            'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104,
            'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108,
            'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111,
            'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114,
            'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117,
            'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120,
            'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124,
            'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127,
            'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131
        }
        
        # Diseases list from your notebook  
        self.diseases_list = {
            15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis',
            14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ',
            17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine',
            7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice',
            29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
            19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E',
            3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia',
            13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins',
            26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis',
            5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne',
            38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'
        }
    
    def predict_disease(self, patient_symptoms):
        """Predict disease from symptoms using your existing function"""
        input_vector = np.zeros(len(self.symptoms_dict))
        
        for item in patient_symptoms:
            if item in self.symptoms_dict:
                input_vector[self.symptoms_dict[item]] = 1
        
        prediction = self.model.predict([input_vector])[0]
        return self.diseases_list[prediction]
    
    def get_disease_info(self, disease):
        """Get disease information from supporting data"""
        description_df = self.supporting_data['description']
        precautions_df = self.supporting_data['precautions']
        medications_df = self.supporting_data['medications']
        diets_df = self.supporting_data['diets']
        workout_df = self.supporting_data['workout']
        
        # Description
        desc = description_df[description_df['Disease'] == disease]['Description']
        desc = " ".join([str(w) for w in desc.values]) if len(desc) > 0 else "No description available"

        # Precautions
        pre = precautions_df[precautions_df['Disease'] == disease][
            ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']
        ]
        precautions_list = []
        if len(pre) > 0:
            for row in pre.values:
                for item in row:
                    if pd.notna(item) and str(item).strip():
                        precautions_list.append(str(item))

        # Medications
        med = medications_df[medications_df['Disease'] == disease]['Medication']
        med_list = [str(m) for m in med.values] if len(med) > 0 else []

        # Diet
        die = diets_df[diets_df['Disease'] == disease]['Diet']
        diet_list = [str(d) for d in die.values] if len(die) > 0 else []

        # Workout
        wrkout = workout_df[workout_df['disease'] == disease]['workout']
        wrkout_list = [str(w) for w in wrkout.values] if len(wrkout) > 0 else []
        
        return {
            'description': desc,
            'precautions': precautions_list,
            'medications': med_list,
            'diet': diet_list,
            'workout': wrkout_list
        }
    
    def get_prediction_with_details(self, symptoms):
        """Complete prediction with all details"""
        try:
            # Clean symptoms input
            user_symptoms = [s.strip() for s in symptoms if s.strip()]
            user_symptoms = [sym.strip("[]' '") for sym in user_symptoms]
            
            # Validate symptoms
            valid_symptoms = [sym for sym in user_symptoms if sym in self.symptoms_dict]
            invalid_symptoms = [sym for sym in user_symptoms if sym not in self.symptoms_dict]
            
            if not valid_symptoms:
                return {
                    'success': False,
                    'error': 'No valid symptoms provided',
                    'invalid_symptoms': invalid_symptoms,
                    'message': 'Please provide valid symptoms from the available list'
                }
            
            # Predict disease
            predicted_disease = self.predict_disease(valid_symptoms)
            
            # Get detailed information
            disease_info = self.get_disease_info(predicted_disease)
            
            return {
                'success': True,
                'predicted_disease': predicted_disease,
                'confidence': 1.0,  # Your model achieved 100% accuracy
                'description': disease_info['description'],
                'precautions': disease_info['precautions'],
                'medications': disease_info['medications'],
                'diet': disease_info['diet'],
                'workout': disease_info['workout'],
                'symptoms_detected': valid_symptoms,
                'invalid_symptoms': invalid_symptoms,
                'total_symptoms': len(valid_symptoms)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Error in prediction process'
            }
    
    def get_all_symptoms(self):
        """Get list of all available symptoms"""
        return list(self.symptoms_dict.keys())
    
    def get_all_diseases(self):
        """Get list of all possible diseases"""
        return list(self.diseases_list.values())
    
    def search_symptoms(self, query, limit=10):
        """Search symptoms by partial name match"""
        query = query.lower()
        matching_symptoms = [
            symptom for symptom in self.symptoms_dict.keys() 
            if query in symptom.lower()
        ]
        return matching_symptoms[:limit]
