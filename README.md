# Shell & Tube Heat Exchanger Design & performance analysis Suite

A Python script for sizing and analyzing the performance of a shell-and-tube heat exchanger from process and fluid property inputs. It calculates tube-side and shell-side heat transfer coefficients, Nusselt no., Prandtl no., pressure drops, required heat transfer area, number of tubes, shell diameter, and baffle spacing, then prints a complete design report.

## Features

- Material selection (Carbon Steel, Stainless Steel, Copper, or custom thermal conductivity)
- Tube-side heat transfer via Dittus-Boelter correlation (with laminar/transitional handling)
- Shell-side heat transfer via the Kern method
- Iterative solver for shell diameter and baffle spacing (these are interdependent, so the script converges on consistent values rather than guessing)
- Automatic flagging when shell-side flow falls outside the turbulent regime the Kern method is valid for
- Square or triangular tube layout support
- Configurable tube pass count (1, 2, or more)

## How it works

1. You select a tube material (or enter a custom thermal conductivity).
2. You enter the process conditions: hot/cold inlet and outlet temperatures, hot-side mass flow rate and specific heat.
3. You enter tube-side fluid properties and geometry (diameter, density, viscosity, conductivity, fouling factor).
4. You enter shell-side fluid properties, fouling factor, number of tube passes, and layout (square or triangular).
5. The script iteratively solves for shell diameter and baffle spacing, since each depends on the other through the overall heat transfer coefficient.
6. A full design report is printed, including Reynolds/Prandtl/Nusselt numbers, velocities, pressure drops, heat transfer coefficients, and final geometry.

## Requirements

- Python 3.x (no external libraries — uses only the built-in `math` module)

## Usage

```bash
python main.py
```

You'll be prompted interactively for all required inputs.

## Example output

```
--- FINAL DESIGN REPORT ---
Heat Duty: 418000.00 W
LMTD: 54.85 °C
no. of tubes required: 59.00
Total Bundle Surface Area: 11.12 m^2
Required Heat Transfer Area: 10.97 m²

[TUBE SIDE]
Re: 39788.74 | Pr: 5.57 | Nu: 218.77 | vel: 1.60
Pressure Drop: 4224.20 Pa | Coeff (h): 6563.01 W/m²K

[SHELL SIDE]
Re: 1208.68 | Pr: 4.71 | Nu: 29.91 | vel: 0.05
Pressure Drop: 1.32 Pa | Coeff (h): 905.95 W/m²K
Shell Diameter: 0.3506 m | Baffle Spacing: 0.1753 m

Overall Heat Transfer Coefficient (U): 694.42 W/m²K
```

## Notes & limitations

- The Kern method is empirically valid primarily for turbulent shell-side flow (Re typically > ~2,000–10,000 depending on source). The script will print a warning if shell-side Reynolds number falls into the laminar or transitional range, since the correlation becomes less reliable there.
- This is a simplified design tool intended for preliminary sizing and educational use, not a substitute for detailed mechanical design (e.g. TEMA standards, Bell-Delaware method) in production engineering work.

## Licences
This project is for educational purposes. Any modification, redistribution, or commercial use is prohibited without express written permission from the author.
