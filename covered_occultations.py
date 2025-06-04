'''
Author: Michaela Benthaus 
Date: 25.05.2025

Script to compare ground-station-covered occultation times (from OBSWeb) with simulated
occultation events computed using SPICE. It extracts and plots only the ingress and egress 
latitudes for which actual observational data is available, which means confirmed 
ground station access to TGO are plotted.

ATTENTION:
    Basically all dates before 1.1.2023 have mspa = nan, thus they are skipped.
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

OBSWEB_FILE = 'opsweb_covered.txt'
SPICE_FILE = 'Occultations_spice.txt'    

df_obsweb = pd.read_csv(
    OBSWEB_FILE,
    skiprows=2,                   
    sep=r"\s{2,}",               
    engine="python",              
    parse_dates=[                 # parse the date columns back to datetime64
        "ingress",
        "egress",
    ],
)

df_spice = pd.read_csv(
    SPICE_FILE,
    skiprows=2,
    sep=r"\s{2,}",
    engine="python",
    parse_dates=["Ingress UTC","Egress UTC"]
)
df_spice = df_spice[
    (df_spice['Ingress UTC'] >= "2023-01-01") &
    (df_spice['Ingress UTC'] <  "2025-01-01")
]


tolerance = pd.Timedelta(seconds=60)   # Tolerated time offset since OBSWeb and SPICE occultations don't match exactly.

merged = pd.merge_asof(
    df_spice,
    df_obsweb,
    left_on='Ingress UTC',
    right_on='ingress',
    direction='nearest',
    tolerance=tolerance,
    suffixes=('_spice', '_obsw')
)

# Drop any spice rows that found no obsweb match:
merged = merged.dropna(subset=['ingress'])

spice_covered = merged[
    ['Ingress UTC',  'Ingress Lat (deg)', 'Ingress SZA (deg)',  'Egress UTC', 'Egress Lat (deg)', 'Egress SZA (deg)']
].copy()


# Percent covered occultations:

total_occ = len(df_spice)
covered_occ = len(spice_covered)
coverage_pct = covered_occ / total_occ * 100

print(f"Occultations in Spice file: {total_occ}")
print(f"Occultations covered by obsweb: {covered_occ}")
print(f"Percent: {coverage_pct:.1f}%")


#---------------------- PLOTS ------------------------

# Latitude vs time:

n_ingress = len(df_spice['Ingress UTC'])
n_egress  = len(df_spice['Egress UTC'])
label_ing = f'Ingress Points (N={n_ingress})'
label_egr = f'Egress Points (N={n_egress})'

plt.figure(figsize=(10, 6))
plt.scatter(
    df_spice['Ingress UTC'],
    df_spice['Ingress Lat (deg)'],
    facecolors='none',     # no fill
    edgecolors='blue',     # circle outline color
    s=10,                  # adjust marker size
    linewidths=1,          # outline thickness
    label=label_ing
)
plt.scatter(
    df_spice['Egress UTC'],
    df_spice['Egress Lat (deg)'],
    facecolors='none',
    edgecolors='red',
    s=10,
    linewidths=1,
    label=label_egr
)
plt.xlabel('Date', size=13)
plt.ylabel('Mars latitude [deg]', size=13)
plt.title('Spatiotemporal Distribution of TGO–Earth Occultation Tangent-Point Latitudes', size=15)
plt.grid(color="gray", linestyle="dotted", linewidth=0.5)
plt.legend(loc='upper right', bbox_to_anchor=(0.81, 1))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Set date formatter to show year-month-day
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))  # interval=3 for 2020-2024, =2 for 2023-2024
plt.gcf().autofmt_xdate()  # auto-rotate date labels
plt.xlim(df_spice['Ingress UTC'].min(), df_spice['Ingress UTC'].max())
plt.ylim(-90, 90)
plt.tight_layout()
plt.show()



n_ingress = len(spice_covered['Ingress UTC'])
n_egress  = len(spice_covered['Egress UTC'])
label_ing = f'Ingress Points (N={n_ingress})'
label_egr = f'Egress Points (N={n_egress})'

plt.figure(figsize=(10, 6))
plt.scatter(
    spice_covered['Ingress UTC'],
    spice_covered['Ingress Lat (deg)'],
    facecolors='none',     # no fill
    edgecolors='blue',     # circle outline color
    s=10,                  # adjust marker size
    linewidths=1,          # outline thickness
    label=label_ing
)
plt.scatter(
    spice_covered['Egress UTC'],
    spice_covered['Egress Lat (deg)'],
    facecolors='none',
    edgecolors='red',
    s=10,
    linewidths=1,
    label=label_egr
)
plt.xlabel('Date', size=13)
plt.ylabel('Mars latitude [deg]', size=13)
plt.title('Spatiotemporal Distribution of TGO–Earth Occultations Tangent-Point Latitudes \n Covered by Ground Stations',size=15)
plt.grid(color="gray", linestyle="dotted", linewidth=0.5)
plt.legend(loc='upper right', bbox_to_anchor=(0.81, 1))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Set date formatter to show year-month-day
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()  # auto-rotate date labels
plt.xlim(spice_covered ['Ingress UTC'].min(), spice_covered ['Ingress UTC'].max())
plt.ylim(-90, 90)
plt.tight_layout()
plt.show()



# Latitude vs SZA:

n_ingress = len(df_spice['Ingress SZA (deg)'])
n_egress  = len(df_spice['Egress SZA (deg)'])
label_ing = f'Ingress Points \n  (N={n_ingress})'
label_egr = f'Egress Points \n  (N={n_egress})'

plt.figure(figsize=(10, 6))
plt.scatter(
    df_spice['Ingress SZA (deg)'],
    df_spice['Ingress Lat (deg)'],
    facecolors='none',     # no fill
    edgecolors='blue',     # circle outline color
    s=10,                  # adjust marker size
    linewidths=1,          # outline thickness
    label=label_ing
)
plt.scatter(
    df_spice['Egress SZA (deg)'],
    df_spice['Egress Lat (deg)'],
    facecolors='none',
    edgecolors='red',
    s=10,
    linewidths=1,
    label=label_egr
)
plt.xlabel('Solar Zenith Angle [deg]', size=13)
plt.ylabel('Mars latitude [deg]', size=13)
plt.title('Latitude vs Solar Zenith Angle at TGO–Earth Occultation Tangent Points', size=15)
plt.grid(color="gray", linestyle="dotted", linewidth=0.5)
plt.legend(loc='upper right', bbox_to_anchor=(1, 1))
plt.xlim(
    min(df_spice['Ingress SZA (deg)'].min(), df_spice['Egress SZA (deg)'].min()),
    max(df_spice['Ingress SZA (deg)'].max(), df_spice['Egress SZA (deg)'].max())
)
plt.ylim(-90, 90)
plt.tight_layout()
plt.show()



n_ingress = len(spice_covered['Ingress SZA (deg)'])
n_egress  = len(spice_covered['Egress SZA (deg)'])
label_ing = f'Ingress Points \n (N={n_ingress})'
label_egr = f'Egress Points \n (N={n_egress})'

plt.figure(figsize=(10, 6))
plt.scatter(
    spice_covered['Ingress SZA (deg)'],
    spice_covered['Ingress Lat (deg)'],
    facecolors='none',     # no fill
    edgecolors='blue',     # circle outline color
    s=10,                  # adjust marker size
    linewidths=1,          # outline thickness
    label=label_ing
)
plt.scatter(
    spice_covered['Egress SZA (deg)'],
    spice_covered['Egress Lat (deg)'],
    facecolors='none',
    edgecolors='red',
    s=10,
    linewidths=1,
    label=label_egr
)
plt.xlabel('Solar Zenith Angle [deg]', size=13)
plt.ylabel('Mars latitude [deg]', size=13)
plt.title('Latitude vs Solar Zenith Angle at TGO–Earth Occultation Tangent Points \n Covered by Ground Stations', size=15)
plt.grid(color="gray", linestyle="dotted", linewidth=0.5)
plt.legend(loc='upper right', bbox_to_anchor=(1, 1))
plt.xlim(
    min(df_spice['Ingress SZA (deg)'].min(), df_spice['Egress SZA (deg)'].min()),
    max(df_spice['Ingress SZA (deg)'].max(), df_spice['Egress SZA (deg)'].max())
)
plt.ylim(-90, 90)
plt.tight_layout()
plt.show()
