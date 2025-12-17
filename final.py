import streamlit as st
#st.write("hellow world")

#import streamlit as st
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#my own functions
import math
import matplotlib.pyplot as plt
import numpy as np

class appl_input:
    def __init__(self,dd,nc,mw):
        self.dd = dd
        self.nc = nc
        self.mw = mw

class generic_inputs:
    def __init__(self,elec_price_dmwh,discount_rate):
        self.elec_price_dmwh = elec_price_dmwh
        self.discount_rate = discount_rate

#dd,nc,mw
appl_list = [
    appl_input(4,300,100),
    appl_input(0.5,5000,10),
    appl_input(1,300,100),
]

class value_f:
    def __init__(self,v2g,v1g,hvac,hpth,std_dev_vf):
        self.v2g = v2g
        self.v1g = v1g
        self.hvac = hvac
        self.hpth = hpth
        self.std_dev_vf = std_dev_vf


class tech_input_V2G:
    def __init__(self,batcap_kwh,rt_effy,chargerpower_kw,daily_charge_E):
        self.batcap_kwh = batcap_kwh
        self.rt_effy = rt_effy
        self.chargerpower_kw = chargerpower_kw
        self.daily_charge_E = daily_charge_E

class cons_input_V2G:
    def __init__(self,gmc,wta_base,wta_hour,base_pt):
        self.gmc = gmc
        self.wta_base = wta_base
        self.wta_hour = wta_hour
        self.base_pt = base_pt

class cost_input_V2G:
    def __init__(self,eol_costs_pc,charger_costs_dc,lifetime_y,oam_pi):
        self.eol_costs_pc = eol_costs_pc
        self.charger_costs_dc = charger_costs_dc
        self.lifetime_y = lifetime_y
        self.oam_pi = oam_pi

class tech_input_V1G:
    def __init__(self,batcap_kwh,rt_effy,chargerpower_kw,daily_charge_E):
        self.batcap_kwh = batcap_kwh
        self.rt_effy = rt_effy
        self.chargerpower_kw = chargerpower_kw
        self.daily_charge_E = daily_charge_E

class cons_input_V1G:
    def __init__(self,wta_base,wta_hour,base_pt):
        self.wta_base = wta_base
        self.wta_hour = wta_hour
        self.base_pt = base_pt

class cost_input_V1G:
    def __init__(self,eol_costs_pc,charger_costs_dc,lifetime_y,oam_pi):
        self.eol_costs_pc = eol_costs_pc
        self.charger_costs_dc = charger_costs_dc
        self.lifetime_y = lifetime_y
        self.oam_pi = oam_pi

class tech_input_HVAC:
    def __init__(self,avg_hp,avg_hp_on,cop,mcp):
        self.avg_hp = avg_hp
        self.avg_hp_on = avg_hp_on
        self.cop = cop
        self.mcp = mcp

class cons_input_HVAC:
    def __init__(self,comp,temp_div,max_act):
        self.comp = comp
        self.temp_div = temp_div
        self.max_act = max_act

class cost_input_HVAC:
    def __init__(self,eol_costs_pc,thermstat_costs_dc,lifetime_y,oam_pi):
        self.eol_costs_pc = eol_costs_pc
        self.thermstat_costs_dc = thermstat_costs_dc
        self.lifetime_y = lifetime_y
        self.oam_pi = oam_pi

class tech_input_hpth:
    def __init__(self,avg_hp,avg_hp_on,cop,cp,wall_thicc,delta_T):
        self.avg_hp = avg_hp
        self.avg_hp_on = avg_hp_on
        self.cop = cop
        self.cp = cp
        self.wall_thicc = wall_thicc
        self.delta_T = delta_T

class cons_input_hpth:
    def __init__(self,comp_m2,comp_base,ceil_h):
        self.comp_m2 = comp_m2
        self.comp_base = comp_base
        self.ceil_h = ceil_h

