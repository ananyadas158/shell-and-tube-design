import math

# --- Constants & Material Data ---
MATERIALS = {
    '1': {'name': 'Carbon Steel', 'cost': 1, 'k': 50.0},
    '2': {'name': 'Stainless Steel', 'cost': 3, 'k': 16.0},
    '3': {'name': 'Copper', 'cost': 5, 'k': 390.0}
}

def print_material_menu():
    print("\n--- Available Materials ---")
    for k, v in MATERIALS.items():
        print(f"[{k}] {v['name']} (Cost Index: {v['cost']}, Thermal Cond: {v['k']} W/mK)")

def run_design_suite():
    print("--- Shell & Tube Design Suite ---")
    print_material_menu()
    print("[4] Other (Manually enter thermal conductivity)")
    
    mat_choice = input("\nSelect material (1-4): ")
    if mat_choice == '4':
        k_val = float(input("Enter custom thermal conductivity (k) for your material (W/mK): "))
        mat = {'name': 'Custom Material', 'k': k_val}
    else:
        # Default to choice or fallback to Carbon Steel
        mat = MATERIALS.get(mat_choice, MATERIALS['1'])
    
    print(f"Selected: {mat['name']} (k={mat['k']})")
    
    # Process Inputs
    print("\n--- Process Inputs ---")
    Th_in, Th_out = float(input("Hot In (°C): ")), float(input("Hot Out (°C): "))
    Tc_in, Tc_out = float(input("Cold In (°C): ")), float(input("Cold Out (°C): "))
    m_h, cp_h = float(input("Hot Mass flow (kg/s): ")), float(input("Hot Cp (J/kgK): "))
    cp_t=float(input("specific heat capacity for tube side (J/kg): "))
    cp_s=float(input("specific heat capacity for shell side (J/kg): "))
    
    Q = m_h * cp_h * abs(Th_in - Th_out)
    lmtd = ((Th_in - Tc_out) - (Th_out - Tc_in)) / math.log((Th_in - Tc_out) / (Th_out - Tc_in))
    
    L = float(input("Tube Length (m): "))

    # Tube-side
    print("\n--- Tube-side Inputs ---")
    d_tube, rho_t, mu_t, m_t = float(input("Inner Diameter (m): ")), float(input("Density (kg/m3): ")), float(input("Viscosity (Pa.s): ")), float(input("Mass flow rate (kg/s): "))
    d_o=float(input("outer diameter of tube(m): "))
    k_t=float(input("thermal conductivity of fluid in tubes (W/mK): "))
    Rf_t = float(input("Possible Fouling Factor inside surface (m²K/W): "))
    tube_area = (math.pi * (d_tube**2)) / 4
    v_t = m_t / (rho_t * tube_area)
    re_t = (4 * m_t) / (math.pi * d_tube * mu_t)
    pr_t = (mu_t * cp_t) / k_t 

    # Pressure drop (Fanning friction factor approximation)
    f_t = 0.046 * (re_t**-0.2) if re_t > 2300 else 16/re_t
    dp_t = 4*f_t * (L / d_tube) * (rho_t * (v_t**2) / 2)

    # Nusselt and Heat Transfer
    if re_t > 10000:
        nu_t = 0.023 * (re_t**0.8) * (pr_t**0.4)
        print(f"Dittus-Boelter equation is used for calculations")
    elif re_t < 2300:
        nu_t = 4.36
        print(f"Laminar approximation")
    else:
        nu_t = 0.023 * (re_t**0.8) * (pr_t**0.4)
        print(f"!!! WARNING: Tube-side flow is TRANSITIONAL (Re={re_t:.0f}).")
    h_t = (nu_t * k_t) / d_tube

    # Shell-side (Kern Method)
    print("\n--- Shell-side Inputs ---")
    rho_s, mu_s, m_s = float(input("Density (kg/m3): ")), float(input("Viscosity (Pa.s): ")), float(input("Mass flow rate (kg/s): "))
    k_s=float(input("thermal conductivity of fluid in shell (W/mK): "))
    Rf_s = float(input("Possible Fouling Factor outside surface (shell side) (m²K/W): "))
    pitch = 1.25 * d_tube
    passes = int(input("Enter number of tube passes (e.g., 1, 2, 4): "))
    if passes == 1:
        K = 0.40
    elif passes <= 2:
        K = 0.30
    else:
        K = 0.25 
    layout = input("Enter tube layout (square/triangular): ")

    if layout == "triangular":
        d_e = (4 * (0.866 * pitch**2 - 0.125 * 3.14 * d_tube**2)) / (0.5 * 3.14 * d_tube)
    else:
    # Default to square
        d_e = (4 * (pitch**2 - 0.785 * d_tube**2)) / (3.14 * d_tube)

    area_guess = Q / ((1 / h_t) * lmtd) if False else None  # placeholder not used; real guess below
    num_tubes = max(1, math.ceil((Q / (lmtd * 500)) / (math.pi * d_tube * L)))  # rough initial guess assuming U ~ 500 W/m2K
    d_shell = d_tube * ((num_tubes / K)**0.5) * (pitch / d_tube)
    baffle_sp = 0.5 * d_shell  # initial guess, refined below

    for iteration in range(15):
        v_s = m_s / (rho_s * (d_shell * baffle_sp))
        pr_s = (mu_s * cp_s) / k_s
        re_s = (rho_s * v_s * d_e) / mu_s

        if re_s > 10000:
            nu_s = 0.36 * (re_s**0.55) * (pr_s**(1/3))
        else:
            nu_s = 0.36 * (re_s**0.55) * (pr_s**(1/3))  # Kern approximation used regardless; flagged below if laminar

        h_s = (nu_s * k_s) / d_e

        U = 1 / (
            (1/h_t)
            + Rf_t
            + (d_tube * math.log(d_o / d_tube)) / (2 * mat['k'])
            + (d_tube/d_o) * Rf_s
            + (d_tube/d_o) * (1/h_s))

        area = Q / (U * lmtd)
        new_num_tubes = math.ceil(area / (math.pi * d_tube * L))
        new_d_shell = d_tube * ((new_num_tubes / K)**0.5) * (pitch / d_tube)
        new_baffle_sp = 0.5 * new_d_shell

        # Check convergence
        if abs(new_d_shell - d_shell) < 1e-4 and new_num_tubes == num_tubes:
            num_tubes, d_shell, baffle_sp = new_num_tubes, new_d_shell, new_baffle_sp
            break

        num_tubes, d_shell, baffle_sp = new_num_tubes, new_d_shell, new_baffle_sp

    if re_s > 10000:
        print(f"Using Kerns method")
    else:
        print(f"!!! WARNING: Shell-side flow is LAMINAR (Re={re_s:.0f}). Kern method may be inaccurate.")

    # Using common approximation for shell-side pressure drop
    dp_s = 0.36 * (re_s**-0.55) * (L / d_e) * (rho_s * (v_s**2) / 2)

    print(f"Converged after {iteration+1} iteration(s) — Baffle Spacing: {baffle_sp:.4f} m, Shell Diameter: {d_shell:.4f} m")

    # Final Report
    print(f"\n" + "="*30)
    print(f"--- FINAL DESIGN REPORT ---")
    print(f"Heat Duty: {Q:.2f} W")
    print(f"LMTD: {lmtd:.2f} °C")
    print(f"no. of tubes required: {num_tubes:.2f}")
    print(f"Total Bundle Surface Area: {num_tubes * math.pi * d_tube * L:.2f} m^2")
    print(f"Required Heat Transfer Area: {area:.2f} m²")
    print(f"\n[TUBE SIDE]")
    print(f"Re: {re_t:.2f} | Pr: {pr_t:.2f} | Nu: {nu_t:.2f} | vel: {v_t:.2f}")
    print(f"Pressure Drop: {dp_t:.2f} Pa | Coeff (h): {h_t:.2f} W/m²K")
    print(f"\n[SHELL SIDE]")
    print(f"Re: {re_s:.2f} | Pr: {pr_s:.2f} | Nu: {nu_s:.2f} | vel: {v_s:.2f}")
    print(f"Pressure Drop: {dp_s:.2f} Pa | Coeff (h): {h_s:.2f} W/m²K")
    print(f"Shell Diameter: {d_shell:.4f} m | Baffle Spacing: {baffle_sp:.4f} m")
    print(f"\nOverall Heat Transfer Coefficient (U): {U:.2f} W/m²K")
    print("="*30)

if __name__ == "__main__":
    run_design_suite()