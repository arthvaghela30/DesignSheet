# DesignSheet — Machine Element Design Calculator

A machine element design calculator covering shaft, bolt, key, and spring design, plus static failure and material analysis, with a companion web interface, built with a clean dark industrial aesthetic.

## Features
- **Shaft Design** — torsion-based diameter calculation, rounded up to real manufacturable sizes using the PSG preferred number (R20) series
- **Bolt Design** — axial tension sizing against a standard metric bolt tensile-area table (M6–M36)
- **Key Design** — shear and crushing stress checks with a governing factor of safety
- **Spring Design** — corrected shear stress using the Wahl factor, with spring index validation
- **Failure Analysis** — quick factor-of-safety check against applied stress
- **Material Analysis** — full property report (yield strength, shear strength, density, Young's modulus) for 9 common engineering materials
- Web-based interface launched directly from the CLI using the `webbrowser` module
- Regression test suite validating the design formulas against known correct outputs

## Tech Stack
- **Python** — core design calculations and material database
- **HTML/CSS** — dark industrial-themed web interface
- **webbrowser module** — launches the interface directly in the browser

## Project Structure
```
designsheet/
├── main.py                 # CLI menu and all design calculations
├── material_database.py    # Material property data (9 materials)
├── report_generator.py     # Formatted material analysis report
├── designsheet.html         # Dark industrial-themed web interface
├── test_regression.py      # Regression tests for design formulas
└── README.md
```

## Future Improvements
- Add more machine element categories (bearings, gears, welded joints)
- Fatigue life estimation for spring and shaft design
- Export calculation reports as PDF
