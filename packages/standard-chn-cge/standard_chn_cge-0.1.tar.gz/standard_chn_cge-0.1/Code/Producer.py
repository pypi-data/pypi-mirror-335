def price_commodity_to_marginal_cost(share_production_to_com, price_domestic_armington, production_tax_rate, Ind, Com):
    marginal_prod_cost = {}
    for ind in Ind:
        marginal_prod_cost[ind] = sum(share_production_to_com[ind, c] * price_domestic_armington[c] for c in Com) * (1 - production_tax_rate[ind])
    return marginal_prod_cost

def intermediate_demand(total_production, scale_prod_ces, share_param_inter_prod, marginal_cost, price_domestic_armington, elas_subs_prod, Ind, Com):
    intermediate_matrix = {}
    for ind in Ind:
        for c in Com:
            intermediate_matrix[c, ind] = total_production[ind] / scale_prod_ces[ind] * (share_param_inter_prod[c, ind] * scale_prod_ces[ind] *
                                                                                          marginal_cost[ind] / price_domestic_armington[c])**elas_subs_prod[ind]
    return intermediate_matrix

def labour_demand(total_production, scale_prod_ces, share_labour_prod, marginal_cost, wage_labour, elas_subs_prod, Ind):
    labour_input = {}
    for ind in Ind:
        labour_input[ind] = total_production[ind] / scale_prod_ces[ind] * (share_labour_prod[ind] *
                              scale_prod_ces[ind] * marginal_cost[ind] / wage_labour[ind])**elas_subs_prod[ind]
    return labour_input

def capital_demand(total_production, scale_prod_ces, share_capital_prod, marginal_cost, rent_capital, elas_subs_prod, Ind):
    capital_input = {}
    for ind in Ind:
        capital_input[ind] = total_production[ind] / scale_prod_ces[ind] * (share_capital_prod[ind] *
                                                                     scale_prod_ces[ind] * marginal_cost[ind] / rent_capital[ind])**elas_subs_prod[ind]
    return capital_input

def produced_ind_to_com(share_production_to_com, total_production, Ind, Com):
    produced_commodity = {}
    for c in Com:
        produced_commodity[c] = sum(share_production_to_com[ind, c] * total_production[ind] for ind in Ind)
    return produced_commodity

def produced_supply_domestic(produced_commodity, scale_prod_transform, share_cet_prod, price_domestic_produced, price_domestic_produced_consumption, elas_subs_transform, Com):
    produced_supply_domestic = {}
    for c in Com:
        produced_supply_domestic[c] = produced_commodity[c] / scale_prod_transform[c] * ((share_cet_prod[c] * price_domestic_produced[c] * scale_prod_transform[c] / price_domestic_produced_consumption[c])**elas_subs_transform[c])
    return produced_supply_domestic

def produced_supply_export(produced_commodity, scale_prod_transform, share_cet_prod, price_domestic_produced, price_export, elas_subs_transform, Com):
    produced_supply_export = {}
    for c in Com:
        produced_supply_export[c] = produced_commodity[c] / scale_prod_transform[c] * (((1-share_cet_prod[c]) * price_domestic_produced[c] * scale_prod_transform[c] / price_export[c])**elas_subs_transform[c])
    return produced_supply_export

def consumed_domestic(armington_commodity, share_armington_prod, scale_prod_armington, price_domestic_armington, price_domestic_produced_consumption, elas_subs_armington, Com):
    consumed_domestic = {}
    for c in Com:
        consumed_domestic[c] = armington_commodity[c] / scale_prod_armington[c] * (share_armington_prod[c] * scale_prod_armington[c] * price_domestic_armington[c] / price_domestic_produced_consumption[c])**elas_subs_armington[c]
    return consumed_domestic

def consumed_import(armington_commodity, share_armington_prod, scale_prod_armington, price_domestic_armington, price_import, elas_subs_armington, Com):
    consumed_import = {}
    for c in Com:
        consumed_import[c] = armington_commodity[c] / scale_prod_armington[c] * ((1-share_armington_prod[c]) * scale_prod_armington[c] * price_domestic_armington[c] / price_import[c])**elas_subs_armington[c]
    return consumed_import

def price_import(exchange_rate, price_word_import, Com):
    price_import = {}
    for c in Com:
        price_import[c] = exchange_rate * price_word_import[c]
    return price_import

def price_export(exchange_rate, price_word_export, Com):
    price_export = {}
    for c in Com:
        price_export[c] = exchange_rate * price_word_export[c]
    return price_export

def armington_demand(intermediate_input, household_demand, government_demand, invest_demand, Com, Ind):
    armington_demand = {}
    for c in Com:
        armington_demand[c] = sum(intermediate_input[c, ind] for ind in Ind) + household_demand[c] + government_demand[c] + invest_demand[c]
    return armington_demand

