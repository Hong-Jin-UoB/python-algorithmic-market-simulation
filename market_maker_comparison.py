import bse_adaptive as bse
import random

def run_q4_session(args):
    trial_id, p1, p2, duration, csv_file = args
    
    try:
        # Load the IBM price-offset schedule.
        offset_info = bse.offset_from_file(csv_file, 0, 1, 100, duration)
        offset_fn, offset_args = offset_info
        sup_range = [100, 200, offset_fn, offset_args]
        dem_range = [100, 200, offset_fn, offset_args]
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sup_range = [100, 200]
        dem_range = [100, 200]

    supply_schedule = [{'from': 0, 'to': duration, 'ranges': [sup_range], 'stepmode': 'fixed'}]
    demand_schedule = [{'from': 0, 'to': duration, 'ranges': [dem_range], 'stepmode': 'fixed'}]

    order_sched = {
        'sup': supply_schedule,
        'dem': demand_schedule,
        'interval': 30,
        'timemode': 'drip-poisson' 
    }

    # Compare five MMM01 and five MMM02 traders in the same market.
    sellers_spec = [
        ('MMM01', 5, p1), ('MMM02', 5, p2), 
        ('ZIP', 5, None), ('ZIC', 5, None), ('GVWY', 2, None)
    ]
    buyers_spec = [
        ('MMM01', 5, p1), ('MMM02', 5, p2), 
        ('ZIP', 5, None), ('ZIC', 5, None), ('GVWY', 2, None)
    ]
    traders_spec = {'sellers': sellers_spec, 'buyers': buyers_spec}

    dump_flags = {'dump_blotters': False, 'dump_lobs': False, 'dump_strats': False, 
                  'dump_avgbals': False, 'dump_tape': False}
    
    # Run the adaptive BSE engine.
    market_results = bse.market_session(
        f"run_{trial_id}", 0, duration, traders_spec, order_sched, dump_flags, False
    )
    
    profits_01 = [t['balance'] for t in market_results if t['ttype'] == 'MMM01']
    profits_02 = [t['balance'] for t in market_results if t['ttype'] == 'MMM02']
    
    avg_01 = sum(profits_01) / len(profits_01) if profits_01 else 0
    avg_02 = sum(profits_02) / len(profits_02) if profits_02 else 0
    
    return (avg_01, avg_02)
