def gdp_use(share_production_to_com, price_commodity, total_production, intermediate_matrix, Ind, Com):
    gdp1 = sum(share_production_to_com[ind, cc] * price_commodity[cc] * total_production[ind] for ind in Ind for cc in Com) - sum(
                intermediate_matrix[cc, ind] * price_commodity[cc] for ind in Ind for cc in Com)
    return gdp1

def gdp_value_added(labour_input, wage_labour, capital_input, rent_capital, Ind):
    value_added = sum(wage_labour[ind] * labour_input[ind] + rent_capital[ind] * capital_input[ind] for ind in Ind)
    return value_added

def gdp_consumption(price_commodity, household_demand, government_demand, invest_goods, Com):
    gdp2 = sum(price_commodity[cc]*(household_demand[cc] + government_demand[cc] + invest_goods[cc]) for cc in Com)
    return gdp2

def commodity_clearing(share_production_to_com, total_production, price_commodity, intermediate_matrix, household_demand, government_demand, invest_goods, Com, Ind):
    error_commodity = {}
    for cc in Com:
        error_commodity[cc] = sum(share_production_to_com[ind, cc] * price_commodity[cc] * total_production[ind] for ind in Ind) - (
                              sum(intermediate_matrix[cc, ind] * price_commodity[cc] for ind in Ind) + price_commodity[cc] * (household_demand[cc] + government_demand[cc] + invest_goods[cc]))
    return error_commodity

def labour_clearing(labour_input, total_labour, Ind):
    error_labour = sum(labour_input[ind] for ind in Ind) - total_labour
    return error_labour

def capital_clearing(capital_input, total_capital, Ind):
    error_capital = sum(capital_input[ind] for ind in Ind) - total_capital
    return error_capital