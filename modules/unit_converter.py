def convert_units(value, category, unit_from, unit_to):
    if value is None:
        return "Please enter a numeric value."
    if not unit_from or not unit_to:
        return "Please specify both 'From Unit' and 'To Unit'."

    try:
        val = float(value)
    except ValueError:
        return "Invalid numeric input."

    u_from = str(unit_from).strip().lower()
    u_to = str(unit_to).strip().lower()
    cat = str(category).strip().lower()

    # --- LENGTH CONVERSIONS (Base: meters) ---
    length_factors = {
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "in": 0.0254, "inch": 0.0254, "inches": 0.0254,
        "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
        "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
        "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    }

    # --- WEIGHT CONVERSIONS (Base: kilograms) ---
    weight_factors = {
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 0.000001, "milligram": 0.000001, "milligrams": 0.000001,
        "lb": 0.453592, "lbs": 0.453592, "pound": 0.453592, "pounds": 0.453592,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
    }

    if cat == "length":
        if u_from not in length_factors or u_to not in length_factors:
            return f"Unsupported length units. Supported: {', '.join(sorted(set(['m', 'cm', 'mm', 'km', 'in', 'ft', 'yd', 'mi'])))}"
        base_val = val * length_factors[u_from]
        res = base_val / length_factors[u_to]
        return f"{val} {unit_from} = {res:.6g} {unit_to}"

    elif cat == "weight":
        if u_from not in weight_factors or u_to not in weight_factors:
            return f"Unsupported weight units. Supported: {', '.join(sorted(set(['kg', 'g', 'mg', 'lb', 'oz'])))}"
        base_val = val * weight_factors[u_from]
        res = base_val / weight_factors[u_to]
        return f"{val} {unit_from} = {res:.6g} {unit_to}"

    elif cat == "temperature":
        # Standardize temperature names
        def normalize_temp(u):
            if u in ["c", "celsius", "°c"]:
                return "c"
            if u in ["f", "fahrenheit", "°f"]:
                return "f"
            if u in ["k", "kelvin"]:
                return "k"
            return None

        t_from = normalize_temp(u_from)
        t_to = normalize_temp(u_to)

        if not t_from or not t_to:
            return "Unsupported temperature units. Supported: C, F, K"

        # Convert to Celsius first
        if t_from == "c":
            c_val = val
        elif t_from == "f":
            c_val = (val - 32) * 5 / 9
        elif t_from == "k":
            c_val = val - 273.15

        # Convert Celsius to Target
        if t_to == "c":
            res = c_val
        elif t_to == "f":
            res = (c_val * 9 / 5) + 32
        elif t_to == "k":
            res = c_val + 273.15

        return f"{val} {unit_from.upper()} = {res:.4f} {unit_to.upper()}"

    return "Select a valid category (Length, Weight, or Temperature)."