class cost_input_hpth:
    def __init__(self,eol_costs_pm2,thermstat_costs_dc, storage_costs_pm3,lifetime_y,oam_pi):
        self.eol_costs_pm2 = eol_costs_pm2
        self.thermstat_costs_dc = thermstat_costs_dc
        self.storage_costs_pm3 = storage_costs_pm3
        self.lifetime_y = lifetime_y
        self.oam_pi = oam_pi

def compute_pMWh_v2g(application_input,technology_input,consumer_input,costs_input,generic_input,minbool):
        if minbool == True:
            minval = 12
        elif minbool == False:
            minval = 0
        else:
            print("errroooor")

        kw=application_input.mw*1000

        gmc_frac = consumer_input.gmc/100

        req_rpt = 2 * ( application_input.dd + ( ( technology_input.batcap_kwh * ( 1 - gmc_frac ) ) + technology_input.daily_charge_E) / ( math.sqrt( technology_input.rt_effy ) * technology_input.chargerpower_kw ) )

        a_f = (req_rpt - (technology_input.daily_charge_E/(math.sqrt(technology_input.rt_effy)*technology_input.chargerpower_kw)))/24

        no_chargers_p = kw/(technology_input.chargerpower_kw*a_f*math.sqrt(technology_input.rt_effy))
        no_chargers_e = (kw*application_input.dd)/(technology_input.batcap_kwh*(1-gmc_frac)*math.sqrt(technology_input.rt_effy)*a_f)

        no_chargers = max(no_chargers_p,no_chargers_e)
        inv_costs = costs_input.charger_costs_dc*no_chargers
        oam = inv_costs*costs_input.oam_pi
        rebound = (application_input.dd*application_input.nc*kw/technology_input.rt_effy)*(generic_input.elec_price_dmwh/1000)
        partcomp_dcm = max(minval,consumer_input.wta_base + (consumer_input.wta_hour * (req_rpt - consumer_input.base_pt)))
        reward = no_chargers*partcomp_dcm*12
        eol = no_chargers*costs_input.eol_costs_pc
        #eol = no_chargers*technology_input.chargerpower_kw*costs_input.eol_costs_dkw
        eol_costs = eol/((1+generic_input.discount_rate)**(costs_input.lifetime_y+1))
        oam_costs = 0
        reward_costs = 0
        rebound_costs = 0
        power_ann_mw = 0
        energy_ann_mwh = 0
        for i in range(costs_input.lifetime_y):
            oam_costs += oam/((1+generic_input.discount_rate)**(i+1))
            reward_costs += reward/((1+generic_input.discount_rate)**(i+1))
            rebound_costs += rebound/((1+generic_input.discount_rate)**(i+1))
            power_ann_mw += application_input.mw/((1+generic_input.discount_rate)**(i+1))
            energy_ann_mwh += (application_input.mw*application_input.dd*application_input.nc)/((1+generic_input.discount_rate)**(i+1))
        #if power_ann_mw ==0:
        #      print("error")
        total_discounted_costs = inv_costs + oam_costs + rebound_costs + reward_costs + eol_costs
        lcodr_mwh = total_discounted_costs/energy_ann_mwh
        #lcodr_kw = lcodr_mw/1000
        return lcodr_mwh, (no_chargers_p > no_chargers_e), [inv_costs/energy_ann_mwh, oam_costs/energy_ann_mwh, reward_costs/energy_ann_mwh, rebound_costs/energy_ann_mwh, eol_costs/energy_ann_mwh]

