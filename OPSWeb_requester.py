"""
Author: Michaela Benthaus
Date: 03.06.2025

Description:
    Script to query ESA OPSweb to identify which occultations for TGO-Earth occultation are fully 
    overed by groundstation passes—indicating that telemetry data should be available.

    Occultations are checked for full coverage by groundstation passes that occur before ingress 
    and after egress with a margin of ±10 minutes.

Notes:
    - Only occultations *entirely* within the selected time range are considered.
    - Time format:
        - Occultations are in Spacecraft (SC) time.
        - Passes are in Groundstation (GS) time (with OWLT corrections applied).
    - Excludes unwanted groundstations (KLZ, BLK) and MSPA passes.
"""

from datetime import datetime, timezone, timedelta
import pandas as pd
import requests
from tabulate import tabulate


def opsw_request(start_time, end_time, mission, event_type):
    """Fetch event data from ESA OPSWeb API."""

    time_start = start_time.strftime("ge:%Y-%m-%dT%H:%M:%SZ")
    time_end   = end_time.strftime("le:%Y-%m-%dT%H:%M:%SZ")

    # Here you can set the `url` variable to the OPSweb API endpoint
    # (the line was removed for publication)
    params = {'time_start': time_start, 'time_end': time_end}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("OPSWeb request failed:", response.status_code, response.reason)
        return []

    data = response.json()
    if not data:
        print('No events found in OPSWeb')
        return []

    print("OPSWeb request successful")
    return data


# ------------------------ Configuration ------------------------

start_date_str = "1.1.2020"
end_date_str   = "1.1.2025"

StartTime = datetime.strptime(start_date_str, "%d.%m.%Y").replace(tzinfo=timezone.utc)
EndTime   = datetime.strptime(end_date_str,   "%d.%m.%Y").replace(tzinfo=timezone.utc) + timedelta(hours=23, minutes=59, seconds=59)

mission_name = 'tgo'


# ------------------------ Retrieve Passes ------------------------

event_type = 'passes'
passes = opsw_request(StartTime, EndTime, mission_name, event_type)
df_passes = pd.DataFrame(passes).sort_values(by=['time_end', 'time_start']).reset_index(drop=True)

# Filter out excluded groundstations and MSPA passes:
df_passes = df_passes[~df_passes['groundstation'].isin(['KLZ', 'BLK'])]
df_passes = df_passes[df_passes['mspa'] != 'true']

# Apply OWLT (One-Way Light Time) correction:
df_passes['time_start']      = pd.to_datetime(df_passes['time_start'], utc=True, format='ISO8601')
df_passes['time_end']        = pd.to_datetime(df_passes['time_end'],   utc=True, format='ISO8601')
df_passes['owlt_delta']      = pd.to_timedelta('00:' + df_passes['owlt'])
df_passes['time_start_corr'] = df_passes['time_start'] - df_passes['owlt_delta']
df_passes['time_end_corr']   = df_passes['time_end']   - df_passes['owlt_delta']


# ------------------------ Retrieve Occultations ------------------------

event_type = 'occultations'
occultations = opsw_request(StartTime, EndTime, mission_name, event_type)
df_occ = pd.DataFrame(occultations).sort_values(by=['time_end', 'time_start']).reset_index(drop=True)

df_occ['time_start'] = pd.to_datetime(df_occ['time_start'], utc=True)
df_occ['time_end']   = pd.to_datetime(df_occ['time_end'],   utc=True)


# ------------------------ Check for Coverage ------------------------

covered = []
for _, occ_row in df_occ.iterrows():
    ing_time = occ_row['time_start']
    egr_time = occ_row['time_end']

    # Define ±10 minute windows around ingress and egress:
    ing_start_req = ing_time - timedelta(minutes=10)
    ing_end_req   = ing_time
    egr_start_req = egr_time
    egr_end_req   = egr_time + timedelta(minutes=10)

    mask_ing = (
        (df_passes['time_start_corr'] <= ing_start_req) &
        (df_passes['time_end_corr']   >= ing_end_req)
    )
    mask_egr = (
        (df_passes['time_start_corr'] <= egr_start_req) &
        (df_passes['time_end_corr']   >= egr_end_req)
    )

    # Only include occultation if both ingress and egress are covered:
    if mask_ing.any() and mask_egr.any():
        covered.append({
            'ingress': ing_time,
            'egress':  egr_time
        })

df_covered = pd.DataFrame(covered)


# ------------------------ Format Output ------------------------

fmt = '%Y-%m-%d %H:%M:%S'
df_passes[['time_start', 'time_end', 'time_start_corr', 'time_end_corr']] = (
    df_passes[['time_start', 'time_end', 'time_start_corr', 'time_end_corr']].apply(lambda col: col.dt.strftime(fmt))
)
df_occ[['time_start', 'time_end']] = df_occ[['time_start', 'time_end']].apply(lambda col: col.dt.strftime(fmt))
df_covered[['ingress', 'egress']] = df_covered[['ingress', 'egress']].apply(lambda col: col.dt.strftime(fmt))

print("Valid passes:\n", df_passes)
print("Covered occultations:\n", df_covered)


# ------------------------ Save to Files ------------------------

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def save_table(df, filename, header):
    table_str = tabulate(df.values, df.columns, tablefmt="plain", showindex=False, stralign="left")
    with open(filename, "w") as f:
        f.write(f"{header}: {ts}\n\n")
        f.write(table_str)

save_table(df_covered,      "opsweb_covered.txt",      "Covered occultations (UTC)")
save_table(df_occ,          "opsweb_occultations.txt", "All occultations (UTC)")
save_table(df_passes,       "opsweb_passes.txt",       "Valid passes (UTC)")
