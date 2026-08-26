import math
import os
import sys
import webbrowser
from pathlib import Path
from material_database import materials
from report_generator import generate_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(BASE_DIR, "designsheet.html")

# Preferred numbers (R20 series) - the standard PSG Design Data Book table
# used to round a calculated dimension up to a real, manufacturable stock
# size, instead of just rounding up to the next whole millimeter.
R20_BASE = [1.00, 1.12, 1.25, 1.40, 1.60, 1.80, 2.00, 2.24, 2.50, 2.80,
            3.15, 3.55, 4.00, 4.50, 5.00, 5.60, 6.30, 7.10, 8.00, 9.00]

PREFERRED_DIAMETERS = (
    [round(v, 2) for v in R20_BASE] +
    [round(v * 10, 1) for v in R20_BASE] +
    [round(v * 100, 1) for v in R20_BASE] +
    [round(v * 1000, 1) for v in R20_BASE]
)

def nearest_standard_diameter(calculated_diameter):
    """Rounds up to the next PSG preferred (R20) diameter."""
    for d in PREFERRED_DIAMETERS:
        if d >= calculated_diameter:
            return d
    return PREFERRED_DIAMETERS[-1]

def get_positive_float(prompt_text):
    while True:
        try:
            val = float(input(prompt_text))
            if math.isnan(val) or math.isinf(val):
                print("Error: Invalid number.")
                continue
            if val <= 0:
                print("Error: Value must be positive.")
                continue
            return val
        except ValueError:
            print("Error: Please enter a numeric value.")


# Print the material property table once, at program start, so it's
# available for reference throughout the session without repeating it
# after every calculation.
print("\nAVAILABLE MATERIALS")
print("{:<18} {:<18} {:<18} {:<15} {:<20}".format(
    "Material", "Yield Strength", "Shear Strength", "Density", "Young's Modulus"
))

print("-"*90)

for m in materials:
    print("{:<18} {:<18} {:<18} {:<15} {:<20}".format(
        m,
        str(materials[m]["yield_strength"]) + " MPa",
        str(materials[m]["shear_strength"]) + " MPa",
        str(materials[m]["density"]) + " kg/m^3",
        str(materials[m]["youngs_modulus"]) + " MPa"
    ))

MATERIAL_MENU = {
    "1": "MILD STEEL", "2": "ALLOY STEEL", "3": "STAINLESS STEEL",
    "4": "ALUMINIUM ALLOY", "5": "TITANIUM ALLOY", "6": "COPPER",
    "7": "BRASS", "8": "BRONZE", "9": "MAGNESIUM ALLOY"
}


