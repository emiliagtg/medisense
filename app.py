from flask import Flask, request, jsonify, render_template
from google.cloud import dialogflow
import os
import sqlite3
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Davina\\Desktop\\medisense\\medisensechatbot-wlsc-fce172291cad.json"
dialogflow_project_id = "medisensechatbot-wlsc"
session_client = dialogflow.SessionsClient()

model = load_model('skin_disease_model.h5')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  

def detect_intent_texts(project_id, session_id, text, language_code="en"):
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(request={"session": session, "query_input": query_input})
    return response.query_result.fulfillment_text

def preprocess_image(image):
    image = image.resize((150, 150))  
    image = np.array(image) / 255.0  
    image = np.expand_dims(image, axis=0)  
    return image

@app.route('/')
def index():
    return render_template('chat.html')

@app.route("/get_text_response", methods=["POST"])
def get_text_response():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"response": "Message cannot be left empty. Please ask related to healthcare/first aid."})
    
    session_id = request.remote_addr
    try:
        response_text = detect_intent_texts(dialogflow_project_id, session_id, user_input, "en")
    except Exception as e:
        print(f"Error communicating with Dialogflow: {e}")
        response_text = "I'm sorry, I couldn't process your request. Please ask related to healthcare/first aid."

    return jsonify({"response": response_text})

