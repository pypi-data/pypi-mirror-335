def gdp_use(share_production_to_com, price_domestic_armington, total_production, intermediate_input, Ind, Com):
    gdp1 = sum(share_production_to_com[ind, c] * price_domestic_armington[c] * total_production[ind] for ind in Ind for c in Com) - sum(
                intermediate_input[c, ind] * price_domestic_armington[c] for ind in Ind for c in Com)
    return gdp1

def gdp_value_added(labour_input, wage_labour, capital_input, rent_capital, total_government_income, Ind):
    gdp3 = sum(wage_labour[ind] * labour_input[ind] + rent_capital[ind] * capital_input[ind] for ind in Ind) + total_government_income
    return gdp3

def gdp_consumption(price_domestic_armington, household_demand, government_demand, invest_goods, price_export, produced_supply_export, price_import, consumed_import, Com):
    gdp2 = sum(price_domestic_armington[c]*(household_demand[c] + government_demand[c] + invest_goods[c]) for c in Com) + sum(price_export[c] * produced_supply_export[c] for c in Com) - sum(price_import[c] * consumed_import[c] for c in Com)
    return gdp2

def trade_balance(price_export, produced_supply_export, price_import, consumed_import, invest_foreign, Com):
    trade_balance = sum(price_export[c] * produced_supply_export[c] for c in Com) - sum(price_import[c] * consumed_import[c] for c in Com) - invest_foreign
    return trade_balance

def commodity_clearing(share_production_to_com, total_production, consumed_import, marginal_cost, production_tax_rate, price_import, intermediate_input, price_domestic_armington, produced_supply_export, price_export, household_demand, government_demand, invest_goods, Com, Ind):
    error_commodity = {}
    for c in Com:
        error_commodity[c] = sum(share_production_to_com[ind, c] * marginal_cost[ind] / (1 - production_tax_rate[ind]) * total_production[ind] for ind in Ind) + price_import[c] * consumed_import[c] - (
                                sum(price_domestic_armington[c] * intermediate_input[c, ind] for ind in Ind)
                             + price_export[c] * produced_supply_export[c] + price_domestic_armington[c] * (household_demand[c] + government_demand[c] + invest_goods[c]))
    return error_commodity

def labour_clearing(labour_input, total_labour_demand, Ind):
    error_labour = sum(labour_input[ind] for ind in Ind) - total_labour_demand
    return error_labour

def capital_clearing(capital_input, total_capital_demand, Ind):
    error_capital = sum(capital_input[ind] for ind in Ind) - total_capital_demand
    return error_capital