def price_production(share_production_to_com, price_domestic_armington, Ind, Com):
    price_prod = {}
    for ind in Ind:
        price_prod[ind] = sum(share_production_to_com[ind, cc] * price_domestic_armington[cc] for cc in Com)
    return price_prod

def price_domestic_produced(scale_prod_transform, share_cet_prod, elas_subs_transform, price_domestic_produced_consumption, price_export, Com):
    price_domestic_produced = {}
    for c in Com:
        if c == 'Com1':
            price_domestic_produced[c] = 1.0
        else:
            price_domestic_produced[c] = (1 / scale_prod_transform[c]) * (share_cet_prod[c] ** elas_subs_transform[c] * price_domestic_produced_consumption[c] ** (1 - elas_subs_transform[c])
                                                                  + (1 - share_cet_prod[c]) ** elas_subs_transform[c] * price_export[c] ** (1 - elas_subs_transform[c])) ** (1 / (1 - elas_subs_transform[c]))
    return price_domestic_produced

def price_domestic_armington(scale_prod_armington, share_armington_prod, elas_subs_armington, price_domestic_produced_consumption, price_import, Com):
    price_domestic_armington = {}
    for c in Com:
        if c == 'Com1':
            price_domestic_armington[c] = 1.0
        else:
            price_domestic_armington[c] = (1 / scale_prod_armington[c]) * (share_armington_prod[c] ** elas_subs_armington[c] * price_domestic_produced_consumption[c] ** (1 - elas_subs_armington[c])
                                                                  + (1 - share_armington_prod[c]) ** elas_subs_armington[c] * price_import[c] ** (1 - elas_subs_armington[c])) ** (1 / (1 - elas_subs_armington[c]))
    return price_domestic_armington

def price_labour(labour_input, total_labour, Ind):
    wage_labour = {}
    for ind in Ind:
        wage_labour[ind] = total_labour / sum(labour_input[ind] for ind in Ind)
    return wage_labour

def price_capital(capital_input, total_capital,Ind):
    rent_capital = {}
    for ind in Ind:
        rent_capital[ind] = total_capital / sum(capital_input[ind] for ind in Ind)
    return rent_capital

def marginal_prod_cost(scale_prod_ces, share_inter_prod, elas_subs_prod, price_domestic_armington, share_labour_prod, share_capital_prod, wage_labour, rent_capital,Ind, Com):
    marginal_cost = {}
    for ind in Ind:
        marginal_cost[ind] = 1/scale_prod_ces[ind] * (sum(share_inter_prod[c, ind]**elas_subs_prod[ind] * price_domestic_armington[c]**(1-elas_subs_prod[ind]) for c in Com)
                            + share_labour_prod[ind]**elas_subs_prod[ind] * wage_labour[ind] ** (1-elas_subs_prod[ind])
                             + share_capital_prod[ind]**elas_subs_prod[ind] * rent_capital[ind] ** (1-elas_subs_prod[ind]))**(1/(1-elas_subs_prod[ind]))
    return marginal_cost

def production_tax(production_tax_rate, total_production, price_production, Ind):
    production_tax = {}
    for ind in Ind:
        production_tax[ind] = production_tax_rate[ind] * total_production[ind] * price_production[ind]
    return production_tax

def total_production(scale_prod_ces, share_param_inter_prod, intermediate_matrix, share_param_labour_prod, share_param_capital_prod,labour_input, capital_input,elasticity_subs_prod, Ind, Com):
    total_production = {}
    for ind in Ind:
        total_production[ind] = scale_prod_ces[ind] * (sum(share_param_inter_prod[c, ind] * intermediate_matrix[c, ind] ** (1-1/elasticity_subs_prod[ind]) for c in Com) +
                                                       share_param_labour_prod[ind] * labour_input[ind] ** (1-1/elasticity_subs_prod[ind]) +
                                                       share_param_capital_prod[ind] * capital_input[ind] ** (1-1/elasticity_subs_prod[ind]))**(elasticity_subs_prod[ind]/(elasticity_subs_prod[ind]-1))
    return total_production

def armington_commodity(scale_prod_armington, share_armington_prod, consumed_domestic, consumed_import, elas_subs_armington, Com):
    armington_commodity = {}
    for c in Com:
        armington_commodity[c] = scale_prod_armington[c] * (share_armington_prod[c] * consumed_domestic[c] ** (1-1/elas_subs_armington[c]) +
                                                           (1-share_armington_prod[c]) * consumed_import[c] ** (1-1/elas_subs_armington[c]))**(elas_subs_armington[c]/(elas_subs_armington[c]-1))
    return armington_commodity