def compute_pMWh_v1g(application_input,technology_input,consumer_input,costs_input,generic_input,minbool):
        if minbool == True:
            minval = 5
        elif minbool == False:
            minval = 0
        else:
            print("errroooor")
        kw=application_input.mw*1000
        chargetime = technology_input.daily_charge_E / (technology_input.chargerpower_kw*math.sqrt(technology_input.rt_effy))
        a_f = chargetime / 24
        no_chargers_p = kw/(technology_input.chargerpower_kw*a_f)
        inv_costs = costs_input.charger_costs_dc*no_chargers_p
        oam = inv_costs*costs_input.oam_pi
        rebound = (application_input.dd*application_input.nc*kw)*(generic_input.elec_price_dmwh/1000)
        rpt = application_input.dd + chargetime
        partcomp_dcm = max(minval,(consumer_input.wta_base + (consumer_input.wta_hour * (rpt - consumer_input.base_pt))))
        reward = no_chargers_p*partcomp_dcm*12
        eol = no_chargers_p*costs_input.eol_costs_pc
        #eol = no_chargers*technology_input.chargerpower_kw*costs_input.eol_costs_dkw
        eol_costs = eol/((1+generic_input.discount_rate)**(costs_input.lifetime_y+1))
        oam_costs = 0
        reward_costs = 0
        rebound_costs = 0
        power_ann_mw = 0
        energy_ann_mwh = 0
        for i in range(costs_input.lifetime_y):
            oam_costs += oam/((1+generic_input.discount_rate)**(i+1))
            reward_costs += reward/((1+generic_input.discount_rate)**(i+1))
            rebound_costs += rebound/((1+generic_input.discount_rate)**(i+1))
            power_ann_mw += application_input.mw/((1+generic_input.discount_rate)**(i+1))
            energy_ann_mwh += (application_input.mw*application_input.dd*application_input.nc)/((1+generic_input.discount_rate)**(i+1))
        #if power_ann_mw ==0:
        #      print("error")
        total_discounted_costs = inv_costs + oam_costs + rebound_costs + reward_costs + eol_costs
        lcodr_mwh = total_discounted_costs/energy_ann_mwh
        #lcodr_kw = lcodr_mw/1000
        return lcodr_mwh, [inv_costs/energy_ann_mwh, oam_costs/energy_ann_mwh, reward_costs/energy_ann_mwh, rebound_costs/energy_ann_mwh, eol_costs/energy_ann_mwh]

def compute_pMWh_hvac2(application_input,technology_input,consumer_input,costs_input,generic_input):
        kw=application_input.mw*1000
        
        # = (application_input.dd / 2) * (technology_input.cop / (technology_input.mcp * consumer_input.temp_div)) * 3600
        
        max_power_diff = 2*((technology_input.mcp * consumer_input.temp_div)/(application_input.dd * technology_input.cop * 3600))
        #ddmax = 2*((technology_input.mcp * consumer_input.temp_div)/(technology_input.avg_hp_on * technology_input.cop * 3600))
        power_diff = min(max_power_diff,technology_input.avg_hp_on)
        no_chargers_p = kw/power_diff
        mult_factor_act = max((application_input.nc/(consumer_input.max_act/12)),1)
        no_chargers = no_chargers_p*mult_factor_act
        inv_costs = costs_input.thermstat_costs_dc*no_chargers
        oam = inv_costs*costs_input.oam_pi
        rebound = (application_input.dd*application_input.nc*kw)*(generic_input.elec_price_dmwh/1000)
        reward = no_chargers*consumer_input.comp*12
        eol = no_chargers_p*costs_input.eol_costs_pc
        #eol = no_chargers*technology_input.chargerpower_kw*costs_input.eol_costs_dkw
        eol_costs = eol/((1+generic_input.discount_rate)**(costs_input.lifetime_y+1))
        oam_costs = 0
        reward_costs = 0
        rebound_costs = 0
        power_ann_mw = 0
        energy_ann_mwh = 0
        for i in range(costs_input.lifetime_y):
            oam_costs += oam/((1+generic_input.discount_rate)**(i+1))
            reward_costs += reward/((1+generic_input.discount_rate)**(i+1))
            rebound_costs += rebound/((1+generic_input.discount_rate)**(i+1))
            power_ann_mw += application_input.mw/((1+generic_input.discount_rate)**(i+1))
            energy_ann_mwh += (application_input.mw*application_input.dd*application_input.nc)/((1+generic_input.discount_rate)**(i+1))
        #if power_ann_mw ==0:
        #      print("error")
        total_discounted_costs = inv_costs + oam_costs + rebound_costs + reward_costs + eol_costs
        lcodr_mwh = total_discounted_costs/energy_ann_mwh
        #lcodr_kw = lcodr_mw/1000
        return lcodr_mwh, [inv_costs/energy_ann_mwh, oam_costs/energy_ann_mwh, reward_costs/energy_ann_mwh, rebound_costs/energy_ann_mwh, eol_costs/energy_ann_mwh]

