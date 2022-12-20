import pandas as pd
from sector_conversions import SECTOR_CONV, GWP_AR5
from utils.constants import SECTORS, CARBON_FREE_TYPES

create_WRL_emissions = False

if create_WRL_emissions:
    f_gases_df = pd.read_excel('../EDGAR/v70_FT2021_F-gases_1990-2021.xlsx', sheet_name='IPCC2006', skiprows=9)
    co2_df = pd.read_excel('../EDGAR/CO2_1970_2021.xlsx', sheet_name='CO2_IPCC2006', skiprows=9)
    ch4_df = pd.read_excel('../EDGAR/CH4_1970_2021.xlsx', sheet_name='CH4_IPCC2006', skiprows=9)
    n2o_df = pd.read_excel('../EDGAR/N2O_1970_2021.xlsx', sheet_name='N2O_IPCC2006', skiprows=9)

    WRL_df = pd.DataFrame()
    WRL_df['year'] = None
    WRL_df = WRL_df.set_index('year')
    for sector in SECTOR_CONV:
        WRL_df[SECTOR_CONV[sector]] = None

    for year in range(2000, 2021 + 1):
        print(year)
        add = {}
        for column in WRL_df.columns:
            add[column] = 0
        add['year'] = year

        for data_df in [co2_df, ch4_df, n2o_df, f_gases_df]:
            for idx, row in data_df.iterrows():
                if row[f'Y_{year}'] > 0:
                    add[SECTOR_CONV[row['ipcc_code_2006_for_standard_report']]] += GWP_AR5[row['Substance']] * row[f'Y_{year}']

        df_add = pd.DataFrame.from_dict([add])
        df_add = df_add.set_index('year')
        WRL_df = pd.concat([WRL_df, df_add])
    cols_with_all_zeros = [column for column in WRL_df.columns if WRL_df[column].sum() == 0]
    WRL_df = WRL_df.drop(columns=cols_with_all_zeros)
    WRL_df.to_csv('../WRL_emissions.csv')

    print('WRL_emissions created')

WRL_emission_df = pd.read_csv('../WRL_emissions.csv', index_col='year')
owid_energy_df = pd.read_csv('../owid/owid-energy-data.csv')

first_year = min(WRL_emission_df.index)
last_year = max(WRL_emission_df.index)

owid_energy_df = owid_energy_df[owid_energy_df.country == 'World']
owid_energy_df = owid_energy_df[owid_energy_df.year >= first_year]
owid_energy_df = owid_energy_df[owid_energy_df.year <= last_year]

owid_energy_df = owid_energy_df.set_index('year')
electricity_columns = [column for column in owid_energy_df.columns if 'electricity' in column]

WRL_data = WRL_emission_df.copy()

for sector in SECTORS:
    WRL_data[sector] = sum([WRL_data[subsector] for subsector in SECTORS[sector] if subsector in WRL_data.columns])
WRL_data['all'] = sum([WRL_data[sector] for sector in SECTORS])
for column in WRL_data.columns:
    WRL_data[column] = WRL_data[column] * 1000
    WRL_data = WRL_data.rename({column: f'{column}_emissions'}, axis=1)

for column in electricity_columns:
    WRL_data[column] = owid_energy_df[column]
WRL_data['carbon_free_electricity'] = sum([WRL_data[f'{elec_type}_electricity'] for elec_type in CARBON_FREE_TYPES])
WRL_data.to_csv('../country/WRL_data.csv')

print('WRL_data created')
