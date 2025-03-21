import numpy as np
import pandas as pd
from scipy import optimize as opt

import Calibration
import Consumer as Cons
import Producer as Prod
import MacroEconomy as Macro
import CGESystem as CGE

sam_table = pd.read_excel(r"D:\OneDriveSyn\OneDrive - The University of Hong Kong - Connect\SynJunex\Project\HKU\CGE\ICountry-2Input-2Consumer-3Sector-Invest-Trade\Data\SAM.xlsx")
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

    vars = Calibration.CGE_IO_Data(sam_table, Ind, Com)
    params = Calibration.CGE_Exo_Param(vars, Ind, Com)

    price_domestic_armington_array = np.array([1.0, 1.0, 1.0])
    #price_commodity_array = np.array([1.0, 3.0, 3.0])
    wage_labour = params.wage_labour
    rent_capital = params.rent_capital

    labour_input = vars.labour_input
    capital_input = vars.capital_input
    total_production = vars.total_production
    armington_commodity = vars.armington_commodity

    while (error_term > max_tolerance) & (iteration < max_iteration):
        iteration += 1
        cge_args = [vars, params, Ind, Com, Fac, Con, price_domestic_armington_array, total_production, armington_commodity, labour_input, capital_input, wage_labour, rent_capital]

        print('Iteration =', iteration)
        print('Initialized product price =', price_domestic_armington_array)

        results = opt.root(CGE.cge_system, price_domestic_armington_array, args=cge_args, method='lm', tol=1e-5)
        price_domestic_armington_array = results.x
        price_domestic_armington_array[0] = 1.0
        price_domestic_armington = dict(zip(Com, price_domestic_armington_array))

        price_utility = Cons.price_utility(params.scale_hoh_utility, params.share_hoh_utility, params.elas_subs_utility, price_domestic_armington, Com)
        value_added = Cons.total_value_added(wage_labour, labour_input, rent_capital, capital_input, Ind)

        price_production = Prod.price_production(params.share_production_to_com, price_domestic_armington, Ind, Com)
        production_tax = Prod.production_tax(params.production_tax_rate, total_production, price_production, Ind)
        government_income = Cons.total_government_income(production_tax, Ind)
        total_government_income = Cons.total_government_income(production_tax, Ind)

        household_demand = Cons.household_consumption(params.share_hoh_utility, price_domestic_armington, params.elas_subs_utility, price_utility, params.scale_hoh_utility, params.saving_rate_hoh, value_added, Com)
        government_demand = Cons.government_consumption(params.share_gov_utility, price_domestic_armington, total_government_income, Com)

        utility_hoh = Cons.consumer_utility(params.scale_hoh_utility, params.share_hoh_utility, household_demand, params.elas_subs_utility, Com)

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

        # Assume
        world_price = price_domestic_produced_consumption
        trade_balance = Macro.trade_balance(price_export, produced_supply_export, price_import, consumed_import, investment_foreign, Com)
        marginal_cost = Prod.marginal_prod_cost(params.scale_prod_ces, params.share_inter_prod, params.elas_subs_prod, price_domestic_armington, params.share_labour_prod, params.share_capital_prod, wage_labour, rent_capital, Ind, Com)

        # Capital, Commodity, Factor endowment, Armington good
        price_domestic_armington_process = Prod.price_domestic_armington(params.scale_prod_armington, params.share_armington_prod, params.elas_subs_armington, price_domestic_produced_consumption, price_import, Com)
        total_production_process = Prod.total_production(params.scale_prod_ces, params.share_inter_prod, intermediate_input, params.share_labour_prod, params.share_capital_prod, labour_input, capital_input, params.elas_subs_prod, Ind, Com)
        armington_commodity_process = Prod.armington_commodity(params.scale_prod_armington, params.share_armington_prod, consumed_domestic, consumed_import, params.elas_subs_armington, Com)

        GDP1 = Macro.gdp_use(params.share_production_to_com, price_domestic_armington, total_production, intermediate_input, Ind, Com)
        GDP2 = Macro.gdp_consumption(price_domestic_armington, household_demand, government_demand, investment_goods, price_export, produced_supply_export, price_import, consumed_import, Com)
        GDP3 = Macro.gdp_value_added(wage_labour, labour_input, rent_capital, capital_input, government_income, Ind)

        final_price_commodity = price_domestic_armington
        final_total_production = total_production_process

        processed_model = {}
        for ind in Ind:
            processed_model[ind] = ((total_production[ind] - total_production_process[ind]) ** 2) ** (1 / 2)

        distance_iter = sum(processed_model[ind] for ind in Ind)
        print('Distance at iteration', iteration, '=', distance_iter)

        price_domestic_armington = (adjust_rate * price_domestic_armington_process[c] + (1-adjust_rate) * price_domestic_armington[c] for c in Com)
        total_production = (adjust_rate * total_production_process[ind] + (1-adjust_rate) * total_production[ind] for ind in Ind)
        capital_input = (adjust_rate * capital_input[ind] + (1-adjust_rate) * capital_input[ind] for ind in Ind)
        armington_commodity = (adjust_rate * armington_commodity_process[c] + (1-adjust_rate) * armington_commodity[c] for c in Com)

        print("Model solved, price = ", price_domestic_armington_array)
        return final_price_commodity, utility_hoh, household_demand, government_demand, investment_goods, final_total_production, intermediate_input, price_utility, marginal_cost, GDP1, GDP2, GDP3

if __name__ == '__main__':
    final_price_commodity, utility_hoh, household_demand, government_demand, investment_goods, final_total_production, intermediate_input, price_utility, marginal_cost, GDP1, GDP2, GDP3 = execute()
    print(final_price_commodity)
    print(household_demand)
    print([GDP1, GDP2, GDP3])
