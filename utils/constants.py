COAL_CO2_LBS_PER_KWH = 2.23  # https://www.eia.gov/tools/faqs/faq.php?id=74&t=11
GAS_CO2_LBS_PER_KWH = 0.91
OIL_CO2_LBS_PER_KWH = 2.13

CO2_LBS_PER_KWH = {'coal': COAL_CO2_LBS_PER_KWH, 'gas': GAS_CO2_LBS_PER_KWH, 'oil': OIL_CO2_LBS_PER_KWH}
CARBON_FREE_TYPES = ['hydro', 'nuclear', 'solar', 'wind', 'other_renewable']
CARBON_FREE_TYPES_LONGNAME = ['Hydroelectric', 'Nuclear', 'Solar', 'Wind', 'Other Renewable']
FOSSIL_TYPES = ['coal', 'gas', 'oil']
FOSSIL_TYPES_LONGNAME = ['Coal', 'Natural Gas', 'Oil']
ELECTRIC_TYPES = [None, 'fossil', 'hydro', 'nuclear', 'solar', 'wind', 'other_renewable']
ELECTRIC_TYPES_LONGNAME = ['Does not Generate Electricity', 'Fossil', 'Hydroelectric', 'Nuclear', 'Solar', 'Wind', 'Other Renewable']

USER_PATH_LIMIT = 5
USER_CLEANTECH_LIMIT = 50
CLEANTECH_REFERENCE_LIMIT = 10

KWH_PER_TON = 2000  # https://www.wri.org/insights/direct-air-capture-resource-considerations-and-costs-carbon-removal

TON_TO_MTON = 1e-6

LBS_TO_TONS = 1 / 2000.0
TWH_TO_GW = 1000 / 24 / 365
KWH_TO_GW = 1e-6 / 24 / 365

MAKE_ZERO = 1000

SUBSECTORS = ['Domestic Aviation', 'Non-residential', 'Manure management (N2O, CH4)', 'Enteric Fermentation (CH4)',
              'Rail', 'Road', 'Inland Shipping', 'Biomass burning (CH4, N2O)', 'Other (energy systems)',
              'Electricity & heat', 'International Aviation', 'Metals', 'Petroleum refining',
              'Coal mining fugitive emissions', 'Synthetic fertilizer application (N2O)', 'Chemicals',
              'Other (transport)', 'Managed soils and pasture (CO2, N2O)', 'Residential', 'Other (industry)', 'Waste',
              'Oil and gas fugitive emissions', 'Cement', 'Rice cultivation (CH4)', 'Non-CO2 (all buildings)',
              'International Shipping']
SECTORS = {'Buildings': ['Non-residential', 'Non-CO2 (all buildings)', 'Residential'],
           'Industry': ['Cement', 'Metals', 'Chemicals', 'Waste', 'Other (industry)'],
           'AFOLU': ['Rice cultivation (CH4)', 'Biomass burning (CH4, N2O)', 'Synthetic fertilizer application (N2O)',
                     'Manure management (N2O, CH4)', 'Enteric Fermentation (CH4)',
                     'Managed soils and pasture (CO2, N2O)'],
           'Transport': ['International Shipping', 'Other (transport)', 'Inland Shipping', 'International Aviation',
                         'Rail', 'Domestic Aviation', 'Road'],
           'Energy systems': ['Other (energy systems)', 'Coal mining fugitive emissions', 'Electricity & heat',
                              'Oil and gas fugitive emissions', 'Petroleum refining']}


def flatten(xss):
    flat_list = []
    for xs in xss:
        if type(xs) is str:
            flat_list.append(xs)
        else:
            for x in xs:
                flat_list.append(x)
    return list(set(flat_list))

TWH_TO_KWH = 1e9    # terawatt-hours to kilowatt-hours
EJ_TO_TWH = 277.778 # Exajoules to terawatt-hours.
PJ_TO_EJ = 1e-3     # Petajoules to exajoules.

