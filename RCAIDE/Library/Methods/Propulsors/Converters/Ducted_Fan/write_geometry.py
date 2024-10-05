# RCAIDE/Library/Methods/Propulsor/Ducted_Fan_Propulsor/write_geometry.py
# 
# Created: Sep 2024, M. Clarke 

# ---------------------------------------------------------------------------------------------------------------------- 
#  Imports
# ----------------------------------------------------------------------------------------------------------------------
from RCAIDE.Library.Methods.Geometry.Airfoil import  import_airfoil_geometry
from .purge_files import purge_files   
 
# ---------------------------------------------------------------------------------------------------------------------- 
# Write Geometry 
# ---------------------------------------------------------------------------------------------------------------------- 
def write_geometry(dfdc_object,run_script_path):
    """This function writes the translated aircraft geometry into text file read 
    by DFDC when it is called 
    """     
    # unpack inputs 
    case_file   = dfdc_object.geometry.tag + '.case'   
    purge_files([case_file]) 
    geometry             = open(case_file,'w') 
    with open(case_file,'w') as geometry:
        make_header_text(dfdc_object,geometry)
        make_duct_text(dfdc_object,geometry)
        make_separator_text(dfdc_object,geometry) 
        make_center_body_text(dfdc_object,geometry) 
    return

def make_header_text(dfdc_object,geometry):  
    """This function writes the header using the template required for the DFDC executable to read
 
    """      
    header_text = \
'''DFDC Version  0.70 
Bladed rotor + actdisk stator test case                                             

OPER
!        Vinf         Vref          RPM          RPM
  0.00000E+00   50.000       8000.0          0.0    
!         Rho          Vso          Rmu           Alt
   1.2260       340.00      0.17800E-04  0.00000E+00
!       XDwake        Nwake
  0.80000               20
!       Lwkrlx
            F
ENDOPER

AERO
!  #sections
     1
!   Xisection
  0.00000E+00
!       A0deg        dCLdA        CLmax         CLmin
  0.00000E+00   6.2800       1.5000      -1.0000    
!  dCLdAstall     dCLstall      Cmconst         Mcrit
  0.50000      0.20000      0.00000E+00  0.70000    
!       CDmin      CLCDmin     dCDdCL^2
  0.12000E-01  0.10000      0.50000E-02
!       REref        REexp
  0.20000E+06  0.35000    
ENDAERO

ROTOR
!       Xdisk        Nblds       NRsta
  0.12000                6           11
!  #stations
    10
!           r        Chord         Beta
  0.50494E-01  0.68423E-01   77.017    
  0.61571E-01  0.63974E-01   64.527    
  0.72648E-01  0.59613E-01   55.142    
  0.83725E-01  0.55667E-01   48.577    
  0.94801E-01  0.52241E-01   43.957    
  0.10588      0.49327E-01   40.191    
  0.11696      0.46879E-01   37.057    
  0.12803      0.44839E-01   34.396    
  0.13911      0.43155E-01   32.088    
  0.15019      0.41782E-01   30.041    
ENDROTOR


AERO
!  #sections
     1
!   Xisection
  0.00000E+00
!       A0deg        dCLdA        CLmax         CLmin
  0.00000E+00   6.2800       1.0000      -1.5000    
!  dCLdAstall     dCLstall      Cmconst         Mcrit
  0.50000      0.20000      0.00000E+00  0.70000    
!       CDmin      CLCDmin     dCDdCL^2
  0.12000E-01 -0.10000      0.50000E-02
!       REref        REexp          TOC      dCDdCL^2
  0.20000E+06  0.35000      0.10000      0.20000E-01
ENDAERO

ACTDISK
! Xdisk   NRPdef
  0.22     11
! #stations
  3
! r     BGam
 0.02   -10.0
 0.06   -10.0
 0.10   -10.0
ENDACTDISK


DRAGOBJ
!  #pts
     4
!           x            r          CDA
  0.40000E-01  0.60000E-01  0.40000E-01
  0.40000E-01  0.80000E-01  0.35000E-01
  0.40000E-01  0.10000      0.30000E-01
  0.40000E-01  0.12000      0.30000E-01
ENDDRAGOBJ

'''

    geometry.write(header_text)     
    return  


def make_duct_text(dfdc_object,geometry):  
    """This function writes the operating conditions using the template required for the DFDC executable to read
 
    """      
    duct_header = \
'''GEOM
FatDuct + CB test case
''' 
    geometry.write(duct_header)
    
    
    if len(dfdc_object.geometry.Airfoil):
        airfoil_filename = dfdc_object.geometry.airfoil
        airfoil_geometry_data = import_airfoil_geometry(airfoil_filename)
        dim = len(airfoil_geometry_data.x_coordinates)
                   
        for i in range(dim - 1):
            if i == int(dim/2):
                pass  
            elif airfoil_geometry_data.y_coordinates[i] < 0.0:
                case_text = '\t' + format(airfoil_geometry_data.x_coordinates[i], '.7f')+ "   " + format(airfoil_geometry_data.y_coordinates[i], '.7f') + "\n" 
                geometry.write(case_text)
            else:   
                case_text = '\t' + format(airfoil_geometry_data.x_coordinates[i], '.7f')+ "    " + format(airfoil_geometry_data.y_coordinates[i], '.7f') + "\n" 
                geometry.write(case_text)
    else:
        duct_geometry = \