def compute_pMWh_hpth(application_input,technology_input,consumer_input,costs_input,generic_input):
        kw=application_input.mw*1000
        n_part = kw / technology_input.avg_hp_on
        m_water = (application_input.dd*technology_input.avg_hp_on)/(technology_input.cp*technology_input.delta_T)

        m_water_part = m_water/n_part
        #print(m_water/(997*math.pi*(consumer_input.ceil_h - 2*technology_input.wall_thicc)))
        #print(consumer_input.ceil_h, technology_input.wall_thicc)
        undersqrt = m_water_part/(997*math.pi*(consumer_input.ceil_h - 2*technology_input.wall_thicc))
        if undersqrt < 0:
              print("negative under squareroot" + str(application_input.dd))
        area = (2*(math.sqrt(undersqrt)+technology_input.wall_thicc))**2
        surf_area = ( 2* math.pi*(math.sqrt(area)/2 - technology_input.wall_thicc) ) * (consumer_input.ceil_h - 2*technology_input.wall_thicc) + 2*(math.pi*(math.sqrt(area)/2 - technology_input.wall_thicc)**2)
        inv_costs = costs_input.storage_costs_pm3*(m_water/997) + costs_input.thermstat_costs_dc*n_part
        oam = inv_costs*costs_input.oam_pi
        rebound = (application_input.dd*application_input.nc*kw)*(generic_input.elec_price_dmwh/1000)
        reward_p_cons = max(0, (area - 1.5) * consumer_input.comp_m2 + consumer_input.comp_base)
        reward = reward_p_cons*12*n_part
        eol = surf_area*costs_input.eol_costs_pm2
        #eol = no_chargers*technology_input.chargerpower_kw*costs_input.eol_costs_dkw
        eol_costs = eol/((1+generic_input.discount_rate)**(costs_input.lifetime_y+1))
        oam_costs = 0
        reward_costs = 0
        rebound_costs = 0
        power_ann_mw = 0
        energy_ann_mwh = 0
        for i in range(costs_input.lifetime_y):
            oam_costs += oam/((1+generic_input.discount_rate)**(i+1))
            reward_costs += reward/((1+generic_input.discount_rate)**(i+1))
            rebound_costs += rebound/((1+generic_input.discount_rate)**(i+1))
            power_ann_mw += application_input.mw/((1+generic_input.discount_rate)**(i+1))
            energy_ann_mwh += (application_input.mw*application_input.dd*application_input.nc)/((1+generic_input.discount_rate)**(i+1))
        #if power_ann_mw ==0:
        #      print("error")
        #print("capital: " + str(inv_costs))
        #print("oam: " + str(oam_costs))
        #print("rebound: " + str(rebound_costs))
        #print("reward: " + str(reward_costs))
        #print("eol: " + str(eol_costs))
        total_discounted_costs = inv_costs + oam_costs + rebound_costs + reward_costs + eol_costs
        lcodr_mwh = total_discounted_costs/energy_ann_mwh
        #lcodr_kw = lcodr_mw/1000
        return lcodr_mwh, [inv_costs/energy_ann_mwh, oam_costs/energy_ann_mwh, reward_costs/energy_ann_mwh, rebound_costs/energy_ann_mwh, eol_costs/energy_ann_mwh]

vf_obj = value_f([0.98,0.986],1.12,1.05,1.05,0.1)

lcos_list_mwh = [220,185,400]
lcos_tech_list_mwh = ["Pumped Hydro","Flywheel","Lithium-ion"]
lcos_cost_comp_mwh = [[0.657692,0.053846,0,0.288462,0],[0.605607,0.082243,0,0.31215,0],[0.592334,0.116725,0,0.290941,0]]

#adjust for inflation
infl = 1.22