while True:

    print("\n===== MACHINE ELEMENT DESIGN CALCULATOR =====")
    print("1. Shaft Design (Torsion)")
    print("2. Bolt Design (Tension)")
    print("3. Key Design")
    print("4. Spring Design")
    print("5. Failure Analysis")
    print("6. Material Analysis")
    print("7. Launch Web Interface")
    print("8. Exit")

    choice = input("Enter your choice: ")

    if choice == "8":
        print("Program Closed")
        break

    if choice == "7":

        if os.path.exists(HTML_PATH):

            webbrowser.open(Path(HTML_PATH).as_uri())
            print("Opening DesignSheet in your browser...")

        else:

            print("designsheet.html not found. Place it in the same folder as main.py")

        continue  

    if choice not in ("1", "2", "3", "4", "5", "6"):
        print("Invalid choice. Please enter a number from the menu above.")
        continue

    print("\nSelect Material")
    print("1. MILD STEEL")
    print("2. ALLOY STEEL")
    print("3. STAINLESS STEEL")
    print("4. ALUMINIUM ALLOY")
    print("5. TITANIUM ALLOY")
    print("6. COPPER")
    print("7. BRASS")
    print("8. BRONZE")
    print("9. MAGNESIUM ALLOY")

    mat_choice = input("Enter material number: ")
    material_name = MATERIAL_MENU.get(mat_choice)

    if material_name is None:
        print("Invalid material. Returning to main menu.")
        continue

    material = materials[material_name]

    # --------------------------------------------------------------
    # 1. SHAFT DESIGN (pure torsion)
    # --------------------------------------------------------------

    if choice == "1":

        print("\n--- SHAFT DESIGN ---")

        torque = get_positive_float("Enter Torque (Nmm): ")
        fos = get_positive_float("Enter Factor of Safety (e.g. 2 or 2.5, no units): ")

        shear_strength = material["shear_strength"]

        # Reduce the material's shear strength by the FOS to get a
        # safe working ("allowable") stress for the calculation.
        allowable_stress = shear_strength / fos

        # Solid shaft torsion formula (T = pi/16 x tau x d^3),
        # rearranged to solve for diameter d.
        diameter = ((16 * torque) / (math.pi * allowable_stress)) ** (1/3)

        # Round up to a real, manufacturable size (PSG preferred
        # number / R20 series) instead of just the next whole mm.
        standard_diameter = nearest_standard_diameter(diameter)
        
        # Calculate actual stress using the selected standard diameter
        actual_stress = (16 * torque) / (math.pi * (standard_diameter**3))
        actual_fos = shear_strength / actual_stress
        
        safe = actual_fos >= fos

        print("\nFormula Used : d = (16 x T / (pi x tau_allow))^(1/3)")

        print("\n------ DESIGN REPORT ------")
        print("Component : Shaft")
        print("Material  :", material_name)
        print("Torque    :", torque, "Nmm")
        print("Required FOS:", fos)

        print("\nAllowable Shear Stress:", round(allowable_stress,2),"MPa")
        print("Required Theoretical Diameter:", round(diameter,2),"mm")
        print("Selected Standard Diameter:", standard_diameter,"mm")
        print("Actual Stress:", round(actual_stress,2), "MPa")
        print("Actual FOS:", round(actual_fos,2))
        if safe:
            print("STATUS: SAFE")
        else:
            print("STATUS: NOT SAFE")

    # --------------------------------------------------------------
    # 2. BOLT DESIGN (axial tension)
    # --------------------------------------------------------------

    elif choice == "2":

        print("\n--- BOLT DESIGN ---")

        force = get_positive_float("Enter Axial Force (N): ")
        fos = get_positive_float("Enter Factor of Safety (e.g. 2 or 2.5, no units): ")

        yield_strength = material["yield_strength"]

        # Safe working stress = yield strength reduced by the FOS.
        allowable_stress = yield_strength / fos

        a_required = force / allowable_stress

        BOLT_TABLE = [
            (6, 20.1), (8, 36.6), (10, 58.0), (12, 84.3),
            (14, 115), (16, 157), (18, 192), (20, 245),
            (22, 303), (24, 353), (27, 459), (30, 561),
            (33, 694), (36, 817)
        ]

        bolt_size = None
        at_selected = None

        for size, area in BOLT_TABLE:
            if area >= a_required:
                bolt_size = size
                at_selected = area
                break

        print("\nFormula Used : A_required = F / sigma_allow")

        print("\n------ DESIGN REPORT ------")
        print("Component : Bolt")
        print("Material  :", material_name)
        print("Axial Force:", force, "N")
        print("Required FOS:", fos)

        print("\nAllowable Tensile Stress:", round(allowable_stress,2),"MPa")
        print("Required Tensile Stress Area:", round(a_required,2),"mm^2")

        if bolt_size is None:
            print("Recommended Bolt Size: Exceeds largest standard size (M36) - reduce force or FOS")
            print("STATUS: NOT SAFE")
        else:
            actual_fos = (at_selected * yield_strength) / force
            print("Recommended Bolt Size: M" + str(bolt_size))
            print("Selected Tensile Area:", at_selected, "mm^2")
            print("Actual FOS:", round(actual_fos,2))
            print("STATUS: SAFE")
        
        print("\nNote: This simplified bolt calculation considers static axial tension only. Bolt preload, joint separation, fatigue, eccentric loading, thread stripping, and combined loading are not evaluated.")

    # --------------------------------------------------------------
    # 3. KEY DESIGN (shear)
    # --------------------------------------------------------------

    elif choice == "3":

        print("\n--- KEY DESIGN ---")
        torque = get_positive_float("Enter Torque (Nmm): ")
        shaft_diameter = get_positive_float("Enter Shaft Diameter (mm): ")
        key_length = get_positive_float("Enter Key Length (mm): ")
        key_width = get_positive_float("Enter Key Width (mm): ")
        key_height = get_positive_float("Enter Key Height (mm): ")
        fos = get_positive_float("Enter FOS (e.g. 2 or 2.5, no units): ")

        shear_strength = material["shear_strength"]
        yield_strength = material["yield_strength"]
        allowable_shear = shear_strength / fos
        allowable_crushing = yield_strength / fos

        shear_stress = (2 * torque) / (shaft_diameter * key_width * key_length)
        crushing_stress = (4 * torque) / (shaft_diameter * key_height * key_length)
        
        shear_fos = shear_strength / shear_stress
        crushing_fos = yield_strength / crushing_stress
        governing_fos = min(shear_fos, crushing_fos)
        
        safe = governing_fos >= fos

        print("\nFormula Used : tau = 2T / (d * w * L), sigma_c = 4T / (d * h * L)")

        print("\n------ DESIGN REPORT ------")
        print("Component : Key")
        print("Material  :", material_name)
        print("Torque    :", torque, "Nmm")
        print("Shaft Dia :", shaft_diameter, "mm")
        print("Key Length:", key_length, "mm")
        print("Key Width :", key_width, "mm")
        print("Key Height:", key_height, "mm")
        print("Required FOS:", fos)
        
        print("\nShear Stress:", round(shear_stress,2), "MPa")
        print("Allowable Shear Stress:", round(allowable_shear,2), "MPa")
        print("Shear FOS:", round(shear_fos,2))
        
        print("\nCrushing Stress:", round(crushing_stress,2), "MPa")
        print("Allowable Crushing Stress:", round(allowable_crushing,2), "MPa")
        print("Crushing FOS:", round(crushing_fos,2))
        
        print("\nGoverning FOS:", round(governing_fos,2))
        
        if safe:
            print("STATUS: SAFE")
        else:
            print("STATUS: NOT SAFE")
        
        print("\nNote: Simplified assumption: allowable crushing stress = material yield strength.")

    # --------------------------------------------------------------
    # 4. SPRING DESIGN
    # --------------------------------------------------------------

    elif choice == "4":
        print("\n--- SPRING DESIGN ---")
        load = get_positive_float("Enter Load (N): ")
        spring_diameter = get_positive_float("Enter Spring Diameter (mm): ")
        wire_diameter = get_positive_float("Enter Wire Diameter (mm): ")
        fos = get_positive_float("Enter Factor of Safety (e.g. 2 or 2.5, no units): ")

        spring_index = spring_diameter / wire_diameter
        if spring_index <= 1:
            print("\nError: Spring Diameter must be greater than Wire Diameter (spring index must exceed 1).")
        else:
            if spring_index < 4 or spring_index > 12:
                print("\nWARNING: Spring index C should ideally be between 4 and 12.")
            
            shear_strength = material["shear_strength"]
            allowable_stress = shear_strength / fos

            # Spring index C = D/d
            spring_index = spring_diameter / wire_diameter

            # Wahl factor Kw
            wahl_factor = ((4 * spring_index - 1) / (4 * spring_index - 4)) + (0.615 / spring_index)
            
            # Raw and Corrected Stress
            raw_stress = (8 * load * spring_diameter) / (math.pi * wire_diameter**3)
            corrected_stress = wahl_factor * raw_stress
            
            actual_fos = shear_strength / corrected_stress
            safe = actual_fos >= fos

            print("\nFormula Used : tau_raw = 8*F*D / (pi*d^3)   |   Kw = (4C-1)/(4C-4) + 0.615/C   |   tau_corrected = Kw * tau_raw")

            print("\n------ DESIGN REPORT ------")
            print("Component      : Spring Design")
            print("Material       :", material_name)
            print("Load           :", load, "N")
            print("Spring Diameter:", spring_diameter, "mm")
            print("Wire Diameter  :", wire_diameter, "mm")
            print("Spring Index   :", round(spring_index,3))
            print("Wahl Factor    :", round(wahl_factor,3))
            print("Required FOS   :", fos)
            print("\nRaw Shear Stress:", round(raw_stress,2), "MPa")
            print("Corrected Shear Stress:", round(corrected_stress,2), "MPa")
            print("Allowable Stress:", round(allowable_stress,2), "MPa")
            print("Actual FOS     :", round(actual_fos,2))

            if safe:
                print("STATUS: SAFE DESIGN")
            else:
                print("STATUS: DESIGN NOT SAFE")
                
            print("\nNote: This simplified spring calculation is a static stress check. Actual spring-wire strength depends on material grade, wire diameter, manufacturing process, and condition. Fatigue life is not evaluated.")

    # --------------------------------------------------------------
    # 5. FAILURE ANALYSIS (static check)
    # --------------------------------------------------------------

    elif choice == "5":
        print("\n--- FAILURE CHECK ---")
        yield_strength = material["yield_strength"]
        applied_stress = get_positive_float("Enter Applied Stress (MPa): ")

        # Factor of Safety = how many times stronger the material
        # is than the stress actually applied to it.
        fos = yield_strength / applied_stress
        print("\nFormula Used : FOS = Sy / sigma_applied")
        print("\n------ DESIGN REPORT ------")
        print("Component      : Failure Analysis")
        print("Material       :", material_name)
        print("Stress Applied :", applied_stress, "MPa")
        print("\nFactor Of Safety: ", round(fos,2))
        if fos < 1:
            print("FAILURE - Material Will Fail!")
        elif fos < 2:
            print("WARNING - Design is not Safe!")
        else:
            print("SAFE - Design is Acceptable!")

    # --------------------------------------------------------------
    # 6. MATERIAL ANALYSIS (full property report)
    # --------------------------------------------------------------

    elif choice == "6":
        print("\n--- MATERIAL ANALYSIS ---")

        applied_stress = get_positive_float("Enter Applied Stress (MPa): ")

        fos = material["yield_strength"] / applied_stress
        print("\nFormula Used : FOS = Sy / sigma_applied")
        generate_report(material_name, material, applied_stress, fos)