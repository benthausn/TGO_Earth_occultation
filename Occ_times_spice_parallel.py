"""
Author: Michaela Benthaus
Date: 02.07.2025

Description:
    Computes occultation events (ingress and egress) for ExoMars TGO using SPICE,
    identifying when the impact parameter crosses the Mars radius.
    Results include UTC time, latitude, longitude, solar zenith angle (SZA) and solar longitude (Ls).
    Computation is parallelized using multiple CPU cores to reduce runtime.
"""

import numpy as np
import spiceypy as spice
import pandas as pd
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from datetime import datetime, timezone
from tabulate import tabulate

# ------------------------ SPICE Setup ------------------------

SPICE_METAKERNEL_PATH = r'C:\Spice\exomars2016\kernels\mk\em16_ops.tm'

class SpiceVariables:
    mars_id = 'MARS'
    frame = 'IAU_MARS'
    tgo_hga_id = '-143025'  # High gain antenna 
    earth_id = '399'
sv = SpiceVariables()

MARS_RADIUS = 3397.515  # km

def load_kernels():
    """
    - Unload kernels everytime since because SPICE maintains an internal list of all loaded kernels and 
      even if a kernel is re-loaded, it is not replaced!
    - Order of the loaded SPICE kernels is important because of dependencies and since certain kernels 
      may override others!
    - Metakernel -> Allows to load all required SPICE kernels with a single command (furnsh) by pointing 
      to this list how the kernels need to be loaded! 
    """
    spice.kclear()
    spice.furnsh(SPICE_METAKERNEL_PATH)

load_kernels()

# ------------------------ Configuration ------------------------

T0_UTC = '2020-01-01T00:00:00.000'
T1_UTC = '2024-12-31T23:59:59.000'
STEP = 1  # seconds
start_et = spice.str2et(T0_UTC)
end_et = spice.str2et(T1_UTC)


def init_spice():
    load_kernels()


def compute_tangent_params(et, gs_id):
    """
    Computation of impact parameters and tangent points.
    """
    try:
        ray = spice.spkpos(gs_id, et, sv.frame, 'CN+S', sv.tgo_hga_id)[0]
        tanpt, *_ = spice.tangpt('ELLIPSOID', 'MARS', et, sv.frame, 'CN+S',
                                 'TANGENT POINT', sv.tgo_hga_id, sv.frame, ray)
        ip = np.linalg.norm(tanpt)
        sun_vec = spice.spkpos('SUN', et, sv.frame, 'NONE', sv.mars_id)[0]
        sza = np.rad2deg(spice.vsep(sun_vec, tanpt))
        return et, ip, tanpt, sza
    except spice.stypes.SpiceyError:
        return None



def find_occultations_parallel(gs_id, start_et, end_et, step, n_procs=4):
    """
    Identifies TGO–Earth radio occultation events by detecting when the impact 
    parameter crosses the Mars mean radius.

    For each ingress and egress, computes:
    - Time (ET and UTC)
    - Tangent point latitude and longitude
    - Solar Zenith Angle (SZA)
    """
    et_list = np.arange(start_et, end_et, step)
    worker = partial(compute_tangent_params, gs_id=gs_id)

    with ProcessPoolExecutor(max_workers=n_procs, initializer=init_spice) as executor:
        results = list(executor.map(worker, et_list, chunksize=500))

    valid = [r for r in results if r]
    et_vals, impact_params, tanpts, szas = zip(*valid)

    et_vals = np.array(et_vals)
    impact_params = np.array(impact_params)
    tanpts = np.array(tanpts)
    szas = np.array(szas)

    ing_mask = (impact_params[:-1] > MARS_RADIUS) & (impact_params[1:] <= MARS_RADIUS)  # ingress
    egr_mask = (impact_params[:-1] <= MARS_RADIUS) & (impact_params[1:] > MARS_RADIUS)  # egress

    ingress, egress = [], []
    for mask, out in [(ing_mask, ingress), (egr_mask, egress)]:
        for idx in np.where(mask)[0] + 1:
            t_et = et_vals[idx]
            _, lon, lat = spice.reclat(tanpts[idx])
            sza = szas[idx]
            ls_deg = np.degrees(spice.lspcn('MARS', t_et, 'LT+S')) % 360  # Solar longitude in deg
            out.append((t_et, np.degrees(lon), np.degrees(lat), sza, ls_deg))

    df_ing = pd.DataFrame(ingress, columns=['ET', 'Longitude (deg)', 'Latitude (deg)', 'SZA (deg)', 'Ingress Ls (deg)'])
    df_ing['Ingress UTC'] = spice.et2utc(df_ing['ET'].tolist(), 'ISOC', 3)

    df_egr = pd.DataFrame(egress, columns=['ET', 'Longitude (deg)', 'Latitude (deg)', 'SZA (deg)', 'Egress Ls (deg)'])
    df_egr['Egress UTC'] = spice.et2utc(df_egr['ET'].tolist(), 'ISOC', 3)

    return df_ing, df_egr



if __name__ == '__main__':
    start_time = time.time()

    df_ingress, df_egress = find_occultations_parallel(
        sv.earth_id, start_et, end_et, STEP
    )


  # ------------------- Format Output -------------------
    ing = df_ingress[['Ingress UTC', 'Latitude (deg)', 'Longitude (deg)', 'SZA (deg)', 'Ingress Ls (deg)']].reset_index(drop=True)
    eg = df_egress[['Egress UTC', 'Latitude (deg)', 'Longitude (deg)', 'SZA (deg)', 'Egress Ls (deg)']].reset_index(drop=True)

    ing.columns = ['Ingress UTC', 'Ingress Lat (deg)', 'Longitude (deg)', 'Ingress SZA (deg)', 'Ingress Ls (deg)']
    eg.columns  = ['Egress UTC',  'Egress Lat (deg)', 'Longitude (deg)', 'Egress SZA (deg)', 'Egress Ls (deg)']

    df_wide = pd.concat([ing, eg], axis=1)

    wide_txt = tabulate(
        df_wide.values,
        df_wide.columns,
        tablefmt="plain",
        showindex=False,
        stralign="left"
    )

    # ------------------- Save to File -------------------

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open("Occultations_spice.txt", "w") as f:
        f.write(f"Created on (UTC): {ts}\n\n")
        f.write(wide_txt + "\n")


