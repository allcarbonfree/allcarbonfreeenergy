import numpy as np
import pandas as pd
from datetime import datetime
import pytz
from paths.models import Country
import json
from utils.constants import *


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def create_path(path, author=None, save_path=False, include_full=False, cleantech_output=None):
    class CleanTechObj:
        list = []

        def __init__(self, *initial_data, **kwargs):
            self.replace = None
            self.limiter_unit = None
            self.list.append(self)
            for dictionary in initial_data:
                for key in dictionary:
                    setattr(self, key, dictionary[key])
            for key in kwargs:
                setattr(self, key, kwargs[key])

            if self.all_subsectors:
                self.all_subsectors = json.loads(self.all_subsectors)
                self.all_subsectors = flatten(self.all_subsectors)

            self.units_per_year = [self.before_start_year_units, self.start_year_units]
            if self.units_per_year:
                self.max_prod = self.units_per_year[-2] - self.units_per_year[-1]

            if self.replace_fossil:  # Clean Energy Source
                self.limiter_unit = self.electric_energy_per_unit
            else:  # Reduce/Replace Carbon Emissions
                self.limiter_unit = self.CO2_reduced_per_unit

        def add_to_annual_output(self, output):
            self.units_per_year = np.append(self.units_per_year, output)

        def calc_max_replace_units(self, annual):
            if self.replace_fossil:
                self.replace = annual['fossil']
            else:
                self.replace = sum([annual[subsector] for subsector in self.all_subsectors])

    class Path:
        def __init__(self, country_code, increase_energy_use=True):
            self.max_carbon_free_electricity = None
            self.total_sim_emissions = None
            self.inc_emission_params = None
            self.output_delta = None
            self.increase_energy_use = increase_energy_use
            self.country_df = pd.read_json(Country.objects.filter(country_code=country_code).first().country_df,
                                           orient='split')
            self.starting_year = 2000
            self.ending_year = 2100
            self.country_df = self.country_df[self.country_df.year >= self.starting_year]
            self.country_df_init = self.country_df.copy()
            self.subsectors = [ss_idx for ss_idx in SUBSECTORS if f'{ss_idx}_emissions' in self.country_df.columns]
            self.sectors = [sector_idx for sector_idx in SECTORS if
                            f'{sector_idx}_emissions' in self.country_df.columns]
            self.annual = {}
            self.annual_df = self.country_df[self.country_df.year == max(self.country_df.year.values)].copy()
            self.set_annual()
            self.latest_year = max(self.country_df.year.values)
            self.fossil_list = []
            self.non_fossil_list = []
            self.cleantech_list = []
            self.set_increase_energy_use_params()

        def set_increase_energy_use_params(self):
            def get_best_fit_log(subsector_idx, years_back=10):
                years = self.country_df['year'].tail(n=years_back).values
                values = self.country_df[subsector_idx + '_emissions'].tail(n=years_back).values
                params = np.polyfit(np.log(years - min(years) + 1), values - min(values), 1)
                return np.append(params, years_back)

            self.inc_emission_params = {subsector_idx: get_best_fit_log(subsector_idx) for subsector_idx in
                                        self.subsectors}

        def set_fossil_list(self):
            self.fossil_list = [tech_idx for tech_idx in self.cleantech_list if
                                (tech_idx.electric_generation_type == 'fossil') or
                                (tech_idx.electric_generation_type is None)]
            self.non_fossil_list = [tech_idx for tech_idx in self.cleantech_list if
                                    (tech_idx.electric_generation_type != 'fossil') and
                                    (tech_idx.electric_generation_type is not None)]

        def set_cleantech_subsectors(self):
            for tech_idx in self.cleantech_list:
                if tech_idx.all_subsectors:
                    tech_idx.all_subsectors = [subsector_idx for subsector_idx in tech_idx.all_subsectors if
                                               subsector_idx in self.subsectors]

        def set_cleantech_list(self, cleantech_list):
            self.cleantech_list = cleantech_list
            self.set_cleantech_subsectors()
            self.set_fossil_list()

        def set_annual(self):
            for column in self.annual_df.columns:
                if column[-9:] == 'emissions':
                    column_pre = column[:-10]
                    if (column_pre in SECTORS) or (column_pre in SUBSECTORS) or (column_pre in ['electricity', 'all']):
                        self.annual.update({column_pre: self.annual_df[column].values[0]})
                elif column[-11:] == 'electricity':
                    self.annual.update({column[:-12]: self.annual_df[column].values[0]})
                else:
                    self.annual.update({column: self.annual_df[column].values[0]})

        def set_annual_totals(self):
            for sector_idx in SECTORS:
                self.annual[sector_idx] = sum([
                    self.annual[ss_idx] for ss_idx in SECTORS[sector_idx] if ss_idx in self.subsectors])

            self.annual['all'] = sum([self.annual[sector_idx] for sector_idx in SECTORS])
            self.annual['electricity'] = TWH_TO_KWH * LBS_TO_TONS * sum(
                [self.annual[elec_type] * CO2_LBS_PER_KWH[elec_type]
                 for elec_type in FOSSIL_TYPES])
            self.annual['carbon_free'] = sum([self.annual[elec_type] for elec_type in CARBON_FREE_TYPES])

            self.annual['fossil'] = sum([self.annual[elec_type] for elec_type in FOSSIL_TYPES])

        def sim_next_year(self, tech):
            def calc_next_logistic_value():
                delta_exp = tech.growth_rate * (tech.units_per_year[-1] - tech.units_per_year[-2])
                if delta_exp > tech.max_prod:
                    tech.max_prod = delta_exp
                all_units = tech.limit_perc * (tech.replace / tech.limiter_unit + tech.units_per_year[-1])
                delta_log = max(tech.saturation_rate * (all_units - tech.units_per_year[-1]), 0)
                return min(delta_log, tech.max_prod)

            tech.calc_max_replace_units(self.annual)

            if tech.replace > MAKE_ZERO and tech.start_year < self.annual['year']:
                self.output_delta = calc_next_logistic_value()

                if tech.all_subsectors:
                    emissions_sum = sum([self.annual[subsector_idx] for subsector_idx in tech.all_subsectors])
                    if tech.replace < self.output_delta * tech.CO2_reduced_per_unit:
                        self.output_delta = tech.replace / tech.CO2_reduced_per_unit
                    if emissions_sum > 0:
                        for subsector_idx in tech.all_subsectors:
                            subsector_perc = self.annual[subsector_idx] / emissions_sum
                            self.annual[subsector_idx] -= subsector_perc * self.output_delta * tech.CO2_reduced_per_unit
                            if self.annual[subsector_idx] < MAKE_ZERO:
                                self.annual[subsector_idx] = 0

                tech.add_to_annual_output(tech.units_per_year[-1] + self.output_delta)

                if (tech.electric_generation_type == 'fossil') or (tech.electric_generation_type is None):
                    if (tech.replace - self.output_delta * tech.limiter_unit) < MAKE_ZERO:
                        self.output_delta = 0

                    for elec_type in FOSSIL_TYPES:
                        if self.annual['fossil'] > 0:
                            elec_type_perc = self.annual[elec_type] / self.annual['fossil']
                        else:
                            if elec_type == 'gas':
                                elec_type_perc = 1
                            else:
                                elec_type_perc = 0
                        self.annual[elec_type] += elec_type_perc * self.output_delta * tech.electric_energy_per_unit
                        self.annual['Electricity & heat'] += CO2_LBS_PER_KWH[elec_type] * \
                                                             tech.electric_energy_per_unit * \
                                                             elec_type_perc * self.output_delta * TWH_TO_KWH * \
                                                             LBS_TO_TONS
                else:
                    self.annual[tech.electric_generation_type] += self.output_delta * tech.electric_energy_per_unit

                    if tech.replace_fossil and self.annual['fossil'] > 0:
                        for elec_type in FOSSIL_TYPES:
                            elec_type_perc = self.annual[elec_type] / self.annual['fossil']
                            self.annual[elec_type] -= elec_type_perc * self.output_delta
                            if self.annual[elec_type] < MAKE_ZERO:
                                self.annual[elec_type] = 0
                            if self.annual['Electricity & heat'] > 0:
                                self.annual['Electricity & heat'] -= CO2_LBS_PER_KWH[elec_type] * elec_type_perc * \
                                                                     self.output_delta * TWH_TO_KWH * LBS_TO_TONS
                            if self.annual['Electricity & heat'] < MAKE_ZERO:
                                self.annual['Electricity & heat'] = 0

                self.set_annual_totals()

        def add_annual_to_df(self):
            for key in self.annual:
                if (key in SECTORS) or (key in SUBSECTORS) or (key in ['electricity', 'all']):
                    self.annual_df[f'{key}_emissions'] = self.annual[key]
                elif (key in CARBON_FREE_TYPES) or (key in FOSSIL_TYPES) or (key in ['carbon_free', 'fossil']):
                    self.annual_df[f'{key}_electricity'] = self.annual[key]
            self.annual_df['year'] = self.annual['year']
            self.country_df = pd.concat([self.country_df, self.annual_df])

        def add_increase_energy_use(self):
            def get_emissions_increase(ss_idx):
                params = self.inc_emission_params[ss_idx]
                last_year = params[1] + params[0] * np.log(self.annual['year'] - self.latest_year + params[2])
                this_year = params[1] + params[0] * np.log(self.annual['year'] - self.latest_year + 1 + params[2])
                return this_year - last_year

            for subsector_idx in self.subsectors:
                self.annual[subsector_idx] += get_emissions_increase(subsector_idx)

            self.set_annual_totals()

        def set_starting_year(self, set_year):
            self.starting_year = set_year
            self.country_df = self.country_df[self.country_df.year >= self.starting_year]

        def set_ending_year(self, set_year):
            self.ending_year = set_year

        def simulate(self):
            self.country_df = self.country_df_init.copy()
            self.annual_df = self.country_df[self.country_df.year == max(self.country_df.year.values)].copy()
            self.set_annual()
            for year_idx in range(self.latest_year + 1, self.ending_year + 1):
                self.annual['year'] = year_idx

                self.add_increase_energy_use()

                for tech_idx in self.fossil_list:
                    self.sim_next_year(tech_idx)
                for tech_idx in self.non_fossil_list:
                    self.sim_next_year(tech_idx)

                self.add_annual_to_df()
                if cleantech_output:
                    for cleantech in self.cleantech_list:
                        if cleantech.id == cleantech_output:
                            self.cleantech_annual_output = json.dumps(np.round(cleantech.units_per_year),
                                                                      cls=NumpyArrayEncoder)
                if self.annual['all'] < MAKE_ZERO:
                    break

        def calc_totals(self):
            emissions_2010 = 1930 * 1e9  # https://www.ipcc.ch/sr15/chapter/chapter-2/2-2/2-2-2/2-2-2-1/figure-2-3/
            emissions_after_2010 = sum(
                self.country_df[self.country_df.year > 2010]['all_emissions'].values)
            self.total_sim_emissions = (emissions_2010 + emissions_after_2010) * 1e-9
            self.max_carbon_free_electricity = max(self.country_df.carbon_free_electricity) * TWH_TO_GW

    cleantechs = path.cleantech_list.all()
    cleantech_ids = str(sorted([str(cleantech.id) for cleantech in cleantechs]))

    path.cleantech_ids = cleantech_ids

    all_carbon_free = Path('WRL')
    all_carbon_free.set_starting_year(path.starting_year)

    for cleantech in cleantechs:
        CleanTechObj(**cleantech.__dict__)

    all_carbon_free.set_cleantech_list(CleanTechObj.list)
    all_carbon_free.simulate()
    all_carbon_free.calc_totals()

    country_df_lite = all_carbon_free.country_df[['year', 'carbon_free_electricity', 'Buildings_emissions',
                                                  'Industry_emissions', 'AFOLU_emissions', 'Transport_emissions',
                                                  'Energy systems_emissions']]
    country_df_lite.set_index('year', inplace=True)
    path.country_df = country_df_lite.to_json(orient='split', double_precision=0)

    if include_full:
        path.country_df_full = all_carbon_free.country_df.to_json(orient='split')
    path.total_sim_emissions = int(all_carbon_free.total_sim_emissions)
    path.max_carbon_free_electricity = int(all_carbon_free.max_carbon_free_electricity)
    path.est_degree_rise = round(all_carbon_free.total_sim_emissions * .00055 - 0.05, 1)
    path.carbon_zero_year = all_carbon_free.annual['year']
    path.time = pytz.utc.localize(datetime.now())
    if cleantech_output:
        path.cleantech_annual_output = all_carbon_free.cleantech_annual_output
    path.author = author
    if author == 'allcarbonfree':
        path.include_with_profile = True
    if save_path:
        path.save()
