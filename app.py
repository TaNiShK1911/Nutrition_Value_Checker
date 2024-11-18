from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
import io
import re

# Nutritional Scoring system
class NutritionalValue:
    def __init__(self, energy, protein, total_fat, saturated_fat, trans_fat, carbohydrates, sugars, dietary_fiber, sodium, cholesterol):
        self.energy = energy
        self.protein = protein
        self.total_fat = total_fat
        self.saturated_fat = saturated_fat
        self.trans_fat = trans_fat
        self.carbohydrates = carbohydrates
        self.sugars = sugars
        self.dietary_fiber = dietary_fiber
        self.sodium = sodium  # in mg
        self.cholesterol = cholesterol  # in mg

# Standard nutritional values per 100 grams
standard_values = NutritionalValue(
    energy=250, protein=15, total_fat=10, saturated_fat=3,
    trans_fat=0, carbohydrates=50, sugars=15, dietary_fiber=5,
    sodium=1000, cholesterol=20
)

# Weights for each nutritional value
weights = {
    'energy': 1.0, 'protein': 2.0, 'total_fat': 1.5, 'saturated_fat': 1.5,
    'trans_fat': 2.0, 'carbohydrates': 1.0, 'sugars': 1.0,
    'dietary_fiber': 2.0, 'sodium': 1.5, 'cholesterol': 1.0
}

def calculate_score(input_values):
    total_weight = sum(weights.values())
    score = 0
    input_sodium_mg = input_values.sodium
    criteria_results = {
        'energy': input_values.energy <= standard_values.energy,
        'protein': input_values.protein >= standard_values.protein,
        'total_fat': input_values.total_fat <= standard_values.total_fat,
        'saturated_fat': input_values.saturated_fat <= standard_values.saturated_fat,
        'trans_fat': input_values.trans_fat <= standard_values.trans_fat,
        'carbohydrates': input_values.carbohydrates <= standard_values.carbohydrates,
        'sugars': input_values.sugars <= standard_values.sugars,
        'dietary_fiber': input_values.dietary_fiber >= standard_values.dietary_fiber,
        'sodium': input_sodium_mg <= standard_values.sodium,
        'cholesterol': input_values.cholesterol <= standard_values.cholesterol,
    }

    for nutrient, result in criteria_results.items():
        if result:
            score += weights[nutrient]

    return (score / total_weight) * 100  # Normalize score to a percentage

def parse_nutritional_info(text):
    """Extract numerical nutritional values from the OCR text."""
    nutrients = {
        'energy': 0, 'protein': 0, 'total_fat': 0, 'saturated_fat': 0,
        'trans_fat': 0, 'carbohydrates': 0, 'sugars': 0, 'dietary_fiber': 0,
        'sodium': 0, 'cholesterol': 0
    }

    # Regex patterns for capturing nutritional values
    patterns = {
        'energy': r'(\d+)\s*kcal',
        'protein': r'Protein\s*(\d+)',
        'total_fat': r'Total Fat\s*(\d+)',
        'saturated_fat': r'Saturated Fat\s*(\d+)',
        'trans_fat': r'Trans Fat\s*(\d+)',
        'carbohydrates': r'Carbohydrates\s*(\d+)',
        'sugars': r'Sugars\s*(\d+)',
        'dietary_fiber': r'Dietary Fiber\s*(\d+)',
        'sodium': r'Sodium\s*(\d+)',
        'cholesterol': r'Cholesterol\s*(\d+)'
    }

    for nutrient, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nutrients[nutrient] = float(match.group(1))

    return NutritionalValue(
        energy=nutrients['energy'],
        protein=nutrients['protein'],
        total_fat=nutrients['total_fat'],
        saturated_fat=nutrients['saturated_fat'],
        trans_fat=nutrients['trans_fat'],
        carbohydrates=nutrients['carbohydrates'],
        sugars=nutrients['sugars'],
        dietary_fiber=nutrients['dietary_fiber'],
        sodium=nutrients['sodium'],
        cholesterol=nutrients['cholesterol']
    )

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    if not image_file:
        return jsonify({"error": "No image uploaded"}), 400

    # Open the image file
    image = Image.open(io.BytesIO(image_file.read()))

    # Perform OCR on the image
    ocr_text = pytesseract.image_to_string(image)

    # Debugging: Print the OCR text to check what's being extracted
    print("OCR Extracted Text:", ocr_text)

    # Parse nutritional information from the OCR result
    nutritional_values = parse_nutritional_info(ocr_text)

    # Debugging: Print the parsed nutritional values
    print("Parsed Nutritional Values:", nutritional_values.__dict__)

    # Calculate the nutritional score
    score = calculate_score(nutritional_values)

    # Debugging: Print the calculated score
    print("Calculated Score:", score)

    # Return the score and evaluation to the frontend
    return jsonify({
        "score": score,
        "nutritional_info": ocr_text  # Optional: Return the extracted text for the frontend to display
    })

if __name__ == "__main__":
    app.run(debug=True)
