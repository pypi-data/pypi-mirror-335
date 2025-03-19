import numpy as np
import pandas as pd
from scipy import optimize as opt

import Calibration
import Consumer as Cons
import Producer as Prod
import MacroEconomy as Macro
import CGESystem as CGE

sam_table = pd.read_excel(r"D:\OneDriveSyn\OneDrive - The University of Hong Kong - Connect\SynJunex\Project\HKU\CGE\ICountry-2Input-2Consumer-3Sector-Invest\Data\SAM.xlsx")
sam_table = sam_table.set_index('Cat')
# Define sets in the model
Ind = ['Pri', 'Sec', 'Ter']
Com = ['Com1', 'Com2', 'Com3']
Fac = ['Lab', 'Cap']
Con = ['Hoh', 'Gov']

def execute():

    error_term = 100
    iteration = 0
    max_iteration = 5000
    max_tolerance = 1e-10
    adjust_rate = 0.1

    vars = Calibration.CGE_IO_Data(sam_table, Ind, Com, Fac, Con)
    params = Calibration.CGE_Exo_Param(vars, Ind, Com, Fac, Con)

    price_commodity_array = np.array([1.0, 1.0, 1.0])
    #price_commodity_array = np.array([1.0, 3.0, 3.0])
    wage_labour = params.price_labour
    rent_capital = params.price_capital

    labour_input = vars.labour_input
    capital_input = vars.capital_input
    total_production = vars.total_production

    while (error_term > max_tolerance) & (iteration < max_iteration):
        iteration += 1
        cge_args = [vars, params, Ind, Com, Fac, Con, price_commodity_array, total_production, labour_input, capital_input, wage_labour, rent_capital]

        print('Iteration =', iteration)
        print('Initialized product price =', price_commodity_array)

        results = opt.root(CGE.cge_system, price_commodity_array, args=cge_args, method='lm', tol=1e-5)
        price_commodity_array = results.x
        price_commodity_array[0] = 1.0
        price_commodity = dict(zip(Com, price_commodity_array))

        price_utility = Cons.price_utility(params.scale_hoh_utility, params.share_param_hoh_utility, params.elas_subs_utility, price_commodity, Com)
        value_added = Cons.total_value_added(wage_labour, labour_input, rent_capital, capital_input, Ind)
        price_production = Prod.price_production(params.share_production_to_com, price_commodity, Ind, Com)
        production_tax = Prod.production_tax(params.production_tax_rate, total_production, price_production, Ind)
        government_income = Cons.total_government_income(production_tax, Ind)
        household_goods = Cons.household_consumption(params.share_param_hoh_utility, price_commodity, params.elas_subs_utility, price_utility, params.scale_hoh_utility, params.saving_rate_hoh, value_added, Com)
        government_goods = Cons.government_consumption(params.share_param_gov_utility, price_commodity, government_income, Com)

        utility_hoh = Cons.consumer_utility(params.scale_hoh_utility, params.share_param_hoh_utility, household_goods, params.elas_subs_utility, Com)
        household_saving = Cons.household_saving(params.saving_rate_hoh, value_added)
        government_saving = Cons.government_saving(params.saving_rate_gov, government_income)
        total_savings = household_saving + government_saving
        total_invest = Cons.total_investment(total_savings)
        invest_goods = Cons.investment_goods(params.share_param_invest, total_invest, price_commodity,Com)

        wage_labour = Prod.price_labour(labour_input, vars.total_labour, Ind)
        rent_capital = Prod.price_capital(capital_input, vars.total_capital, Ind)

        marginal_cost = Prod.marginal_prod_cost(params.scale_prod_ces, params.share_param_inter_prod, params.elas_subs_prod, price_commodity, params.share_param_labour_prod, params.share_param_capital_prod, wage_labour, rent_capital, Ind, Com)
        intermediate_matrix = Prod.intermediate_demand(total_production, params.scale_prod_ces, params.share_param_inter_prod, marginal_cost, price_commodity, params.elas_subs_prod, Ind, Com)
        labour_input = Prod.labour_demand(total_production, params.scale_prod_ces, params.share_param_labour_prod, marginal_cost, wage_labour, params.elas_subs_prod, Ind, Com)
        capital_input = Prod.capital_demand(total_production, params.scale_prod_ces, params.share_param_capital_prod, marginal_cost, rent_capital, params.elas_subs_prod, Ind, Com)

        price_commodity_process = Prod.price_commodity(total_production, params.share_production_to_com, intermediate_matrix, household_goods, government_goods,invest_goods, Ind, Com)
        total_production_process = Prod.total_production(params.scale_prod_ces, params.share_param_inter_prod, intermediate_matrix, params.share_param_labour_prod, params.share_param_capital_prod, labour_input, capital_input, params.elas_subs_prod, Ind, Com)

        GDP1 = Macro.gdp_use(params.share_production_to_com, price_commodity, total_production, intermediate_matrix, Ind, Com)
        GDP2 = Macro.gdp_consumption(price_commodity, household_goods, government_goods, invest_goods, Com)
        GDP3 = Macro.gdp_value_added(wage_labour, labour_input, rent_capital, capital_input, Ind)

        final_price_commodity = price_commodity
        final_total_production = total_production_process

        processed_model = {}
        for ind in Ind:
            processed_model[ind] = ((total_production[ind] - total_production_process[ind]) ** 2) ** (1 / 2)

        distance_iter = sum(processed_model[ind] for ind in Ind)
        print('Distance at iteration', iteration, '=', distance_iter)

        price_commodity = (adjust_rate * price_commodity_process[cc] + (1-adjust_rate) * price_commodity[cc] for cc in Com)
        total_production = (adjust_rate * total_production_process[ind] + (1-adjust_rate) * total_production[ind] for ind in Ind)
        capital_input = (adjust_rate * capital_input[ind] + (1-adjust_rate) * capital_input[ind] for ind in Ind)

        print("Model solved, price = ", price_commodity_array)
        return final_price_commodity, utility_hoh, household_goods, final_total_production, intermediate_matrix, price_utility, marginal_cost, GDP1, GDP2, GDP3

if __name__ == '__main__':
    price_commodity, utility_hoh, household_goods, total_production, intermediate_matrix, price_utility, marginal_cost, GDP1, GDP2, GDP3 = execute()
    print(price_commodity)
    print(total_production)
    print([GDP1, GDP2, GDP3])