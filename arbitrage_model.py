import pyomo.environ as pyo
from pyomo.opt import SolverFactory

import pandas as pd

df = pd.read_csv('data/20170801damlbmp_zone_csv/20170801damlbmp_zone.csv',\
                 index_col="Time Stamp")
nyc_df=df[df["Name"]=='N.Y.C.'][['LBMP ($/MWHr)']]
nyc_df.columns = ['cost']


mcp = 100 # Max Charge Power
mdp = 100 # Max Discharge Power
d = 200   # Discharge energy capacity(Battery Energy Capacity)
e = .85   # Round Trip efficiency
ddl = 200 # Daily Energy Discharge Limit


def battery_arbitrage(mcp, mdp, d, e, ddl):
    """
    This is a battery arbitrage model that can optimize for profit given a set
    of parameters across a 24 hour time period in one hour time steps.
    Inputs:
        mcp:int: The max power the battery can charge at (KW)
        mdp:int: The max power the battery can discharge at (KW)
        d:int: The battery capacity (KWh)
        e:float: Round trip energy efficiency range(0,1)
        ddl:int: The daily discharge limit (KWh)
     Outputs:tuple:
         revenue:float: The total money made over the optimization horizon
         charging_cost:float: The cost of charging for the day ($)
         total_discharge:float: Total energy discharged by the battery (KWh)
         net_power_ts:pd.Series: Power differential of the battery at every
                                 time step
         lbmp:pd.Series: The spot price of energy at every time step
         revenue_ts:pd.Series: The revenue at every time step
    """
    model = pyo.ConcreteModel()
    T = 24
    # SETS #
    model.t = pyo.RangeSet(1, T)
    model.b = pyo.Set(initialize=[1])

    # VARIABLES #
    model.Pd = pyo.Var(model.t, model.b, bounds=(0, mcp),initialize=0)
    model.Pg = pyo.Var(model.t, model.b, bounds=(0, mdp),initialize=0)
    model.C = pyo.Var(model.t, bounds=(0, d), initialize=0)

    # CONSTRAINTS #
    model.batterycharge = pyo.ConstraintList()
    for t in model.t:
        for b in model.b:
            if t > 1:
                model.batterycharge.add(model.C[t] == model.C[t-1] + e*(model.Pd[t,b]) - model.Pg[t,b])
            else:
                pyo.Constraint.Skip
                model.batterycharge.add(model.C[1]==0)

    model.dailydischarge = pyo.ConstraintList()
    for b in model.b:
        model.dailydischarge.add(sum(model.Pg[t,b] for t in model.t)<=ddl)

    # OBJECTIVE #
    model.obj = pyo.Objective(expr=sum(model.Pg[i]*nyc_df.cost[i[0]-1] - \
                                       model.Pd[i]*nyc_df.cost[i[0]-1] for i in model.t*model.b),
                                       sense=pyo.maximize )

    # SOLVE #
    opt = SolverFactory('glpk')
    results = opt.solve(model)

    # RESULTS #

    charge_hist = [pyo.value(x) for x in model.C.values()]
    purchase_hist = [pyo.value(x) for x in model.Pd.values()]
    sale_hist = [pyo.value(x) for x in model.Pg.values()]

    df = pd.DataFrame({'charge ctate(KWh)': charge_hist,
                       'purchases(KW)': purchase_hist,
                       'sales(KW)': sale_hist,
                       'spot_price($)': nyc_df.cost.to_list()},
                      index = pd.to_datetime(nyc_df.index))

    revenue = model.obj.expr()/1000
    revenue = round(revenue, 2)

    charging_cost = sum(df['purchases(KW)']*df['spot_price($)'])/1000
    charging_cost = round(charging_cost, 2)

    total_discharge = sum(df['sales(KW)'])

    net_power_ts = df['sales(KW)'] - df['purchases(KW)']

    lbmp = df['spot_price($)']/1000

    revenue_ts = (df['sales(KW)']*df['spot_price($)'] - df['purchases(KW)']* \
                  df['spot_price($)'])/1000
    revenue_ts = round(revenue_ts, 2)

    return(revenue, charging_cost, total_discharge, net_power_ts, lbmp, revenue_ts)

battery_arbitrage(mcp, mdp, d, e, ddl)