COUNTRY_CODES = dict(AFG='Afghanistan', OWID_AFR='Africa', ALB='Albania', DZA='Algeria', ASM='American Samoa',
                     AGO='Angola', ATG='Antigua and Barbuda', ARG='Argentina', ARM='Armenia', ABW='Aruba',
                     AUS='Australia', AUT='Austria', AZE='Azerbaijan', BHS='Bahamas', BHR='Bahrain', BGD='Bangladesh',
                     BRB='Barbados', BLR='Belarus', BEL='Belgium', BLZ='Belize', BEN='Benin', BMU='Bermuda',
                     BTN='Bhutan', BOL='Bolivia', BIH='Bosnia and Herzegovina', BWA='Botswana', BRA='Brazil',
                     VGB='British Virgin Islands', BRN='Brunei', BGR='Bulgaria', BFA='Burkina Faso', BDI='Burundi',
                     KHM='Cambodia', CMR='Cameroon', CAN='Canada', CPV='Cape Verde', CYM='Cayman Islands',
                     CAF='Central African Republic', TCD='Chad', CHL='Chile', CHN='China', COL='Colombia',
                     COM='Comoros', COG='Congo', COK='Cook Islands', CRI='Costa Rica', CIV="Cote d'Ivoire",
                     HRV='Croatia', CUB='Cuba', CYP='Cyprus', CZE='Czechia', COD='Democratic Republic of Congo',
                     DNK='Denmark', DJI='Djibouti', DMA='Dominica', DOM='Dominican Republic', ECU='Ecuador',
                     EGY='Egypt', SLV='El Salvador', GNQ='Equatorial Guinea', ERI='Eritrea', EST='Estonia',
                     SWZ='Eswatini', ETH='Ethiopia', OWID_EUR='Europe', OWID_EU27='European Union (27)',
                     FRO='Faeroe Islands', FLK='Falkland Islands', FJI='Fiji', FIN='Finland', FRA='France',
                     GUF='French Guiana', PYF='French Polynesia', GAB='Gabon', GMB='Gambia', GEO='Georgia',
                     DEU='Germany', GHA='Ghana', GRC='Greece', GRL='Greenland', GRD='Grenada', GLP='Guadeloupe',
                     GUM='Guam', GTM='Guatemala', GIN='Guinea', GNB='Guinea-Bissau', GUY='Guyana', HTI='Haiti',
                     HND='Honduras', HKG='Hong Kong', HUN='Hungary', ISL='Iceland', IND='India', IDN='Indonesia',
                     IRN='Iran', IRQ='Iraq', IRL='Ireland', ISR='Israel', ITA='Italy', JAM='Jamaica', JPN='Japan',
                     JOR='Jordan', KAZ='Kazakhstan', KEN='Kenya', KIR='Kiribati', OWID_KOS='Kosovo', KWT='Kuwait',
                     KGZ='Kyrgyzstan', LAO='Laos', LVA='Latvia', LBN='Lebanon', LSO='Lesotho', LBR='Liberia',
                     LBY='Libya', LTU='Lithuania', LUX='Luxembourg', MAC='Macao', MDG='Madagascar', MWI='Malawi',
                     MYS='Malaysia', MDV='Maldives', MLI='Mali', MLT='Malta', MTQ='Martinique', MRT='Mauritania',
                     MUS='Mauritius', MEX='Mexico', FSM='Micronesia (country)', MDA='Moldova', MNG='Mongolia',
                     MNE='Montenegro', MSR='Montserrat', MAR='Morocco', MOZ='Mozambique', MMR='Myanmar', NAM='Namibia',
                     NRU='Nauru', NPL='Nepal', NLD='Netherlands', ANT='Netherlands Antilles', NCL='New Caledonia',
                     NZL='New Zealand', NIC='Nicaragua', NER='Niger', NGA='Nigeria', NIU='Niue', PRK='North Korea',
                     MKD='North Macedonia', MNP='Northern Mariana Islands', NOR='Norway', OMN='Oman', PAK='Pakistan',
                     PSE='Palestine', PAN='Panama', PNG='Papua New Guinea', PRY='Paraguay', PER='Peru',
                     PHL='Philippines', POL='Poland', PRT='Portugal', PRI='Puerto Rico', QAT='Qatar', REU='Reunion',
                     ROU='Romania', RUS='Russia', RWA='Rwanda', SHN='Saint Helena', KNA='Saint Kitts and Nevis',
                     LCA='Saint Lucia', SPM='Saint Pierre and Miquelon', VCT='Saint Vincent and the Grenadines',
                     WSM='Samoa', STP='Sao Tome and Principe', SAU='Saudi Arabia', SEN='Senegal', SRB='Serbia',
                     SYC='Seychelles', SLE='Sierra Leone', SGP='Singapore', SVK='Slovakia', SVN='Slovenia',
                     SLB='Solomon Islands', SOM='Somalia', ZAF='South Africa', KOR='South Korea', SSD='South Sudan',
                     ESP='Spain', LKA='Sri Lanka', SDN='Sudan', SUR='Suriname', SWE='Sweden', CHE='Switzerland',
                     SYR='Syria', TWN='Taiwan', TJK='Tajikistan', TZA='Tanzania', THA='Thailand', TLS='Timor',
                     TGO='Togo', TON='Tonga', TTO='Trinidad and Tobago', TUN='Tunisia', TUR='Turkey',
                     TKM='Turkmenistan', TCA='Turks and Caicos Islands', TUV='Tuvalu', UGA='Uganda', UKR='Ukraine',
                     ARE='United Arab Emirates', GBR='United Kingdom', USA='United States',
                     VIR='United States Virgin Islands', URY='Uruguay', UZB='Uzbekistan', VUT='Vanuatu',
                     VEN='Venezuela', VNM='Vietnam', ESH='Western Sahara', OWID_WRL='World', YEM='Yemen', ZMB='Zambia',
                     ZWE='Zimbabwe')
