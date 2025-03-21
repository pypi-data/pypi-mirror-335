def household_consumption(share_hoh_utility, price_domestic_armington, elas_subs_utility, price_utility, scale_utility, saving_rate_hoh, household_income, Com):
    household_demand = {}
    for c in Com:
        household_demand[c] = (share_hoh_utility[c] * scale_utility * price_utility / price_domestic_armington[c]) ** elas_subs_utility * (1-saving_rate_hoh) * household_income / (price_utility * scale_utility)
    return household_demand

def government_consumption(share_gov_utility, price_domestic_armington, total_government_income, Com):
    government_demand = {}
    for c in Com:
        government_demand[c] = share_gov_utility[c] * total_government_income / price_domestic_armington[c]
    return government_demand

def consumer_utility(scale_utility, share_hoh_utility, household_demand, elas_subs_utility, Com):
    utility_hoh = scale_utility * sum(share_hoh_utility[c] * (household_demand[c]**(1-1/elas_subs_utility))
                                              for c in Com)**(elas_subs_utility/(elas_subs_utility-1))
    return utility_hoh

def total_value_added(wage_labour, labour_input, rent_capital, capital_input, Ind):
    value_added = sum(wage_labour[ind]*labour_input[ind] + rent_capital[ind]*capital_input[ind] for ind in Ind)
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

def investment_goods(share_invest, total_investment, price_domestic_armington, Com):
    invest_goods = {}
    for c in Com:
        invest_goods[c] = share_invest[c] * total_investment / price_domestic_armington[c]
    return invest_goods

def investment_foreign(invest_goods, total_investment, Com):
    invest_foreign = total_investment - sum(invest_goods[c] for c in Com)
    return invest_foreign

def price_utility(scale_hoh_utility, share_hoh_utility, elas_subs_utility, price_domestic_armington, Com):
    price_util = (1/scale_hoh_utility) * sum(share_hoh_utility[c]**elas_subs_utility * price_domestic_armington[c]**(1-elas_subs_utility) for c in Com)**(1/(1-elas_subs_utility))
    return price_util

def agg_final_demand(household_demand, government_demand, Com):
    total_final_demand = sum(household_demand[c] + government_demand[c] for c in Com)
    return total_final_demand



