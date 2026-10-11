import bse
import numpy as np
import os

# get dynamic path
base_dir = os.path.dirname(os.path.abspath(__file__))

csv_file = os.path.join(base_dir, 'data', 'ibm_price_offsets.csv')


start_time = 0
end_time = 900  # 15 min 5 observe + 10 trade

def run_sim(args):
    """
    Run one parameter configuration for N trials and return mean profit.
    args: (n_past, bid_pct, ask_delt, market_type, n_trials)
    """
    n_past, bid_pct, ask_delt, market_type, n_trials = args
    
    # MMM01
    mm_params = {
        'n_past_trades': n_past,
        'bid_percent': bid_pct,
        'ask_delta': ask_delt
    }
    
    # traders
    sellers = [('ZIP', 5), ('ZIC', 5), ('GVWY', 5), ('SHVR', 3)]
    buyers =  [('ZIP', 5), ('ZIC', 5), ('GVWY', 5), ('SHVR', 3)]
    mm = [('MMM01', 1, mm_params)]
    
    traders = {
        'sellers': sellers, 
        'buyers': buyers,
        'mrktmakers': mm
    }
    
    # Market
    min = 100
    max = 200
    
    if market_type == 'Real':
        # IBM 
        offset_events = bse.schedule_offsetfn_read_file(csv_file, col_t=1, col_p=5, scale_factor=50)
        # must be [[ ... ]] !!!!!!

        offset = (bse.schedule_offsetfn_from_eventlist, [ [end_time, offset_events] ])
        
        sup_range = [min, max, offset]
        dem_range = [min, max, offset]
    else:
        # static market
        sup_range = [min, max]
        dem_range = [min, max]

    sup_sched = [{'from': 0, 'to': end_time, 'ranges': [sup_range], 'stepmode': 'fixed'}]
    dem_sched = [{'from': 0, 'to': end_time, 'ranges': [dem_range], 'stepmode': 'fixed'}]
    
    order_sched = {
        'sup': sup_sched, 'dem': dem_sched,
        'interval': 30, 'timemode': 'drip-poisson'
    }
    
    # close IO output (speed up)
    dump_flags = {
        'dump_blotters': False, 'dump_lobs': False, 'dump_strats': False, 
        'dump_avgbals': False, 'dump_tape': False
    }

    profits = []
    for i in range(n_trials):
        trial_id = f"p_{market_type}_{n_past}_{bid_pct}_{ask_delt}_{i}"
        
        try:
            balances = bse.market_session(trial_id, start_time, end_time, 
                                          traders, order_sched, 
                                          dump_flags, False)
            
            profit = balances.get('M00', 0) - 500
            profits.append(profit)
            
        except Exception as e:

            error_msg = f"!!!CRASH!!! Error in {trial_id}: {str(e)} | File: {csv_file}"
            return (n_past, bid_pct, ask_delt, market_type, error_msg)
            
    return (n_past, bid_pct, ask_delt, market_type, np.mean(profits))
