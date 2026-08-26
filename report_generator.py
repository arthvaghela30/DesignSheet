def generate_report(material_name, material, applied_stress, fos):

    print("\n---------------------------------")
    print("     MECHANICAL ANALYSIS REPORT")
    print("---------------------------------")

    print("\nMaterial:", material_name)

    print("\nMaterial Properties")
    print("-------------------")
    print("Yield Strength:", material["yield_strength"], "MPa")
    print("Shear Strength:", material["shear_strength"], "MPa")
    print("Density:", material["density"], "kg/m^3")
    print("Young's Modulus:", material["youngs_modulus"], "MPa")

    print("\nApplied Stress:", applied_stress, "MPa")
    print("\nFactor of Safety:", round(fos,2))

    print("\nResult")
    print("------")

    if fos < 1:
        print("FAILURE: Material will fail")
    elif fos < 2:
        print("WARNING: Design is risky")
    else:
        print("SAFE: Design acceptable")

    print("---------------------------------")