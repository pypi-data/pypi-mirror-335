import numpy as np
import pandas as pd

class CGE_IO_Data(object):
    def __init__(self, sam, Ind, Com, Fac, Con):
        # Intermediate input QX
        self.intermediate_matrix = sam.loc[Com, Ind]
        # Total output X
        self.total_production = sam.loc[Ind, 'Total']
        # Commodity matrix XQ
        self.commodity_matrix = sam.loc[Ind, Com]
        # Production tax:
        self.production_tax = sam.loc['Gov', Ind]
        # Labour input
        self.labour_input = sam.loc['Lab', Ind]
        self.total_labour = sum(self.labour_input[ind] for ind in Ind)
        # Capital input
        self.capital_input = sam.loc['Cap', Ind]
        self.total_capital = sum(self.capital_input[ind] for ind in Ind)
        self.value_added = self.total_labour + self.total_capital
        # Household's demand
        self.household_good = sam.loc[Com, 'Hoh'].T
        # Household's savings:
        self.household_savings = sam.loc['Sav/Invest', 'Hoh']
        # Household's expenditure
        self.household_expenditure = sam.loc['Total', 'Hoh']
        # Government's demand
        self.government_good = sam.loc[Com, 'Gov'].T
        # Government's income
        self.government_income = sam.loc['Gov', Ind]
        # Government's savings:
        self.government_savings = sam.loc['Sav/Invest', 'Gov']
        # Government's expenditure
        self.government_expenditure = sam.loc['Total', 'Gov']
        # Total savings:
        self.total_savings = self.household_savings + self.government_savings
        # Total investment
        self.total_investment = self.total_savings
        # Total demand
        #self.total_demand = sum(self.final_demand[cc] for cc in Com) + self.total_savings
        # Goods investment
        self.invest_goods = sam.loc[Com, 'Sav/Invest']

        # generate dict
        self.intermediate_matrix = self.intermediate_matrix.stack().to_dict()
        self.household_good = self.household_good.to_dict()
        self.government_good = self.government_good.to_dict()
        self.government_income = self.government_income.to_dict()
        self.labour_input = self.labour_input.to_dict()
        self.capital_input = self.capital_input.to_dict()
        self.total_production = self.total_production.to_dict()
        self.production_tax = self.production_tax.to_dict()
        self.commodity_matrix = self.commodity_matrix.stack().to_dict()
        self.invest_goods = self.invest_goods.to_dict()

class CGE_Exo_Param(object):
    def __init__(self, CGE_IO_Data, Ind, Com, Fac, Con):
        # Initial elasticity value
        self.elas_subs_utility = 0.5
        self.elas_subs_invest = 0.5
        self.elas_subs_prod = {key: 0.5 for key in Ind}

        # Initial price value
        self.price_utility = 1
        self.price_commodity = {key: 1 for key in Com}
        self.price_labour = {key: 1 for key in Ind}
        self.price_capital = {key: 1 for key in Ind}
        self.marginal_cost = {key: 1 for key in Ind}

        # Calibrated parameters
        self.share_param_hoh_utility = {}
        for cc in Com:
            self.share_param_hoh_utility[cc] = (self.price_commodity[cc] * CGE_IO_Data.household_good[cc]) ** (1 / self.elas_subs_utility) / sum(
                self.price_commodity[cc] * CGE_IO_Data.household_good[cc] ** (1 / self.elas_subs_utility) for cc in Com)

        self.share_param_gov_utility = {}
        for cc in Com:
            self.share_param_gov_utility[cc] = CGE_IO_Data.government_good[cc] / CGE_IO_Data.government_expenditure

        self.saving_rate_hoh = CGE_IO_Data.household_savings / CGE_IO_Data.household_expenditure
        self.saving_rate_gov = CGE_IO_Data.government_savings / CGE_IO_Data.government_expenditure

        self.share_param_invest = {}
        for cc in Com:
            self.share_param_invest[cc] = CGE_IO_Data.invest_goods[cc] / CGE_IO_Data.total_investment

        self.production_tax_rate = {}
        for ind in Ind:
            self.production_tax_rate[ind] = CGE_IO_Data.production_tax[ind] / CGE_IO_Data.total_production[ind]

        self.share_param_inter_prod = {}
        for ind in Ind:
            for cc in Com:
                self.share_param_inter_prod[cc, ind] = (self.price_commodity[cc] * CGE_IO_Data.intermediate_matrix[cc, ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_commodity[cc]
                                                                       * CGE_IO_Data.intermediate_matrix[cc, ind] ** (1 / self.elas_subs_prod[ind]) for cc in Com))
                                                                       + (self.price_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                       + (self.price_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))

        self.share_param_labour_prod = {}
        for ind in Ind:
            self.share_param_labour_prod[ind] = (self.price_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_commodity[cc]
                                                                       * CGE_IO_Data.intermediate_matrix[cc, ind] ** (1 / self.elas_subs_prod[ind]) for cc in Com))
                                                                       + (self.price_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                       + (self.price_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))
        self.share_param_capital_prod = {}
        for ind in Ind:
            self.share_param_capital_prod[ind] = (self.price_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]) / (sum((self.price_commodity[cc]
                                                                    * CGE_IO_Data.intermediate_matrix[cc, ind] ** (1 / self.elas_subs_prod[ind]) for cc in Com))
                                                                    + (self.price_labour[ind] * CGE_IO_Data.labour_input[ind]) ** (1 / self.elas_subs_prod[ind])
                                                                    + (self.price_capital[ind] * CGE_IO_Data.capital_input[ind]) ** (1 / self.elas_subs_prod[ind]))

        self.share_production_to_com = {}
        for ind in Ind:
            for cc in Com:
                self.share_production_to_com[ind, cc] = CGE_IO_Data.commodity_matrix[ind, cc] / CGE_IO_Data.total_production[ind]

        self.scale_hoh_utility = 1 / self.price_utility * sum((self.share_param_hoh_utility[cc] ** self.elas_subs_utility) * (
                self.price_commodity[cc] ** (1 - self.elas_subs_utility)) for cc in Com) ** (1 / (1 - self.elas_subs_utility))

        self.scale_gov_utility = CGE_IO_Data.government_expenditure / np.prod([CGE_IO_Data.government_good[cc] ** self.share_param_gov_utility[cc] for cc in Com])

        self.scale_invest = CGE_IO_Data.total_investment / np.prod([CGE_IO_Data.invest_goods[cc] ** self.share_param_invest[cc] for cc in Com])

        self.scale_prod_ces = {}
        for ind in Ind:
            self.scale_prod_ces[ind] = CGE_IO_Data.total_production[ind] / (sum(self.share_param_inter_prod[cc, ind] * CGE_IO_Data.intermediate_matrix[cc, ind] ** (1 - 1 / self.elas_subs_prod[ind]) for cc in Com)
                                                           + self.share_param_labour_prod[ind] * CGE_IO_Data.labour_input[ind] ** (1 - 1 / self.elas_subs_prod[ind])
                                                           + self.share_param_capital_prod[ind] * CGE_IO_Data.capital_input[ind] ** (1 - 1 / self.elas_subs_prod[ind])) ** (self.elas_subs_prod[ind] / (self.elas_subs_prod[ind] - 1))
