import numpy as np
import pandas as pd

class CGE_IO_Data(object):
    def __init__(self, sam, Ind, Com):
        # Intermediate input QX
        self.intermediate_input = sam.loc[Com, Ind]
        # Labour input
        self.labour_input = sam.loc['Lab', Ind]
        self.total_labour_demand = sum(self.labour_input[ind] for ind in Ind)
        # Capital input
        self.capital_input = sam.loc['Cap', Ind]
        self.total_capital_demand = sum(self.capital_input[ind] for ind in Ind)
        # Value added
        self.value_added = self.total_labour_demand + self.total_capital_demand
        # Production tax:
        self.production_tax = sam.loc['Gov', Ind]
        # Total output X
        self.total_production = sam.loc[Ind, 'Total']
        # Commodity matrix XQ
        self.commodity_matrix = sam.loc[Ind, Com]

        # Exports
        self.export_commodity = sam.loc[Com, 'Foreign']
        self.import_commodity = sam.loc['Foreign', Com]

        # Household's demand
        self.household_commodity = sam.loc[Com, 'Hoh'].T
        # Household's savings:
        self.household_savings = sam.loc['Sav/Invest', 'Hoh']
        # Household's expenditure
        self.household_expenditure = sam.loc['Total', 'Hoh']

        # Government's demand
        self.government_commodity = sam.loc[Com, 'Gov'].T
        # Government's savings:
        self.government_savings = sam.loc['Sav/Invest', 'Gov']
        # Government's expenditure
        self.government_expenditure = sam.loc['Total', 'Gov']
        # Government's income
        self.government_income = sam.loc['Gov', Ind]

        # Total savings:
        self.total_savings = self.household_savings + self.government_savings
        # Goods investment
        self.invest_commodity = sam.loc[Com, 'Sav/Invest']
        # Foreign investment
        self.invest_foreign = sam.loc['Foreign', 'Sav/Invest']
        # Total investment
        self.total_investment = sam.loc['Sav/Invest', 'Total']

        # generate dict
        self.intermediate_input = self.intermediate_input.stack().to_dict()
        self.household_commodity = self.household_commodity.to_dict()
        self.government_commodity = self.government_commodity.to_dict()
        self.government_income = self.government_income.to_dict()
        self.labour_input = self.labour_input.to_dict()
        self.capital_input = self.capital_input.to_dict()
        self.total_production = self.total_production.to_dict()
        self.production_tax = self.production_tax.to_dict()
        self.commodity_matrix = self.commodity_matrix.stack().to_dict()
        self.invest_commodity = self.invest_commodity.to_dict()
        self.export_commodity = self.export_commodity.to_dict()
        self.import_commodity = self.import_commodity.to_dict()

        # Total commodity Q
        self.total_commodity = {}
        for c in Com:
            self.total_commodity[c] = sum(self.commodity_matrix[ind, c] for ind in Ind)

        self.domestic_commodity = {}
        for c in Com:
            self.domestic_commodity[c] = self.total_commodity[c] - self.export_commodity[c]

        self.armington_commodity = {}
        for c in Com:
            self.armington_commodity[c] = self.domestic_commodity[c] + self.import_commodity[c]

