import numpy as np
import Calibration as Calibration
import Consumer as Cons
import Producer as Prod
import MacroEconomy as Macro

def cge_system(price_commodity_array, args):
    (vars, params, Ind, Com, Fac, Con, price_domestic_armington_array, total_production, armington_commodity, labour_input, capital_input, wage_labour, rent_capital) = args
    price_domestic_armington = dict(zip(Com, price_domestic_armington_array))

    price_utility = Cons.price_utility(params.scale_hoh_utility, params.share_hoh_utility, params.elas_subs_utility, price_domestic_armington, Com)
    value_added = Cons.total_value_added(wage_labour, labour_input, rent_capital, capital_input, Ind)
    price_production = Prod.price_production(params.share_production_to_com, price_domestic_armington, Ind, Com)
    production_tax = Prod.production_tax(params.production_tax_rate, total_production, price_production, Ind)
    government_income = Cons.total_government_income(production_tax, Ind)
    total_government_income = Cons.total_government_income(production_tax, Ind)
    household_demand = Cons.household_consumption(params.share_hoh_utility, price_domestic_armington, params.elas_subs_utility, price_utility, params.scale_hoh_utility, params.saving_rate_hoh, value_added, Com)
    government_demand = Cons.government_consumption(params.share_gov_utility, price_domestic_armington, government_income, Com)

    household_saving = Cons.household_saving(params.saving_rate_hoh, value_added)
    government_saving = Cons.government_saving(params.saving_rate_gov, government_income)
    total_savings = Cons.total_saving(household_saving, government_saving)
    total_investment = Cons.total_investment(total_savings)
    investment_goods = Cons.investment_goods(params.share_invest_utility, total_investment, price_domestic_armington, Com)
    investment_foreign = Cons.investment_foreign(investment_goods, total_investment, Com)

    marginal_cost = Prod.price_commodity_to_marginal_cost(params.share_production_to_com, price_domestic_armington, params.production_tax_rate, Ind, Com)
    intermediate_input = Prod.intermediate_demand(total_production, params.scale_prod_ces, params.share_inter_prod, marginal_cost, price_domestic_armington, params.elas_subs_prod, Ind, Com)
    labour_input = Prod.labour_demand(total_production, params.scale_prod_ces, params.share_labour_prod, marginal_cost, wage_labour, params.elas_subs_prod, Ind)
    capital_input = Prod.capital_demand(total_production, params.scale_prod_ces, params.share_capital_prod, marginal_cost, rent_capital, params.elas_subs_prod, Ind)

    price_import = Prod.price_import(params.exchange_rate, params.price_word_import, Com)
    price_export = Prod.price_export(params.exchange_rate, params.price_word_export, Com)

    produced_commodity = Prod.produced_ind_to_com(params.share_production_to_com, total_production, Ind, Com)
    price_domestic_produced = Prod.price_domestic_produced(params.scale_prod_transform, params.share_cet_prod, params.elas_subs_transform, params.price_domestic_produced_consumption, price_export, Com)
    price_domestic_produced_consumption = price_domestic_produced

    produced_supply_domestic = Prod.produced_supply_domestic(produced_commodity, params.scale_prod_transform, params.share_cet_prod, price_domestic_produced, price_domestic_produced_consumption, params.elas_subs_transform, Com)
    produced_supply_export = Prod.produced_supply_export(produced_commodity, params.scale_prod_transform, params.share_cet_prod, price_domestic_produced, price_export, params.elas_subs_transform, Com)

    consumed_domestic = Prod.consumed_domestic(armington_commodity, params.share_armington_prod, params.scale_prod_armington, price_domestic_armington, price_domestic_produced_consumption, params.elas_subs_armington, Com)
    consumed_import = Prod.consumed_import(armington_commodity, params.share_armington_prod, params.scale_prod_armington, price_domestic_armington, price_import, params.elas_subs_armington, Com)

    wage_labour = Prod.price_labour(labour_input, vars.total_labour_demand, Ind)
    rent_capital = Prod.price_capital(capital_input, vars.total_capital_demand, Ind)

    marginal_cost = Prod.marginal_prod_cost(params.scale_prod_ces, params.share_inter_prod, params.elas_subs_prod, price_domestic_armington, params.share_labour_prod, params.share_capital_prod, wage_labour, rent_capital, Ind, Com)

    error_labour = Macro.labour_clearing(labour_input, vars.total_labour_demand, Ind)
    error_capital = Macro.capital_clearing(capital_input, vars.total_capital_demand, Ind)
    error_com = Macro.commodity_clearing(params.share_production_to_com, total_production, consumed_import, marginal_cost, params.production_tax_rate, price_import, intermediate_input, price_domestic_armington, produced_supply_export, price_export, household_demand, government_demand, investment_goods, Com, Ind)
    error_commodity = [error_com[cc] for cc in Com]
    error_list = np.append(error_commodity, [error_labour, error_capital])
    return error_list