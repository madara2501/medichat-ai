import re

def feet_to_cm(feet_value):
    """
    Convert height in feet format to cm.
    Example:
    5.6 feet -> interpreted as 5 feet 6 inches
    """
    feet_int = int(feet_value)
    decimal_part = round((feet_value - feet_int) * 10)

    total_inches = (feet_int * 12) + decimal_part
    return round(total_inches * 2.54, 2)


def extract_bmi_data(user_input):

    text = user_input.lower()

    # FIND WEIGHT
    weight_match = re.search(
        r'(\d+(\.\d+)?)\s*kg',
        text
    )

    # FIND HEIGHT IN CM
    cm_match = re.search(
        r'(\d+(\.\d+)?)\s*cm',
        text
    )

    # FIND HEIGHT IN FEET
    feet_match = re.search(
        r'(\d+(\.\d+)?)\s*(feet|foot|ft)',
        text
    )

    weight = (
        float(weight_match.group(1))
        if weight_match else None
    )

    height_cm = None

    # VALIDATE WEIGHT
    if weight:
        if weight < 10 or weight > 300:
            return None, None

    # HEIGHT IN CM
    if cm_match:

        height_cm = float(
            cm_match.group(1)
        )

        # VALIDATE HUMAN HEIGHT
        if height_cm < 50 or height_cm > 250:
            return None, None

    # HEIGHT IN FEET
    elif feet_match:

        feet_value = float(
            feet_match.group(1)
        )

        # VALID HUMAN HEIGHT
        if feet_value < 1 or feet_value > 8:
            return None, None

        height_cm = feet_to_cm(feet_value)

    return weight, height_cm

def calculate_bmi(weight, height_cm):
    try:
        height_m = height_cm / 100  # Convert cm to meters

        if height_m <= 0:
            return None, None

        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi < 25:
            category = "Normal"
        elif 25 <= bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        return round(bmi, 2), category

    except Exception:
        return None, None