for i in lcos_cost_comp_mwh:
    for idx,j in enumerate(i):
        if idx != 3:
            j = j * infl


#make figure
def compute_figure(v2g_wta_5,v2g_wta_15,
                   #v2g_freq_5,v2g_freq_15,
                   sc_wta_5,sc_wta_15,
                   #sc_freq_5,sc_freq_15,
                   hp_wta,hpts_wta_1,hpts_wta_2,no,min):
    numberstring = str(no)
    v2g_wta_10 = v2g_wta_5
    v2g_wta_ph = (v2g_wta_15 - v2g_wta_5) / 5
    #v2g_freq_10 = (v2g_freq_15 + v2g_freq_5) / 2
    #v2g_freq_ph = (v2g_freq_15 - v2g_freq_5) / 10

    sc_wta_10 = sc_wta_5
    sc_wta_ph = (sc_wta_15 - sc_wta_5) / 5
    #sc_freg_10 = (sc_freq_15 + sc_freq_5) / 2
    #sc_freq_ph = (sc_freq_15 - sc_freq_5) / 10

    hpts_wta_1_5 = (hpts_wta_1 + hpts_wta_2) / 2
    hpts_wta_pm2 = (hpts_wta_2 - hpts_wta_1)

    gen_inp = generic_inputs(50,0.08)

    #v2g
    v2g_tech = tech_input_V2G(60,0.86,7.4,5.56)
    v2g_cons = cons_input_V2G(33,v2g_wta_10,v2g_wta_ph,10)
    v2g_costs = cost_input_V2G(50,3000,15,0.05)
    

    v2g_res_list = []
    for i in appl_list:
        v2g_res = compute_pMWh_v2g(i,v2g_tech,v2g_cons,v2g_costs,gen_inp,min)
        if v2g_res[1]:
            e_or_p = 1
        else:
            e_or_p = 0
        v2g_res_list.append([v2g_res[2][j]/vf_obj.v2g[e_or_p] for j in range(5)])

    #v1g
    v1g_tech = tech_input_V1G(60,0.86,7.4,5.56)
    v1g_cons = cons_input_V1G(sc_wta_10,sc_wta_ph,10)
    v1g_costs = cost_input_V1G(0,107,15,0.05)
    v1g_res_list = []
    for i in appl_list:
        v1g_res_list.append([compute_pMWh_v1g(i,v1g_tech,v1g_cons,v1g_costs,gen_inp,min)[1][j]/vf_obj.v1g for j in range(5)])


    #hpts
    hpth_tech = tech_input_hpth(0.4596,1.68,2.71,4.18,0.05,35)
    hpth_cons = cons_input_hpth(hpts_wta_pm2,hpts_wta_1_5,2.3)
    hpth_costs = cost_input_hpth(1,85,2042,15,0.05)
    hpts_res_list = []
    for i in appl_list:
        hpts_res_list.append([compute_pMWh_hpth(i,hpth_tech,hpth_cons,hpth_costs,gen_inp)[1][j]/(vf_obj.hpth) for j in range(5)])
   
    # Data for the sales
    applications = ['Energy Arbitrage', 'Primary Response', 'Congestion Management']
    labels = ['V2G', 'Smart Charging', 'HP + Thermal Storage']#,'LCOS (2025)'] #['Energy Arbitrage', 'Primary Response', 'Congestion Management']
    labels_text = ['V2G', 'Smart\nCharging', 'Heat Pump +\nThermal Storage']
    stor_tech = ['Pumped\nHydro', 'Flywheel', 'Li-ion']
    #stores = ['North', 'East', 'West']

    cost_types = ['Investment', 'O&M', 'Rewards', 'Rebound', 'EOL']

    # Sales data (example values)
    sales_data = {
        'Energy Arbitrage': {
            'V2G': v2g_res_list[0],
            'Smart Charging': v1g_res_list[0],
            #'Smart Heat Pump': mc_results_comp[0][2],
            'HP + Thermal Storage': hpts_res_list[0],
            'Pumped\nHydro' : [lcos_list_mwh[0]*lcos_cost_comp_mwh[0][i] for i in range(5)]
        },
        'Primary Response': {
            'V2G': v2g_res_list[1],
            'Smart Charging': v1g_res_list[1],
            #'Smart Heat Pump': mc_results_comp[1][2],
            'HP + Thermal Storage': hpts_res_list[1],
            'Flywheel' : [lcos_list_mwh[1]*lcos_cost_comp_mwh[1][i] for i in range(5)]
        },
        'Congestion Management': {
            'V2G': v2g_res_list[2],
            'Smart Charging': v1g_res_list[2],
            #'Smart Heat Pump': mc_results_comp[2][2],
            'HP + Thermal Storage': hpts_res_list[2],
            'Li-ion' : [lcos_list_mwh[2]*lcos_cost_comp_mwh[2][i] for i in range(5)]
        }
    }

    # Colors for the fruits
    colors = ['blue', 'orange', 'gray','yellow','green']

    # Plotting the data
    fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=False)

    y_limits = [max([sum(v2g_res_list[i]),sum(v1g_res_list[i]),sum(hpts_res_list[i]),lcos_list_mwh[i]])*1.1 for i in range(3)]

    labels_text2 = ["V2G", "Smart\nCharging", "HP + Heat\nStorage"]

    #error_list = []
    #for i in range(len(applications)):
    #    y_max = [(max(mc_results[i].lcodr_dist[i2]) - sum(mc_results[i].lcodr_dist[i2])/len(mc_results[i].lcodr_dist[i2]))/(max(mc_results[i].lcodr_dist[i2]) - min(mc_results[i].lcodr_dist[i2]))*np.std(mc_results[i].lcodr_dist[i2])/3 for i2 in range(4)]
    #    ymaxfin = y_max[:2] + [y_max[3]*5] + [((lcos_range_list_mwh[i][1] - lcos_list_mwh[i])/3)]
    #    lcos_range_list_mwh = [[140,340],[50,270],[230,710]]
    #    y_min = [(sum(mc_results[i].lcodr_dist[i2])/len(mc_results[i].lcodr_dist[i2]) - min(mc_results[i].lcodr_dist[i2]))/(max(mc_results[i].lcodr_dist[i2]) - min(mc_results[i].lcodr_dist[i2]))*np.std(mc_results[i].lcodr_dist[i2])/3 for i2 in range(4)]
    #    yminfin = y_min[:2] + [y_min[3]*5] + [((lcos_list_mwh[i] - lcos_range_list_mwh[i][0])/3)]
    #    error_list.append([yminfin,ymaxfin])

    for idx, year in enumerate(applications):
        ax = axs[idx]
        bottom = np.zeros(4)

        for i, fruit in enumerate(cost_types):
            #labelsplus = 
            values = [sales_data[year][store][i] for store in labels + [stor_tech[idx]]]
            ax.bar(labels_text2 + [stor_tech[idx]], values, label=fruit, bottom=bottom)#, color=colors[i])
            bottom += values
        #ax.errorbar(labels_text2 + [stor_tech[idx]],[sum(mc_results_comp[idx][i2]) for i2 in [0,1,3]] + [lcos_list_mwh[idx]],yerr=error_list[idx],fmt='none',capsize=5)
        ax.set_title(applications[idx], size=16)
        ax.set_ylim(0, y_limits[idx])
        #if idx == 0:
        ax.yaxis.label.set_size(13)
        if idx == 0:
            ax.set_ylabel(r'Levelised cost in $\$_{2025}$/MWh')
        ax.xaxis.set_tick_params(labelsize=12)
        ax.yaxis.set_tick_params(labelsize=13)
        ax.set_xticks(labels_text2 + [stor_tech[idx]])
        ax.legend(prop={'size': 13})
    plt.savefig("C:/Users/simon/local python/" + numberstring + ".png", format="png", bbox_inches="tight")    
    return fig, ax

