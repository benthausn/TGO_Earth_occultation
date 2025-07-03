# ExoMars TGO Occultation Analysis with SPICE and OPSWeb

This repository contains tools for analyzing ExoMars Trace Gas Orbiter (TGO) occultation events 
using the SPICE toolkit and ground station pass data from OPSWeb (ESA tool). The results are 
presented at European Science Congress (EPSC) 2025. 

The goal of this project is to:

- Simulate occultation events between TGO and Earth using SPICE.
- Identify which of these are covered by ground station passes, indicating where real data exists.
- Visualize ingress and egress latitudes as a function of time and solar zenith angle, both for 
  all occultations and for those with available ground station coverage.

The code in this repository is licensed under MIT. See the LICENSE file for details.

---

## Repository Contents

1. `Occ_times_spice_parallel.py`

   - Computes occultation events (ingress/egress) between TGO and Earth using SPICE.
   - Determines the latitude and longitude of tangent points where the signal path grazes Mars.
   - Computes the corresponding solar zenith angles (SZA) and solar longitudes (Ls).
   - Outputs results in `Occultations_spice.txt`.

2. `OPSWeb_requester.py`

   - Queries ESA's OPSWeb for:
     - All occultation events
     - Ground station passes
   - Filters events where both ingress and egress are covered (±10 min margin).
   - Outputs to:  
     - `opsweb_covered.txt`  
     - `opsweb_occultations.txt`  
     - `opsweb_passes.txt`

3. `covered_occultations.py`

  - Compares SPICE-simulated occultations with covered ones from `opsweb_covered.txt`.
  - Plots only ingress/egress latitudes (as a function of time and SZA) where ground 
    station coverage exists.
  - Plots covered ingress/ egress latitudes as a function of SZA colorcoeded by Ls. 
  - Also provides a full distribution of all occultation latitudes (2023–2024).

---

## Example Outputs

> **Note:** All simulations for the example outputs are conducted with **1 s** time steps.
> Dates before **2023‑01‑01** have `mspa = NaN` (multiple‑spacecraft‑per‑aperture) and are therefore skipped, so coverage data is only available from the beginning of 2023 onward.  
> Since `mspa` reflects cases where more than one spacecraft uses a ground station — allowing multiple downlinks but only one uplink — it is unknown whether TGO received an uplink before 2023.

- **[Latitude vs Time (2020–2024)](Latitude_Time.png)**  
  Ingress & egress latitudes vs. time for 2020–2024.

- **[Latitude vs Time (2023–2024)](Latitude_Time_starting_2023.png)**  
  Ingress & egress latitudes vs. time for 2023–2024.

- **[Latitude vs Time (2023–2024, Covered)](Latitude_Time_starting_2023_covered.png)**  
  Ingress & egress latitudes vs. time with ground‑station coverage for 2023–2024.

- **[Latitude vs SZA (2020–2024)](Latitude_SZA.png)**  
  Ingress & egress latitudes vs. solar‑zenith angle for 2020–2024.

- **[Latitude vs SZA (2023–2024)](Latitude_SZA_starting_2023.png)**  
  Ingress & egress latitudes vs. solar‑zenith angle for 2023–2024.

- **[Latitude vs SZA (2023–2024, Covered)](Latitude_SZA_starting_2023_covered.png)**  
  Ingress & egress latitudes vs. solar‑zenith angle with ground‑station coverage for 2023–2024.

- **[Latitude vs SZA (2023–2024, Covered), color‑coded by Ls](Latitude_SZA_starting_2023_covered_Ls.png)**  
  Ingress & egress latitudes vs. solar‑zenith angle with ground‑station coverage, color‑coded by solar longitude for 2023–2024.

---

## How to Use

1. Download and install the newest [SPICE kernels](https://naif.jpl.nasa.gov/naif/data.html) required for TGO and Mars (ExoMars).

2. Modify the `SPICE_METAKERNEL_PATH` in the scripts to point to your local `.tm` file.

3. Run `Occ_times_spice.py` to compute occultations using SPICE and generate the output file.

4. Run `OPSWeb_requester.py` to fetch ground station tracking times from OPSWeb and generate output files.

5. Run `covered_occultations.py` to filter occultation events by actual coverage and generate plots.



