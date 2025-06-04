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
   - Computes the corresponding solar zenith angles.
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
  - Also provides a full distribution of all occultation latitudes (2023–2024).

---

## Example Outputs

- **[Latitude vs Time](Latitude_Time_step_1s.png)**  
  All ingress and egress latitudes computed from 2020–2024.

- **[Latitude vs Time (2023–2024)](Latitude_Time_step_1s_starting_2023.png)**  
  Filtered to show only occultations from 2023–2024.

- **[Latitude vs Time (Covered)](Latitude_Time_step_1s_starting_2023_covered.png)**  
  Occultation events with ground station tracking (from OBSWeb) in 2023–2024.

- **[Latitude vs SZA (2020–2024)](Latitude_SZA_step_1s.png)**  
  Tangent-point latitude vs solar zenith angle (SZA) for all occultations.

- **[Latitude vs SZA (2023–2024)](Latitude_SZA_step_1s_starting_2023.png)**  
  Subset showing events from 2023–2024 only.

- **[Latitude vs SZA (Covered)](Latitude_SZA_step_1s_starting_2023_covered.png)**  
  SZA–latitude distribution of events with ground station coverage (2023–2024).

---

## How to Use

1. Download and install the newest [SPICE kernels](https://naif.jpl.nasa.gov/naif/data.html) required for TGO and Mars.

2. Modify the `SPICE_METAKERNEL_PATH` in the scripts to point to your local `.tm` file.

3. Run `Occ_times_spice.py` to compute occultations using SPICE and generate the output file.

4. Run `OPSWeb_requester.py` to fetch ground station tracking times from OPSWeb and generate output files.

5. Run `covered_occultations.py` to filter occultation events by actual coverage and generate plots.