# Define the compute_results function
#def compute_results(a, b, c):
    # Example computation (replace with actual logic)
#    x = a + b + c
#    y = a * b * c
#    z = (a + b) / c if c != 0 else 0
#    return x, y, z

def send_email(email, results):
    sender_email = "jacobthraen@gmail.com"
    sender_password = "qeto fysv dhka aafr"
    recipient_email = email

    subject = "Your Computation Results"
    body = f"Here are your results:\nX: {results[0]}\nY: {results[1]}\nZ: {results[2]}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        st.success("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        st.error("Failed to login to the SMTP server. Check your email and password.")
    except smtplib.SMTPConnectError:
        st.error("Failed to connect to the SMTP server. Check the server address and port.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Streamlit app
st.title("Compute Results Application")

# Input fields for a, b, and c

st.subheader("Smart Charging")

col1, col2 = st.columns(2)
with col1:
    sc_mon5 = st.slider("Monthly remuneration for required average plug-in of 5h/day :", min_value=0, max_value=300, value=20, key="sc_mon5")
    sc_mon15 = st.slider("Monthly remuneration for required average plug-in of 15h/day :", min_value=0, max_value=300, value=20, key="sc_mon15")
with col2:
    sc_freq5 = st.slider("How often do you think you would plug-in / week with this contract", min_value=1.0, max_value=14.0, value=7.0, key="sc_freq5")
    sc_freq15 = st.slider("How often do you think you would plug-in / week with this contract", min_value=1.0, max_value=14.0, value=7.0, key="sc_freq15")

st.subheader("Vehicle-to-Grid")

col3, col4 = st.columns(2)
with col3:
    v2g_mon5 = st.slider("Monthly remuneration for required average plug-in of 5h/day :", min_value=0, max_value=300, value=20, key="v2g_mon5")
    v2g_mon15 = st.slider("Monthly remuneration for required average plug-in of 15h/day :", min_value=0, max_value=300, value=20, key="v2g_mon15")
with col4:
    v2g_freq5 = st.slider("How often do you think you would plug-in / week with this contract", min_value=1.0, max_value=14.0, value=7.0, key="v2g_freq5")
    v2g_freq15 = st.slider("How often do you think you would plug-in / week with this contract", min_value=1.0, max_value=14.0, value=7.0, key="v2g_freq15")

st.subheader("Smart Heat Pumps")

a = st.slider("Monthly remuneration for maximum temperature divergence of 1:", min_value=0, max_value=300, value=20, key="a")

#col3, col4 = st.columns(2)
#with col3:
#    v2g_mon5 = st.slider("Monthly remuneration for maximum temperature divergence of 1:", min_value=0, max_value=300, value=20, key="a")
#[[]]    v2g_mon15 = st.slider("Monthly remuneration for required average plug-in of 15h/day :", min_value=0, max_value=300, value=20, key="c")

st.subheader("Heat Pump with Thermal Storage")

hpts1m2 = st.slider("Monthly remuneration for hosting a thermal storage tank that occupies an area of 1m2", min_value=0, max_value=300, value=20, key="hpts1m2")
hpts2m2 = st.slider("Monthly remuneration for hosting a thermal storage tank that occupies an area of 2m2", min_value=0, max_value=300, value=20, key="hpts2m2")



# Compute results
if st.button("Compute"):
    #x, y, z = compute_results(a, a, a)
    #st.write(f"Results: X = {x}, Y = {y}, Z = {z}")

    # Plot the results
    #fig, ax = plt.subplots()
    #ax.bar(["X", "Y", "Z"], [x, y, z])
    #ax.set_ylabel("Values")
    #ax.set_title("Results Bar Graph")
    fig, ax = compute_figure(v2g_mon5,v2g_mon15,
                   #v2g_freq_5,v2g_freq_15,
                   sc_mon5,sc_mon15,
                   #sc_freq_5,sc_freq_15,
                   1000,hpts1m2,hpts2m2)

    st.pyplot(fig)

    # Email input
    email = st.text_input("Enter your email to receive the results:")
    if st.button("Send Email"):
        #if email:
            send_email(email, (10,20,30))
        #else:
        #    st.error("Please enter your email address.")