'''     0.306379    0.035928
     0.304409    0.036661
     0.299975    0.038172
     0.295358    0.039548
     0.290635    0.040753
     0.285782    0.041792
     0.280790    0.042672
     0.275673    0.043396
     0.270468    0.043968
     0.265187    0.044388
     0.259796    0.044661
     0.254106    0.044798
     0.247873    0.044837
     0.241073    0.044839
     0.234083    0.044846
     0.227046    0.044856
     0.220000    0.044863
     0.213314    0.044869
     0.206626    0.044876
     0.199935    0.044882
     0.193244    0.044889
     0.186554    0.044896
     0.179864    0.044902
     0.173172    0.044909
     0.166484    0.044915
     0.159797    0.044922
     0.153112    0.044929
     0.146433    0.044936
     0.139760    0.044941
     0.133105    0.044949
     0.126505    0.044956
     0.120000    0.044956
     0.113424    0.044972
     0.107220    0.045002
     0.101441    0.044960
     0.095654    0.044806
     0.089898    0.044553
     0.084235    0.044200
     0.078649    0.043739
     0.073148    0.043167
     0.067743    0.042481
     0.062438    0.041674
     0.057235    0.040743
     0.052163    0.039689
     0.047230    0.038507
     0.042442    0.037191
     0.037817    0.035743
     0.033376    0.034163
     0.029135    0.032449
     0.025113    0.030605
     0.021331    0.028633
     0.017808    0.026539
     0.014565    0.024329
     0.011618    0.022011
     0.008984    0.019594
     0.006673    0.017087
     0.004697    0.014494
     0.003059    0.011823
     0.001765    0.009075
     0.000818    0.006237
     0.000220    0.003272
     0.000000    0.000000'''
    geometry.write(duct_geometry)      
    return  
 
def make_separator_text(dfdc_object,geometry):  
    """This function writes the operating conditions using the template required for the DFDC executable to read 
    """      
    separator_text = \
'''
  999.0 999.0
'''
    geometry.write(separator_text) 
    return 

def make_center_body_text(dfdc_object,geometry):  
    """This function writes the rotor using the template required for the DFDC executable to read 
    """
     
    center_geometry = \
'''     0.304542    0.159526
     0.300090    0.161360
     0.294089    0.163786
     0.287155    0.166525
     0.279918    0.169313
     0.272562    0.172071
     0.265159    0.174775
     0.257734    0.177412
     0.250271    0.179992
     0.242791    0.182506
     0.235295    0.184954
     0.227802    0.187328
     0.220289    0.189634
     0.212770    0.191870
     0.205266    0.194028
     0.197773    0.196105
     0.190295    0.198100
     0.182837    0.200009
     0.175399    0.201830
     0.167998    0.203559
     0.160654    0.205185
     0.153344    0.206710
     0.146087    0.208129
     0.138907    0.209434
     0.131841    0.210615
     0.124987    0.211651
     0.118379    0.212516
     0.111879    0.213217
     0.105460    0.213762
     0.099122    0.214146
     0.092868    0.214367
     0.086702    0.214422
     0.080632    0.214307
     0.074675    0.214022
     0.068839    0.213562
     0.063131    0.212926
     0.057569    0.212114
     0.052173    0.211126
     0.046954    0.209961
     0.041929    0.208621
     0.037125    0.207114
     0.032572    0.205448
     0.028297    0.203631
     0.024324    0.201678
     0.020684    0.199606
     0.017398    0.197435
     0.014488    0.195183
     0.011963    0.192867
     0.009829    0.190499
     0.008090    0.188086
     0.006750    0.185635
     0.005819    0.183156
     0.005307    0.180666
     0.005219    0.178163
     0.005587    0.175711
     0.006428    0.173371
     0.007726    0.171180
     0.009456    0.169156
     0.011594    0.167295
     0.014136    0.165586
     0.017089    0.164017
     0.020469    0.162580
     0.024289    0.161274
     0.028565    0.160102
     0.033285    0.159068
     0.038452    0.158177
     0.044042    0.157425
     0.050036    0.156813
     0.056422    0.156332
     0.063182    0.155973
     0.070302    0.155724
     0.077764    0.155572
     0.085568    0.155504
     0.093708    0.155502
     0.102173    0.155550
     0.110962    0.155632
     0.120000    0.155724
     0.126668    0.155795
     0.133170    0.155883
     0.139589    0.155993
     0.146086    0.156122
     0.152658    0.156266
     0.159302    0.156421
     0.166019    0.156585
     0.172800    0.156754
     0.179623    0.156925
     0.186436    0.157092
     0.193212    0.157254
     0.199963    0.157409
     0.206680    0.157556
     0.213355    0.157692
     0.220000    0.157815
     0.226000    0.157918
     0.231995    0.158012
     0.237979    0.158097
     0.243952    0.158171
     0.249925    0.158235
     0.255902    0.158290
     0.261888    0.158336
     0.267883    0.158373
     0.273872    0.158400
     0.279876    0.158420
     0.285849    0.158434
     0.291632    0.158440
     0.296938    0.158442
     0.301213    0.158441
     0.304466    0.158439'''
    
    end_text = \
'''
ENDGEOM
'''  
    # Insert inputs into the template
    center_body_text = center_geometry + end_text  

    geometry.write(center_body_text) 
    return  