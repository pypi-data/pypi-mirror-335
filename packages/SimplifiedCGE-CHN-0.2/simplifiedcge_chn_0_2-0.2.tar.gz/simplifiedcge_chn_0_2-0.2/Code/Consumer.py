def consumer_utility(scale_utility, share_param_hoh_utility, household_demand, elas_subs_utility, Com):
    utility_cons = scale_utility * sum(share_param_hoh_utility[cc] * (household_demand[cc]**(1-1/elas_subs_utility))
                                              for cc in Com)**(elas_subs_utility/(elas_subs_utility-1))
    return utility_cons

def price_utility(scale_utility, share_param_hoh_utility, elas_subs_utility, price_commodity, Com):
    price_util = (1/scale_utility) * sum(share_param_hoh_utility[cc]**elas_subs_utility * price_commodity[cc]**(1-elas_subs_utility) for cc in Com)**(1/(1-elas_subs_utility))
    return price_util

def household_consumption(share_param_hoh_utility, price_commodity, elas_subs_utility, price_utility, scale_utility, saving_rate_hoh, household_income, Com):
    household_demand = {}
    for cc in Com:
        household_demand[cc] = (share_param_hoh_utility[cc] * scale_utility * price_utility / price_commodity[cc]) ** elas_subs_utility * (1-saving_rate_hoh) * household_income / (price_commodity[cc] * scale_utility)
    return household_demand

def government_consumption(share_param_gov_utility, price_commodity, government_income, Com):
    government_demand = {}
    for cc in Com:
        government_demand[cc] = share_param_gov_utility[cc] * government_income / price_commodity[cc]
    return government_demand

def agg_final_demand(household_demand, government_demand, Com):
    total_final_demand = sum(household_demand[cc] + government_demand[cc] for cc in Com)
    return total_final_demand

def total_value_added(price_labour, labour_input, price_capital, capital_input, Ind):
    value_added = sum(price_labour[ind]*labour_input[ind] + price_capital[ind]*capital_input[ind] for ind in Ind)
    return value_added

def total_government_income(production_tax, Ind):
    government_income = sum(production_tax[ind] for ind in Ind)
    return government_income

def household_saving(saving_rate_hoh, household_income):
    household_savings = saving_rate_hoh * household_income
    return household_savings

def government_saving(saving_rate_gov, government_income):
    government_savings = saving_rate_gov * government_income
    return government_savings

def total_saving(household_savings, government_savings):
    total_savings = household_savings + government_savings
    return total_savings

def total_investment(total_savings):
    total_invest = total_savings
    return total_invest

def investment_goods(share_param_invest, total_investment, price_commodity, Com):
    invest_goods = {}
    for cc in Com:
        invest_goods[cc] = share_param_invest[cc] * total_investment / price_commodity[cc]
    return invest_goods