@app.route("/upload_image", methods=["POST"])
def upload_image():
    file = request.files.get("image") 
    if not file:
        return jsonify({"response": "No image uploaded. Please upload a valid image file."}), 400

    try:
        image = Image.open(file.stream).convert("RGB")
        processed_image = preprocess_image(image)  
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions, axis=1)[0]
        
        condition_mapping = {
                    0: 'Acne_Keloidalis_Nuchae',
                    1: 'Acne_Vulgaris',
                    2: 'Acrokeratosis_Verruciformis',
                    3: 'Actinic_solar_Damage(Actinic_Cheilitis)',
                    4: 'Actinic_solar_Damage(Actinic_Keratosis)',
                    5: 'Actinic_solar_Damage(Cutis_Rhomboidalis_Nuchae)',
                    6: 'Actinic_solar_Damage(Pigmentation)',
                    7: 'Actinic_solar_Damage(Solar_Elastosis)',
                    8: 'Actinic_solar_Damage(Solar_Purpura)',
                    9: 'Actinic_solar_Damage(Telangiectasia)',
                    10: 'Acute_Eczema',
                    11: 'Allergic_Contact_Dermatitis',
                    12: 'Alopecia_Areata',
                    13: 'Androgenetic_Alopecia',
                    14: 'Angioma',
                    15: 'Angular_Cheilitis',
                    16: 'Aphthous_Ulcer',
                    17: 'Apocrine_Hydrocystoma',
                    18: 'Arsenical_Keratosis',
                    19: 'Balanitis_Xerotica_Obliterans',
                    20: 'Basal_Cell_Carcinoma',
                    21: "Beau's_Lines",
                    22: "Becker's_Nevus",
                    23: "Behcet's_Syndrome",
                    24: 'Benign_Keratosis',
                    25: 'Blue_Nevus',
                    26: "Bowen's_Disease",
                    27: 'Bowenoid_Papulosis',
                    28: 'Cafe_Au_Lait_Macule',
                    29: 'Callus',
                    30: 'Candidiasis',
                    31: 'Cellulitis',
                    32: 'Chalazion',
                    33: 'Clubbing_of_Fingers',
                    34: 'Compound_Nevus',
                    35: 'Congenital_Nevus',
                    36: "Crowe's_Sign",
                    37: 'Cutanea_Larva_Migrans',
                    38: 'Cutaneous_Horn',
                    39: 'Cutaneous_T-Cell_Lymphoma',
                    40: 'Cutis_Marmorata',
                    41: 'Darier-White_Disease',
                    42: 'Dermatofibroma',
                    43: 'Dermatosis_Papulosa_Nigra',
                    44: 'Desquamation',
                    45: 'Digital_Fibroma',
                    46: 'Dilated_Pore_of_Winer',
                    47: 'Discoid_Lupus_Erythematosus',
                    48: 'Disseminated_Actinic_Porokeratosis',
                    49: 'Drug_Eruption',
                    50: 'Dry_Skin_Eczema',
                    51: 'Dyshidrosiform_Eczema',
                    52: 'Dysplastic_Nevus',
                    53: 'Eccrine_Poroma',
                    54: 'Eczema',
                    55: 'Epidermal_Nevus',
                    56: 'Epidermoid_Cyst',
                    57: 'Epithelioma_Adenoides_Cysticum',
                    58: 'Erythema_Ab_Igne',
                    59: 'Erythema_Annulare_Centrifigum',
                    60: 'Erythema_Craquele',
                    61: 'Erythema_Multiforme',
                    62: 'Exfoliative_Erythroderma',
                    63: 'Factitial_Dermatitis',
                    64: 'Favre_Racouchot',
                    65: 'Fibroma',
                    66: 'Fibroma_Molle'
                }

        condition = condition_mapping.get(predicted_class, "Unknown")
        first_aid_responses = {
                'Acne_Keloidalis_Nuchae': "Avoid irritants; consult a dermatologist for long-term care.",
                'Acne_Vulgaris': "Cleanse skin gently; avoid picking or squeezing acne lesions.",
                'Acrokeratosis_Verruciformis': "Moisturize regularly; avoid irritating products on affected areas.",
                'Actinic_solar_Damage(Actinic_Cheilitis)': "Apply sunscreen and lip balm; avoid sun exposure.",
                'Actinic_solar_Damage(Actinic_Keratosis)': "Use sunscreen; see a healthcare provider for potential removal.",
                'Actinic_solar_Damage(Cutis_Rhomboidalis_Nuchae)': "Use sun protection and consult a dermatologist.",
                'Actinic_solar_Damage(Pigmentation)': "Apply sunscreen; avoid direct sun exposure.",
                'Actinic_solar_Damage(Solar_Elastosis)': "Use moisturizing products and avoid sun exposure.",
                'Actinic_solar_Damage(Solar_Purpura)': "Apply cold compresses and avoid trauma to the skin.",
                'Actinic_solar_Damage(Telangiectasia)': "Protect skin from sun; consult a dermatologist if needed.",
                'Acute_Eczema': "Apply a hypoallergenic moisturizer; avoid scratching.",
                'Allergic_Contact_Dermatitis': "Wash affected area; apply hydrocortisone cream if necessary.",
                'Alopecia_Areata': "Consult a dermatologist for treatment options; reduce stress.",
                'Androgenetic_Alopecia': "Seek professional medical advice; maintain a healthy diet.",
                'Angioma': "No immediate action needed; consult a doctor if changes occur.",
                'Angular_Cheilitis': "Apply lip balm; avoid licking lips and keep the area dry.",
                'Aphthous_Ulcer': "Use a saltwater rinse; avoid spicy or acidic foods.",
                'Apocrine_Hydrocystoma': "No immediate first aid needed; consult a dermatologist for removal if necessary.",
                'Arsenical_Keratosis': "Avoid further arsenic exposure; consult a healthcare provider.",
                'Balanitis_Xerotica_Obliterans': "Apply prescribed ointments; consult a urologist if persistent.",
                'Basal_Cell_Carcinoma': "See a dermatologist promptly for assessment and possible removal.",
                "Beau's_Lines": "Monitor nail growth; consult a healthcare provider if persistent.",
                "Becker's_Nevus": "Typically no treatment is required; consult a dermatologist if needed.",
                "Behcet's_Syndrome": "Avoid irritating foods; consult a healthcare provider for medication.",
                'Benign_Keratosis': "Moisturize skin; see a healthcare provider for removal if desired.",
                'Blue_Nevus': "No immediate action needed; monitor for changes and consult a dermatologist.",
                "Bowen's_Disease": "Avoid sun exposure; see a healthcare provider for treatment.",
                'Bowenoid_Papulosis': "Avoid friction to affected area; consult a healthcare provider.",
                'Cafe_Au_Lait_Macule': "No first aid required; monitor for any changes in size or color.",
                'Callus': "Soak and moisturize the area; use a pumice stone to reduce thickness.",
                'Candidiasis': "Keep the area clean and dry; consult a healthcare provider for antifungal treatment.",
                'Cellulitis': "Apply a cold compress; seek medical treatment if swelling or pain worsens.",
                'Chalazion': "Apply warm compresses; avoid squeezing.",
                'Clubbing_of_Fingers': "No immediate first aid; consult a healthcare provider for evaluation.",
                'Compound_Nevus': "Monitor for changes in color or size; consult a dermatologist if concerned.",
                'Congenital_Nevus': "Monitor for any changes; consult a dermatologist.",
                "Crowe's_Sign": "No first aid required; consult a healthcare provider for advice.",
                'Cutanea_Larva_Migrans': "Avoid scratching; consult a healthcare provider for antiparasitic medication.",
                'Cutaneous_Horn': "See a healthcare provider for removal; avoid trauma to the area.",
                'Cutaneous_T-Cell_Lymphoma': "Consult an oncologist; avoid skin trauma.",
                'Cutis_Marmorata': "Keep warm; no treatment usually required.",
                'Darier-White_Disease': "Keep skin cool and dry; avoid tight clothing.",
                'Dermatofibroma': "No treatment needed; consult a dermatologist if changes occur.",
                'Dermatosis_Papulosa_Nigra': "No immediate action; consult a dermatologist if removal is desired.",
                'Desquamation': "Moisturize skin and avoid harsh chemicals; keep skin hydrated.",
                'Digital_Fibroma': "Monitor for changes; see a healthcare provider if growth continues.",
                'Dilated_Pore_of_Winer': "No immediate action; consult a dermatologist if removal is desired.",
                'Discoid_Lupus_Erythematosus': "Avoid sun exposure; use prescribed creams if advised.",
                'Disseminated_Actinic_Porokeratosis': "Use sun protection; consult a dermatologist.",
                'Drug_Eruption': "Discontinue suspected medication and consult a healthcare provider.",
                'Dry_Skin_Eczema': "Moisturize frequently; avoid hot water and harsh soaps.",
                'Dyshidrosiform_Eczema': "Apply moisturizer; avoid prolonged water exposure.",
                'Dysplastic_Nevus': "Monitor for changes; consult a dermatologist if changes occur.",
                'Eccrine_Poroma': "No first aid required; consult a dermatologist if bothersome.",
                'Eczema': "Apply hypoallergenic moisturizer and avoid triggers.",
                'Epidermal_Nevus': "No immediate action; consult a dermatologist if treatment is desired.",
                'Epidermoid_Cyst': "Apply a warm compress; avoid squeezing.",
                'Epithelioma_Adenoides_Cysticum': "No immediate first aid needed; monitor for changes.",
                'Erythema_Ab_Igne': "Avoid heat exposure; moisturize affected area.",
                'Erythema_Annulare_Centrifigum': "No immediate first aid; avoid triggers.",
                'Erythema_Craquele': "Apply moisturizing ointment; avoid scratching.",
                'Erythema_Multiforme': "Consult a healthcare provider; avoid triggers if known.",
                'Exfoliative_Erythroderma': "Seek immediate medical assistance for widespread skin peeling.",
                'Factitial_Dermatitis': "Avoid scratching; consult a healthcare provider.",
                'Favre_Racouchot': "Protect skin from sun exposure; use retinoids as prescribed.",
                'Fibroma': "No treatment needed; consult a healthcare provider if it causes discomfort.",
                'Fibroma_Molle': "No first aid required; monitor for any changes."
            }

        first_aid_response = first_aid_responses.get(condition, "No specific first aid advice available for this condition. Please retake your picture to make sure it is not blurred.")
        return jsonify({"condition": condition, "first_aid": first_aid_response})

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"response": "Error processing image."}), 500

if __name__ == "__main__":
    app.run(debug=True)
