# weights.py
import  RCAIDE
from RCAIDE.Framework.Core import Data  
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import Propulsion       as Propulsion
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import Transport        as Transport
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import Common           as Common
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import General_Aviation as General_Aviation
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import BWB              as BWB
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import Human_Powered    as HP
from RCAIDE.Library.Methods.Weights.Correlation_Buildups import UAV              as UAV
from RCAIDE.Library.Methods.Weights.Physics_Based_Buildups import Electric       as Electric
 
from RCAIDE.load import load as load_results
from RCAIDE.save import save as save_results 

import numpy as  np 
import sys

sys.path.append('../../Vehicles')
# the analysis functions

from Boeing_737             import vehicle_setup as transport_setup
from Cessna_172             import vehicle_setup as general_aviation_setup
from Boeing_BWB_450         import vehicle_setup as bwb_setup
from Stopped_Rotor_EVTOL    import vehicle_setup as evtol_setup
from Solar_UAV              import vehicle_setup as uav_setup
from Human_Powered_Glider   import vehicle_setup as hp_setup

def main(): 
    Transport_Aircraft_Test()
    BWB_Aircraft_Test()
    General_Aviation_Test()
    Human_Powered_Aircraft_Test()
    EVTOL_Aircraft_Test()
    UAV_Test()
    return


def Transport_Aircraft_Test():  
    method_types = ['RCAIDE', 'FLOPS Simple', 'FLOPS Complex', 'Raymer']
    
    for method_type in method_types:
        print('Testing Method: '+method_type) 
        
        weight_analysis                               = RCAIDE.Framework.Analyses.Weights.Weights_Transport()
        weight_analysis.vehicle                       = transport_setup() 
        weight_analysis.method                        = method_type 
        weight                                        = weight_analysis.evaluate() 
    
        #save_results(weight, 'weights_'+method_type.replace(' ','_')+'.res')
        old_weight = load_results('weights_'+method_type.replace(' ','_')+'.res')
    
        check_list = [
            'payload_breakdown.total',        
            'payload_breakdown.passengers',             
            'payload_breakdown.baggage',                                   
            'structural_breakdown.wing',            
            'structural_breakdown.fuselage',        
            'propulsion_breakdown.total',      
            'structural_breakdown.nose_landing_gear',    
            'structural_breakdown.main_landing_gear',                   
            'systems_breakdown.total',         
            'systems_breakdown.furnish',      
            'structural_breakdown.horizontal_tail', 
            'structural_breakdown.vertical_tail',
            'empty',  
        ]
    
        # do the check
        for k in check_list:
            print(k) 
            old_val = old_weight.deep_get(k)
            new_val = weight.deep_get(k)
            err = (new_val-old_val)/old_val
            print('Error:' , err)
            assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     
    
            print('')
            
    return 

def General_Aviation_Test():
     
    weight_analysis          = RCAIDE.Framework.Analyses.Weights.Weights_General_Aviation()
    weight_analysis.vehicle  = general_aviation_setup()
    weight                   = weight_analysis.evaluate()
    
    #save_results(weight, 'weights_General_Aviation.res')
    old_weight = load_results('weights_General_Aviation.res')

    check_list = [
        'empty',
        'structural_breakdown.wing',
        'structural_breakdown.fuselage',
        'structural_breakdown.total',
        'propulsion_breakdown.total',   
        'systems_breakdown.total',  
    ]

    # do the check
    for k in check_list:
        print(k)

        old_val = old_weight.deep_get(k)
        new_val = weight.deep_get(k)
        err = (new_val-old_val)/old_val
        print('Error:' , err)
        assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     

        print('')
    return 
        
def BWB_Aircraft_Test():
    
    weight_analysis          = RCAIDE.Framework.Analyses.Weights.Weights_BWB()
    weight_analysis.vehicle  = bwb_setup()
    weight                   = weight_analysis.evaluate()
    
    #save_results(weight, 'weights_BWB.res')
    old_weight = load_results('weights_BWB.res')
    
    check_list = [
        'empty',
        'structural_breakdown.wing', 
        'structural_breakdown.total',
        'propulsion_breakdown.total',   
        'systems_breakdown.total',  
    ]

    # do the check
    for k in check_list:
        print(k)

        old_val = old_weight.deep_get(k)
        new_val = weight.deep_get(k)
        err = (new_val-old_val)/old_val
        print('Error:' , err)
        assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     

        print('')
        
    return

def EVTOL_Aircraft_Test():
    new_regression           = False # ONLY turn to True for a new regression, typically left false
    weight_analysis          = RCAIDE.Framework.Analyses.Weights.Weights_EVTOL()
    weight_analysis.vehicle  = evtol_setup(new_regression) 
    weight                   = weight_analysis.evaluate() 

    #save_results(weight, 'weights_EVTOL.res')
    old_weight = load_results('weights_EVTOL.res')
    
    check_list = [
        'empty', 
        'structural_breakdown.total',
        'propulsion_breakdown.total',   
        'systems_breakdown.total',  
    ]

    # do the check
    for k in check_list:
        print(k)

        old_val = old_weight.deep_get(k)
        new_val = weight.deep_get(k)
        err = (new_val-old_val)/old_val
        print('Error:' , err)
        assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     

        print('')
     
    return

        
def Human_Powered_Aircraft_Test(): 
    weight_analysis          = RCAIDE.Framework.Analyses.Weights.Weights_Human_Powered()
    weight_analysis.vehicle  = hp_setup()
    weight                   = weight_analysis.evaluate()    

    #save_results(weight, 'weights_Human_Powered.res')
    old_weight = load_results('weights_Human_Powered.res')
    
    check_list = [
        'empty', 
    ]

    # do the check
    for k in check_list:
        print(k)

        old_val = old_weight.deep_get(k)
        new_val = weight.deep_get(k)
        err = (new_val-old_val)/old_val
        print('Error:' , err)
        assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     

        print('')
        
    return       


def UAV_Test():

    weight_analysis          = RCAIDE.Framework.Analyses.Weights.Weights_UAV()
    weight_analysis.vehicle  = uav_setup()
    weight                   = weight_analysis.evaluate() 

    #save_results(weight, 'weights_UAV.res')
    old_weight = load_results('weights_UAV.res')
    
    check_list = [
        'empty', 
    ]

    # do the check
    for k in check_list:
        print(k) 
        old_val = old_weight.deep_get(k)
        new_val = weight.deep_get(k)
        err = (new_val-old_val)/old_val
        print('Error:' , err)
        assert np.abs(err) < 1e-6 , 'Check Failed : %s' % k     

        print('') 
    
    return


if __name__ == '__main__':
    main()