class CGE_Exo_Param(object):
    def __init__(self, CGE_IO_Data, Ind, Com):
        # Initial elasticity value
        self.elas_subs_utility = 0.8
        self.elas_subs_prod = {key: 0.8 for key in Ind}
        self.elas_subs_transform = {key: 0.8 for key in Com}
        self.elas_subs_armington = {key: 0.8 for key in Com}

        # Initial price value
        # Price for activity of domestic production PX
        self.price_production = {key: 1 for key in Ind}
        # Relative price of Armington commodity (Domestic + Import) sold in domestic market PC
        self.price_domestic_armington = {key: 1 for key in Com}
        # Price of domestically-produced commodity(From production to commodity) PQ
        self.price_domestic_produced = {key: 1 for key in Com}
        # Price of domestically-produced commodity sold in domestic market PQD
        self.price_domestic_produced_consumption = {key: 1 for key in Com}
        # Price of export at domestic currency
        self.price_export = {key: 1 for key in Com}
        # Price of import at domestic currency
        self.price_import = {key: 1 for key in Com}
        self.exchange_rate = 1
        # World price of import at foreign currency
        self.price_word_import = {key: 1 for key in Com}
        # World price of export at foreign currency
        self.price_word_export = {key: 1 for key in Com}
        self.price_utility = 1

        self.wage_labour = {key: 1 for key in Ind}
        self.rent_capital = {key: 1 for key in Ind}

        #Marginal cost of production
        self.marginal_cost = {key: 1 for key in Ind}

        # Calibrated parameters
        self.share_hoh_utility = {}
        for c in Com:
            self.share_hoh_utility[c] = (self.price_domestic_armington[c] * CGE_IO_Data.household_commodity[c]) ** (1 / self.elas_subs_utility) / sum(
                self.price_domestic_armington[c] * CGE_IO_Data.household_commodity[c] ** (1 / self.elas_subs_utility) for c in Com)

        # Household's saving rate
        self.saving_rate_hoh = CGE_IO_Data.household_savings / CGE_IO_Data.household_expenditure

        self.share_gov_utility = {}
        for c in Com:
            self.share_gov_utility[c] = CGE_IO_Data.government_commodity[c] / CGE_IO_Data.government_expenditure

        # Government's saving rate
        self.saving_rate_gov = CGE_IO_Data.government_savings / CGE_IO_Data.government_expenditure

        self.share_invest_utility = {}
        for c in Com:
            self.share_invest_utility[c] = CGE_IO_Data.invest_commodity[c] / CGE_IO_Data.total_investment

        self.production_tax_rate = {}
        for ind in Ind:
            self.production_tax_rate[ind] = CGE_IO_Data.production_tax[ind] / CGE_IO_Data.total_production[ind]

        self.share_inter_prod = {}
        for ind in Ind:
            for c in Com:
                self.share_inter_prod[c, ind] = (self.price_domestic_armington[c] * CGE_IO_Data.intermediate_input[c, ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_domestic_armington[c]
                                                                       * CGE_IO_Data.intermediate_input[c, ind] ** (1 / self.elas_subs_prod[ind]) for c in Com))
                                                                       + (self.wage_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                       + (self.rent_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))

        self.share_labour_prod = {}
        for ind in Ind:
            self.share_labour_prod[ind] = (self.wage_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_domestic_armington[c]
                                                                       * CGE_IO_Data.intermediate_input[c, ind] ** (1 / self.elas_subs_prod[ind]) for c in Com))
                                                                       + (self.wage_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                       + (self.rent_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))
        self.share_capital_prod = {}
        for ind in Ind:
            self.share_capital_prod[ind] = (self.rent_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_domestic_armington[c]
                                                                    * CGE_IO_Data.intermediate_input[c, ind] ** (1 / self.elas_subs_prod[ind]) for c in Com))
                                                                    + (self.wage_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                    + (self.rent_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))

        self.share_armington_prod = {}
        for c in Com:
            self.share_armington_prod[c] = (self.price_domestic_produced_consumption[c] * CGE_IO_Data.domestic_commodity[c]) ** (1 / self.elas_subs_armington[c]) / (self.price_domestic_produced_consumption[c]
                                        * CGE_IO_Data.domestic_commodity[c] ** (1 / self.elas_subs_armington[c]) + self.price_import[c] * CGE_IO_Data.import_commodity[c] ** (1 / self.elas_subs_armington[c]))

        self.share_cet_prod = {}
        for c in Com:
            self.share_cet_prod[c] = (self.price_domestic_produced_consumption[c] * CGE_IO_Data.domestic_commodity[c]) ** (1 / self.elas_subs_transform[c]) / (self.price_domestic_produced_consumption[c]
                                                                                                                                                                     * CGE_IO_Data.domestic_commodity[c] ** (1 / self.elas_subs_transform[c]) + self.price_export[c] * CGE_IO_Data.export_commodity[c] ** (

                                                                                                                                                                               1 / self.elas_subs_transform[c]))

        self.share_production_to_com = {}
        for ind in Ind:
            for c in Com:
                self.share_production_to_com[ind, c] = CGE_IO_Data.commodity_matrix[ind, c] / CGE_IO_Data.total_production[ind]

        self.scale_hoh_utility = 1 / self.price_utility * sum((self.share_hoh_utility[c] ** self.elas_subs_utility) * (
                                    self.price_domestic_armington[c] ** (1 - self.elas_subs_utility)) for c in Com) ** (1 / (1 - self.elas_subs_utility))

        self.scale_gov_utility = CGE_IO_Data.government_expenditure / np.prod([CGE_IO_Data.government_commodity[c] ** self.share_gov_utility[c] for c in Com])

        self.scale_invest = CGE_IO_Data.total_investment / np.prod([CGE_IO_Data.invest_commodity[c] ** self.share_invest_utility[c] for c in Com])

        self.scale_prod_ces = {}
        for ind in Ind:
            self.scale_prod_ces[ind] = CGE_IO_Data.total_production[ind] / (sum(self.share_inter_prod[c, ind] * CGE_IO_Data.intermediate_input[c, ind] ** (1 - 1 / self.elas_subs_prod[ind]) for c in Com)
                                                           + self.share_labour_prod[ind] * CGE_IO_Data.labour_input[ind] ** (1 - 1 / self.elas_subs_prod[ind])
                                                           + self.share_capital_prod[ind] * CGE_IO_Data.capital_input[ind] ** (1 - 1 / self.elas_subs_prod[ind])) ** (self.elas_subs_prod[ind] / (self.elas_subs_prod[ind] - 1))

        self.scale_prod_armington = {}
        for c in Com:
            self.scale_prod_armington[c] = CGE_IO_Data.armington_commodity[c] / (self.share_armington_prod[c] * CGE_IO_Data.domestic_commodity[c] ** (1 - 1 / self.elas_subs_armington[c])
                                           + (1 - self.share_armington_prod[c]) * CGE_IO_Data.import_commodity[c] ** (1 - 1 / self.elas_subs_armington[c])) ** (self.elas_subs_armington[c] / (self.elas_subs_armington[c] - 1))

        self.scale_prod_transform = {}
        for c in Com:
            self.scale_prod_transform[c] = CGE_IO_Data.total_commodity[c] / (self.share_cet_prod[c] * CGE_IO_Data.domestic_commodity[c] ** (1 - 1 / self.elas_subs_transform[c])
                                           + (1 - self.share_cet_prod[c]) * CGE_IO_Data.export_commodity[c] ** (1 - 1 / self.elas_subs_transform[c])) ** (self.elas_subs_transform[c] / (self.elas_subs_transform[c] - 1))

        self.marginal_prod_cost = {}
        for ind in Ind:
            self.marginal_prod_cost[ind] = 1/self.scale_prod_ces[ind] * (sum(
                                            self.share_inter_prod[c, ind]**self.elas_subs_prod[ind] * self.price_domestic_armington[c]**(1-self.elas_subs_prod[ind]) for c in Com)
                                            + self.share_labour_prod[ind]**self.elas_subs_prod[ind] * self.wage_labour[ind]**(1-self.elas_subs_prod[ind])
                                            + self.share_capital_prod[ind]**self.elas_subs_prod[ind] * self.rent_capital[ind]**(1-self.elas_subs_prod[ind]))**(1/(1-self.elas_subs_prod[ind]))
