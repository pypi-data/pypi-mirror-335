import numpy as np
import Calibration as Calibration
import Consumer as Cons
import Producer as Prod
import MacroEconomy as Macro

def cge_system(price_commodity_array, args):
    (vars, params, Ind, Com, Fac, Con, price_commodity_array, total_production, labour_input, capital_input, wage_labour, rent_capital) = args
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
    invest_goods = Cons.investment_goods(params.share_param_invest, total_invest, price_commodity, Com)

    wage_labour = Prod.price_labour(labour_input, vars.total_labour, Ind)
    rent_capital = Prod.price_capital(capital_input, vars.total_capital, Ind)

    marginal_cost = Prod.marginal_prod_cost(params.scale_prod_ces, params.share_param_inter_prod, params.elas_subs_prod, price_commodity, params.share_param_labour_prod, params.share_param_capital_prod, wage_labour, rent_capital, Ind, Com)
    intermediate_matrix = Prod.intermediate_demand(total_production, params.scale_prod_ces, params.share_param_inter_prod, marginal_cost, price_commodity, params.elas_subs_prod, Ind, Com)
    labour_input = Prod.labour_demand(total_production, params.scale_prod_ces, params.share_param_labour_prod, marginal_cost, wage_labour, params.elas_subs_prod, Ind, Com)
    capital_input = Prod.capital_demand(total_production, params.scale_prod_ces, params.share_param_capital_prod, marginal_cost, rent_capital, params.elas_subs_prod, Ind, Com)

    error_labour = Macro.labour_clearing(labour_input, vars.total_labour, Ind)
    error_capital = Macro.capital_clearing(capital_input, vars.total_capital, Ind)
    error_com = Macro.commodity_clearing(params.share_production_to_com, total_production, price_commodity, intermediate_matrix, household_goods, government_goods, invest_goods, Com, Ind)
    error_commodity = [error_com[cc] for cc in Com]
    error_list = np.append(error_commodity, [error_labour, error_capital])
    return error_list