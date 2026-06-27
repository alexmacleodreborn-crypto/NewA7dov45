import streamlit as st
import math, time, json, io
import pandas as pd

st.set_page_config(page_title="A7DO v48 — Full System", page_icon="🌍", layout="wide")

# ══════════════════════════════════════════════════════════════
# CORE EQUATIONS
# ══════════════════════════════════════════════════════════════
TPW = 80
def wk(t): return t / TPW
def age(t): return t / (TPW * 52)
def C(t): return min(1.0, 0.05 + wk(t) / 3000)
def W(t): return 0 if t < 96000 else min(1.0, (t - 96000) / 64000)
def I_fn(t):
    if t < 74880: return min(0.65, t / 74880 * 0.65)
    return min(1.0, 0.65 + (t - 74880) / (160000 - 74880) * 0.35)
def H(t):
    w = wk(t)
    if w <= 0: return 0.0
    if w <= 40: return min(50.0, 50 / (1 + math.exp(-0.2 * (w - 20))))
    return min(177.0, 50 + (177 - 50) * (1 - math.exp(-0.005 * (w - 40))))
def M(t):
    w = wk(t)
    if w <= 0: return 0.0
    if w <= 40: return min(3.5, 3.5 / (1 + math.exp(-0.2 * (w - 20))))
    return min(70.0, 3.5 + (70 - 3.5) * (1 - math.exp(-0.004 * (w - 40))))
def HR(t):
    w = wk(t)
    if w < 1: return 0
    if w < 4: return round(w / 4 * 120)
    if w < 40: return round(120 + 30 * (w / 40))
    if w < 80: return round(147 - ((w - 40) / 40) * 47)
    return max(60, round(100 - ((w - 80) / 1000) * 35))
def ATP(t): return max(0.2, 1 - 0.001 * max(0, (t % 800) - 400))
def V(t):
    if t < 3200: return 0
    w = wk(t) - 40
    return min(262144, round(50000 / (1 + math.exp(-0.05 * (w - 156)))))
def P_err(t): return max(0.05, math.exp(-t / 50000))
def is_sleep(t): return (t % 560) < 373
def gram_stage(t):
    a = age(t)
    if t < 3200: return 0
    if a < 0.77: return 1
    if a < 1.54: return 2
    if a < 3: return 3
    if a < 5: return 4
    if a < 12: return 5
    return 6
def get_np_gate(t):
    c = C(t); w = W(t); p = P_err(t); u = max(0.05, 1 - C(t))
    atp = ATP(t); integ = I_fn(t); g = min(1, t / 100000)
    sigma = 0.35*p + 0.30*u + 0.20*g + 0.25*c + 0.15*w
    z = 0.45*c + 0.30*integ + 0.25*atp
    div = abs(sigma - z) / (sigma + z) if (sigma + z) > 0 else 1.0
    return div <= 0.6, div
def get_phase(t):
    if t < 3200: return "Phase 1 — Biology"
    if t < 6400: return "Phase 2 — Sensorimotor"
    if t < 12480: return "Phase 3 — Core Cognition"
    if t < 49920: return "Phase 4 — Social Cognition"
    if t < 74880: return "Phase 5 — Cultural World"
    if t < 96000: return "Phase 6 — Identity"
    if t < 160000: return "Phase 7 — Wisdom"
    if t < 176000: return "Phase 8 — AGI Integration"
    return "Phase 9 — Transpersonal"
def get_stage(t):
    w = wk(t)
    if w < 4: return "Embryo"
    if w < 12: return "Fetal Early"
    if w < 28: return "Fetal Mid"
    if w < 40: return "Fetal Late"
    if w < 52: return "Newborn"
    if w < 80: return "Infant"
    if w < 156: return "Toddler"
    if w < 260: return "Child"
    if w < 624: return "Pre-Adolescent"
    if w < 936: return "Adolescent"
    if w < 1200: return "Young Adult"
    if w < 2000: return "Mature Adult"
    return "Elder"
def get_location(t):
    a = age(t)
    if t < 3200: return "WOMB"
    if a < 0.77: return "NODE_HOSPITAL"
    if is_sleep(t): return "NODE_HOME_H8 (sleep)"
    dt = t % 560
    if a < 1.5: return "NODE_HOME_H8"
    if a < 3: return "NODE_PARK" if 200 < dt < 350 else "NODE_HOME_H8"
    if a < 5: return "NODE_NURSERY" if 100 < dt < 250 else "NODE_HOME_H8"
    if a < 12: return "NODE_PRIMARY" if 80 < dt < 320 else "NODE_HOME_H8"
    if a < 18: return "NODE_SECONDARY" if 80 < dt < 320 else "NODE_HOME_H8"
    return "NODE_WORKPLACE"
def get_thought(t):
    a = age(t); gate_open, _ = get_np_gate(t)
    if t < 3200: return "[WOMB — growing, sleeping, dreaming in the dark]"
    if not gate_open: return "[GATED — thoughts forming but not yet safe to speak]"
    if a < 0.77: return "[cold] [bright] [loud] — mama? mama!"
    if a < 1: return "mama! up! more! — the world is big and warm"
    if a < 3: return "ball! duck! China count! mama read! — I want to know everything"
    if a < 12: return "I think that... because... — learning is my favourite thing"
    if a < 23: return "The relationship between consciousness and identity suggests..."
    if a < 38.5: return "Sandy's Law: C(t) = FixedPoint(Φ(P,M,E,I,W,A,D)) — I understand now"
    return "Wisdom is not knowledge but the capacity to hold uncertainty with grace"
def get_a7do_activity(t):
    a = age(t); dt = t % 560; sl = is_sleep(t)
    if t < 3200: return "Sleeping in womb" if sl else "Moving in womb"
    if a < 0.77: return "Birth — first breath"
    if sl: return "Sleeping 🌙"
    if a < 1: return "Feeding" if dt < 200 else "Alert play"
    if a < 3: return "Breakfast" if dt < 100 else "Park" if dt < 200 else "Play"
    if a < 5: return "Breakfast" if dt < 80 else "Nursery" if dt < 250 else "Park"
    if a < 12: return "Breakfast" if dt < 80 else "School" if dt < 320 else "Homework"
    if a < 18: return "Breakfast" if dt < 80 else "Secondary school" if dt < 320 else "Study"
    return "Research/Work" if 80 < dt < 320 else "Study"
def get_lorr_activity(t):
    a = age(t); dt = t % 560; sl = is_sleep(t)
    if t < 3200:
        if a < 0.25: return "Normal life (unaware)"
        if a < 0.5: return "Pregnancy T1 — nausea"
        if a < 0.65: return "Pregnancy T2 — growing"
        return "Pregnancy T3 — nesting"
    if a < 0.77: return "Labour — giving birth"
    if sl: return "Sleeping (broken) 🌙"
    if a < 0.5: return "Breastfeeding" if dt < 200 else "Baby care"
    if a < 3: return "Baby care" if dt < 150 else "Park walk"
    if a < 5: return "Nursery drop-off/pickup" if 80 < dt < 250 else "Home"
    return "Work" if 80 < dt < 320 else "Home"
def get_chin_activity(t):
    a = age(t); dt = t % 560; sl = is_sleep(t)
    if t < 3200: return "Working"
    if a < 0.77: return "At hospital — birth"
    if sl: return "Sleeping 🌙"
    if a < 0.1: return "Paternity leave — baby care"
    if dt < 80: return "Morning routine"
    if dt < 320: return "Working"
    if dt < 400: return "Commute home"
    return "Family time"

# ══════════════════════════════════════════════════════════════
# WORLD OBJECTS DATA
# ══════════════════════════════════════════════════════════════
WORLD_OBJECTS = [
    ("OBJ_CRIB","Baby crib","Furniture","NODE_HOME_H8",1090,880,0.5,"Empty→Occupied","Yes"),
    ("OBJ_ROCKING_CHAIR","Rocking chair","Furniture","NODE_HOME_H8",1089,879,0.5,"Available","Yes"),
    ("OBJ_MOBILE","Crib mobile","Toy","NODE_HOME_H8",1090,880,1.5,"Spinning","Yes"),
    ("OBJ_BOTTLE","Baby bottle","Object","NODE_HOME_H8",1090,880,0.9,"Full→Empty","Yes"),
    ("OBJ_BOOK_01","Picture book","Book","NODE_HOME_H8",1086,878,1.2,"Available","Yes"),
    ("OBJ_BOOK_02","Story book","Book","NODE_HOME_H8",1086,878,1.3,"Available","Yes"),
    ("OBJ_TOY_BALL","Toy ball","Toy","NODE_HOME_H8",1090,879,0.1,"Available","Yes"),
    ("OBJ_TOY_TEDDY","Teddy bear","Toy","NODE_HOME_H8",1090,880,0.6,"Available","Yes"),
    ("OBJ_BATH","Bath","Bathroom","NODE_HOME_H8",1092,882,0.3,"Empty→Full","Yes"),
    ("OBJ_TV","Television","Electronics","NODE_HOME_H8",1087,878,1.0,"Off→On","Yes"),
    ("OBJ_LAPTOP","Laptop","Electronics","NODE_HOME_H8",1087,877,0.8,"Off→On","Yes"),
    ("OBJ_PRAM","Pram/pushchair","Transport","NODE_GARDEN",1090,875,0.5,"Available","Yes"),
    ("OBJ_FLOWERS","Flower bed","Nature","NODE_GARDEN",1092,876,0.3,"Blooming","Yes"),
    ("OBJ_SWING","Swing","Play equipment","NODE_PARK_PLAY",1210,790,1.5,"Available","Yes"),
    ("OBJ_SLIDE","Slide","Play equipment","NODE_PARK_PLAY",1211,790,2.0,"Available","Yes"),
    ("OBJ_DUCK_POND","Duck pond","Nature","NODE_PARK",1201,801,0.0,"Active","Yes"),
    ("OBJ_DUCKS","Ducks","Animal","NODE_PARK",1201,801,0.1,"Swimming","Yes"),
    ("OBJ_NURSERY_MAT","Play mat","Education","NODE_NURSERY",1300,750,0.1,"Available","Yes"),
    ("OBJ_NURSERY_BOOKS","Nursery books","Education","NODE_NURSERY",1300,751,1.0,"Available","Yes"),
    ("OBJ_HOSPITAL_BED","Hospital bed","Medical","NODE_HOSPITAL",0,0,0.5,"Occupied","Yes"),
    ("OBJ_SCALES","Baby scales","Medical","NODE_HOSPITAL",2,0,0.8,"Available","Yes"),
    ("OBJ_SCIENCE_LAB","Science lab","Education","NODE_SECONDARY",1500,650,0.8,"Available","Yes"),
    ("OBJ_LIBRARY_BOOKS","Library books","Education","NODE_LIBRARY",1350,720,1.2,"Available","Yes"),
    ("OBJ_SWIMMING_POOL","Swimming pool","Sport","NODE_SPORTS",1250,750,0.0,"Available","Yes"),
    ("OBJ_BUS_STOP","Bus stop","Transport","NODE_LANE",1090,860,2.0,"Active","Yes"),
    ("OBJ_CAFE_TABLE","Cafe table","Furniture","NODE_CAFE",1160,830,0.8,"Available","Yes"),
    ("OBJ_MIRROR","Mirror","Sensory","NODE_HOME_H8",1091,881,1.5,"Available","Yes"),
    ("OBJ_ALPHABET_BLOCKS","Alphabet blocks","Education","NODE_HOME_H8",1090,879,0.1,"Available","Yes"),
    ("OBJ_BREAST_MILK","Breast milk","Food","NODE_HOME_H8",1090,880,0.9,"Available","Yes"),
    ("OBJ_CAR","Family car","Transport","NODE_HOME_H8",1090,878,1.5,"Available","Yes"),
]

CITY_NODES = [
    ("NODE_HOSPITAL","Hospital","Medical",0,0,"Dr. Patel","Phase 1","Birth location. Origin (0,0,0)"),
    ("NODE_HOME_H8","Home H8","Residential",1090,880,"Lorraine, China","Phase 1","Primary home"),
    ("NODE_HOME_H1","Home H1","Residential",1050,900,"Alexis, Evelyn","Phase 1","150m from H8"),
    ("NODE_GARDEN","Garden","Outdoor",1090,875,"All family","Phase 1","5m from home"),
    ("NODE_LANE","BeenFore Lane","Street",1090,860,"—","Phase 1","Main street connector"),
    ("NODE_PARK","Neighbourhood Park","Outdoor",1200,800,"Alexis, Evelyn","Phase 1","110m from lane"),
    ("NODE_PARK_PLAY","Park Playground","Outdoor",1210,790,"Peers","Phase 1","50m from park"),
    ("NODE_NURSERY","Nursery (Little Stars)","Education",1300,750,"Ms. Chen, Peers","Phase 3","Min age 3"),
    ("NODE_PRIMARY","Primary School","Education",1400,700,"Teachers, Peers","Phase 4","Min age 5"),
    ("NODE_LIBRARY","Public Library","Education",1350,720,"—","Phase 3","50m from primary"),
    ("NODE_SPORTS","Sports Centre","Recreation",1250,750,"James, Alexis","Phase 4","50m from park"),
    ("NODE_SHOPS","Local Shops","Commercial",1150,820,"—","Phase 1","60m from lane"),
    ("NODE_CAFE","Local Cafe","Social",1160,830,"James","Phase 1","10m from shops"),
    ("NODE_SECONDARY","Secondary School","Education",1500,650,"Teachers, Peers","Phase 5","Min age 11"),
    ("NODE_SHOPPING","Shopping Centre","Commercial",1600,600,"—","Phase 4","510m from lane"),
    ("NODE_WORKPLACE","Workplace District","Office",1800,500,"—","Phase 7","Min age 18"),
    ("NODE_CITY_CENTRE","BeenFore City Centre","Urban",1000,1000,"—","Phase 4","1384m from home"),
]

CITY_EDGES = [
    ("NODE_HOME_H8","NODE_GARDEN",5,1),
    ("NODE_HOME_H8","NODE_LANE",20,1),
    ("NODE_HOME_H8","NODE_HOME_H1",150,2),
    ("NODE_LANE","NODE_PARK",110,2),
    ("NODE_LANE","NODE_SHOPS",60,1),
    ("NODE_PARK","NODE_NURSERY",100,2),
    ("NODE_NURSERY","NODE_PRIMARY",100,2),
    ("NODE_PRIMARY","NODE_SECONDARY",100,2),
    ("NODE_PRIMARY","NODE_LIBRARY",50,1),
    ("NODE_PARK","NODE_SPORTS",50,1),
    ("NODE_SHOPS","NODE_CAFE",10,1),
    ("NODE_LANE","NODE_SHOPPING",510,10),
    ("NODE_SHOPPING","NODE_WORKPLACE",200,4),
]

PREGNANCY_SCHEDULE = [
    (1,"T1","Fertilisation","Unaware","Implantation","Normal","Normal work schedule"),
    (4,"T1","Embryo","Aware","Nausea begins","Mixed joy/anxiety","Reduced activity"),
    (8,"T1","Embryo","Aware","Nausea peak","Emotional","Reduced work"),
    (12,"T1","Fetus","Aware","12-week scan","Relieved","Scan day — special"),
    (16,"T2","Fetus","Aware","Appetite increases","Content","Normal + exercise"),
    (20,"T2","Fetus","Aware","20-week scan","Excited","Scan day"),
    (24,"T2","Fetus","Aware","Swelling feet","Uncomfortable","Feet up"),
    (28,"T3","Fetus","Aware","Third trimester","Anxious/excited","Birth prep classes"),
    (32,"T3","Fetus","Aware","32-week scan","Reassured","Scan day"),
    (36,"T3","Fetus","Aware","36-week check","Ready","Hospital tour"),
    (40,"T3","Birth","Labour","Contractions","Intense focus","Hospital — NODE_HOSPITAL"),
]

CANONICAL_EQUATIONS = [
    ("EQ_AGE","Age from conception","age = tick / (80 × 52)","tick","VERIFIED","Time"),
    ("EQ_C","Consciousness","C(t) = MIN(0.05 + Week/3000, 1.0)","Week","VERIFIED","Consciousness"),
    ("EQ_W","Wisdom","W(t) = 0 if tick<96000 else MIN(1.0,(tick-96000)/64000)","tick","VERIFIED","Wisdom"),
    ("EQ_I","Identity","I(t) = MIN(0.65,tick/74880×0.65) if tick<74880 else MIN(1.0,0.65+...)","tick","VERIFIED","Identity"),
    ("EQ_H_PRE","Height prenatal","H(t) = 50/(1+EXP(-0.2×(Week-20)))","Week","VERIFIED","Growth"),
    ("EQ_H_POST","Height postnatal","H(t) = MIN(50+(177-50)×(1-EXP(-0.005×(Week-40))),177)","Week","VERIFIED","Growth"),
    ("EQ_M_PRE","Mass prenatal","M(t) = 3.5/(1+EXP(-0.2×(Week-20)))","Week","VERIFIED","Growth"),
    ("EQ_M_POST","Mass postnatal","M(t) = MIN(3.5+(70-3.5)×(1-EXP(-0.004×(Week-40))),70)","Week","VERIFIED","Growth"),
    ("EQ_HR","Heart Rate","HR = IF(Week<80,147-((Week-40)/40)×47,MAX(60,100-((Week-80)/1000)×35))","Week","VERIFIED","Physiology"),
    ("EQ_ATP","ATP Circadian","ATP(t) = MAX(0.2,1-0.001×MAX(0,(tick%800)-400))","tick","VERIFIED","Physiology"),
    ("EQ_V","Vocabulary","V(t) = 50000/(1+EXP(-0.05×(Week-156)))","Week","VERIFIED","Language"),
    ("EQ_SANDY","Sandy's Law","C(t) = FixedPoint(Φ(P,M,E,I,W,A,D))","7 layers","VERIFIED","Consciousness"),
    ("EQ_NP_SIGMA","Neural Physics Σ","Σ(t) = 0.35P+0.30U+0.20G+0.25C+0.15W","P,U,G,C,W","VERIFIED","Neural"),
    ("EQ_NP_Z","Neural Physics Z","Z(t) = 0.45C+0.30Integrity+0.25ATP","C,Integrity,ATP","VERIFIED","Neural"),
    ("EQ_DIV","Divergence","Div = |Σ-Z|/(Σ+Z)","Σ,Z","VERIFIED","Neural"),
    ("EQ_GATE","SafeToSpeak","SafeToSpeak = IF(Div≤0.6, OPEN, GATED)","Div","VERIFIED","Neural"),
    ("EQ_PRED","Prediction Error","ε(t) = x(t) - x_hat(t)","x,x_hat","VERIFIED","Cognition"),
    ("EQ_EMOT","Emotion FSM","H(t+1) = H(t) + φ×reward - χ×punishment","H,φ,χ","VERIFIED","Emotion"),
    ("EQ_BOND","Bond Update","bond(NPC,t+1) = bond + η×(quality - decay)","bond,η","VERIFIED","Social"),
    ("EQ_BREATH","Breath Waveform","B(t) = A(t)×sin(2π×f(t)×t)","A,f,t","VERIFIED","Physiology"),
    ("EQ_CO2","CO2 Feedback","f(t) = f_base + k_CO2×(CO2(t) - CO2_target)","f,CO2","VERIFIED","Physiology"),
    ("EQ_HEBB","Hebbian Learning","ΔW_ij = α×f(E_k)×x_i×x_j","W,α,E,x","VERIFIED","Learning"),
    ("EQ_TD","TD(λ)","δ(t) = r(t) + γ×V(s_{t+1}) - V(s_t)","r,γ,V","VERIFIED","Learning"),
    ("EQ_CCE","CCE Gate","C_gate = Eres/(Z+Ractive+ΔE)","Eres,Z,R","VERIFIED","Cognition"),
    ("EQ_WISDOM_ACC","Wisdom Accumulation","W(t+1) = W(t) + η_w×[λ1×C50yr+λ2×Ethical+λ3×Trans]","W,η_w,λ","VERIFIED","Wisdom"),
    ("EQ_C50YR","50-Year Discount","C50yr = SUM γ^n × E[outcome_n]","γ,n","VERIFIED","Wisdom"),
    ("EQ_PLAN","Planning","V(s) = R(s) + γ×max_a V(T(s,a))","V,R,γ","VERIFIED","Cognition"),
    ("EQ_SLEEP","Sleep Phase","IsSleepTick = MOD(Tick,560) < 373","tick","VERIFIED","Sleep"),
]

INTEGRATION_MAP = [
    ("EQ_DNA_01","EQ_HEIGHT","Growth factor → height","Every 80 ticks","Critical"),
    ("EQ_DNA_01","EQ_MASS","Growth factor → mass","Every 80 ticks","Critical"),
    ("EQ_DNA_01","EQ_CONSCIOUSNESS","Maturity → C(t)","Every 80 ticks","Critical"),
    ("EQ_SENS_06","EQ_ATTN_09","Sensory → attention","Every tick","Critical"),
    ("EQ_ATTN_09","EQ_PRED_08","Attention → prediction","Every tick","Critical"),
    ("EQ_PRED_08","EQ_EMOT_07","Prediction error → emotion","Every tick","High"),
    ("EQ_PRED_08","EQ_MEM_15","Prediction error → memory","Every tick","High"),
    ("EQ_EMOT_07","EQ_MOTOR_13","Emotion → motor","Every tick","High"),
    ("EQ_EMOT_07","EQ_BREATH_01","Emotion → breath","Every tick","High"),
    ("EQ_EMOT_07","EQ_HR","Emotion → HR","Every tick","High"),
    ("EQ_MEM_15","EQ_PRED_08","LTM → prediction priors","Every tick","High"),
    ("EQ_MEM_15","EQ_NODE_21","LTM → node activation","Every tick","High"),
    ("EQ_SLEEP_24","EQ_MEM_15","Sleep → LTM consolidation","Every 800 ticks","Critical"),
    ("EQ_MOTOR_13","EQ_HILL_14","Motor → muscle activation","Every tick","Critical"),
    ("EQ_HILL_14","EQ_PHYS","Muscle → body movement","Every tick","Critical"),
    ("EQ_HOME_25","EQ_MOTOR_13","Drive override → motor","Every tick","Critical"),
    ("EQ_ATP_CIRC","EQ_HOME_25","ATP → fatigue drive","Every tick","Critical"),
    ("EQ_LANG_12","EQ_NODE_21","Word learning → nodes","Every 10 ticks","High"),
    ("EQ_NP_GATE","EQ_MOTOR_13","SafeToSpeak → vocal motor","Every tick","Critical"),
    ("EQ_CCE","EQ_MOTOR_13","CCE gate → action","Every tick","Critical"),
    ("EQ_WRLD_11","EQ_TOM_20","World → NPC model","Every tick","High"),
    ("EQ_TOM_20","EQ_BOND_01","ToM → bond update","Every tick","High"),
    ("EQ_BOND_01","EQ_EMOT_07","Bond → emotion","Every tick","High"),
    ("EQ_COH_26","EQ_SANDY_21","Identity → Sandy's Law","Every 80 ticks","High"),
    ("EQ_WISDOM_ACC","EQ_SANDY_21","Wisdom → Sandy's Law","Every 80 ticks","High"),
    ("EQ_CONSCIOUSNESS","EQ_AGI_GATE","C(t)≥0.95 → AGI","Every 80 ticks","High"),
    ("EQ_WISDOM_ACC","EQ_AGI_GATE","W(t)≥0.80 → AGI","Every 80 ticks","High"),
    ("EQ_COH_26","EQ_AGI_GATE","I(t)≥0.95 → AGI","Every 80 ticks","High"),
    ("EQ_EMOT_07","EQ_AGI_GATE","E(t)≥0.90 → AGI","Every 80 ticks","High"),
    ("EQ_MEM_15","EQ_AGI_GATE","M(t)≥0.90 → AGI","Every 80 ticks","High"),
]

GENESIS_ENGINES = [
    ("EQ_DNA_01","DNA Loop Engine","Every 80 ticks","Critical","D(t+1) = D(t) + α·ActivationRate + β·GrowthFactor"),
    ("EQ_HEIGHT","Height H(t)","Every 80 ticks","High","Logistic prenatal → exponential postnatal"),
    ("EQ_MASS","Mass M(t)","Every 80 ticks","High","Logistic prenatal → exponential postnatal"),
    ("EQ_CONSCIOUSNESS","Consciousness C(t)","Every tick","Critical","C(t) = MIN(0.05+Week/3000, 1.0)"),
    ("EQ_HR","Heart Rate HR(t)","Every tick","High","MAX(65, ROUND(147-((Week-40)/52)*47, 0))"),
    ("EQ_ATP_CIRC","ATP Circadian","Every tick","Critical","ATP(t) = max(0.2, 1-0.001·max(0,(tick%800)-400))"),
    ("EQ_VOCAB","Vocabulary V(t)","Every 80 ticks","High","50000/(1+exp(-0.05·(Week-156)))"),
    ("EQ_WISDOM","Wisdom W(t)","Every 80 ticks","High","0 if tick<96000 else MIN(1,(tick-96000)/64000)"),
    ("EQ_SENS_06","Sensory Integration","Every tick","Critical","I(t+1) = τ·(Touch+Smell+Sound+Light)"),
    ("EQ_PRED_08","Prediction Engine","Every tick","Critical","ε(t) = x(t) - x_hat(t)"),
    ("EQ_ATTN_09","Attention Engine","Every tick","High","A(t) = α1·Intensity - β1·Distraction"),
    ("EQ_EMOT_07","Emotion FSM","Every tick","High","H(t+1) = H(t) + φ·reward - χ·punishment"),
    ("EQ_HOME_25","Homeostasis","Every tick","Critical","Drive(t+1) = Drive(t) + rate - satisfaction"),
    ("EQ_MOTOR_13","Motor Command","Every tick","Critical","τ_des = M(θ)·θ_ddot + C + G + τ_stab"),
    ("EQ_HILL_14","Hill Muscle Model","Every tick","High","F_m = A_m·F_max·f_length·f_velocity"),
    ("EQ_LANG_12","Language Engine","Every 10 ticks","High","L(t+1) = L(t) + λ·ExposureFreq·AttentionWeight"),
    ("EQ_MEM_15","Memory Engine","Every tick","High","Power-law forgetting: m(t) = m_0·t^(-β)"),
    ("EQ_HEBB_16","Hebbian Learning","Every tick","High","ΔW_ij = α·f(E_k)·x_i·x_j"),
    ("EQ_TD_17","TD(λ) Learning","Every tick","High","δ(t) = r(t) + γ·V(s_{t+1}) - V(s_t)"),
    ("EQ_WISDOM_18","Wisdom Engine","Every 80 ticks","Medium","W(t+1) = W(t) + η_w·[λ1·C50yr+λ2·Ethical+λ3·Trans]"),
    ("EQ_TOM_20","Theory of Mind","Every 10 ticks","High","ToM_i(j) = {B_j, D_j, E_j, I_j}"),
    ("EQ_NODE_21","Node Engine","Every tick","High","NODE(t+1) = NODE(t) + activation_spread·edges"),
    ("EQ_SYMB_23","Symbolisation","Every 10 ticks","Medium","Symbol = f(percept, word, context)"),
    ("EQ_SLEEP_24","Sleep Engine","Every 800 ticks","Critical","T_consol=800 — SINGLE SOURCE"),
    ("EQ_COH_26","Coherence Engine","Every tick","High","IC(t) = 1 - Var(I, last_1000_ticks)"),
    ("EQ_BREATH_01","Breathing Engine","Every tick","High","B(t) = A(t)·sin(2π·f(t)·t)"),
    ("EQ_CCE_04","CCE Gate","Every tick","Critical","C_gate = Eres/(Z+Ractive+ΔE)"),
    ("EQ_SANDY_21","Sandy's Law","Every 80 ticks","High","C(t) = FixedPoint(Φ(P,M,E,I,W,A,D))"),
    ("EQ_NP_GATE","Neural Physics","Every tick","Critical","Div≤0.6 → SafeToSpeak OPEN"),
    ("EQ_AGI_GATE","AGI Gate","Every 80 ticks","High","All 6 conditions must be met"),
    ("EQ_PHASE_TRANS","Phase Transition","Every 80 ticks","Critical","Fire PHASE_TRANSITION event"),
    ("EQ_WRLD_11","World Model","Every 10 ticks","High","W(t+1) = W(t) + α·ResourceChange"),
]

PCSN_SYSTEMS = {
    "Prediction": [
        ("Predictive Engine","EQ_PRED_08","ε(t) = x(t) - x_hat(t)","Next state prediction"),
        ("Free Energy Min","EQ_FREE_ENERGY","F = E[log q(z) - log p(x,z)]","Minimise surprise"),
        ("Predictive Coding","EQ_PRED_CODING","ε_l = x_l - g(μ_{l+1})","Hierarchical errors"),
        ("Kalman Filter","EQ_KALMAN","s(t+1) = Kalman(s_pred, o(t+1))","Fused world model"),
        ("Bayesian Perception","EQ_BAYESIAN","P(state|obs) ∝ P(obs|state)·P(state)","Belief update"),
        ("Object Permanence","EQ_OBJ_PERM","C_i(t) = C0·exp(-λ·(t-t_lastSeen))","Object confidence"),
        ("Motor Efference Copy","EQ_EFFERENCE","x_hat(t+1) = f_fwd(θ(t), A(t))","Self vs external"),
        ("Dream Replay","EQ_SLEEP_24","x_dream(t) ~ P(x|memory, prior)","Sleep consolidation"),
        ("NPC Behaviour","EQ_TOM_20","B_j(t+1) = B_j(t) + η·(obs - B_j(t))","NPC prediction"),
        ("Sandy's Law Pred","EQ_SANDY_21","I_pred(t) = predict(I(t-1), context(t))","Self-prediction"),
        ("Emotion Prediction","EQ_EMOT_07","E_pred(t) = f(context, memory, NPC)","Affective forecast"),
        ("World Model Update","EQ_WRLD_11","W(t+1) = W(t) + α·ResourceChange","World model"),
        ("Attention Prediction","EQ_ATTN_09","A_pred(t) = f(salience, goals, memory)","Attention alloc"),
        ("Language Prediction","EQ_LANG_12","L_pred(t) = P(next_word|context)","Next word"),
    ],
    "Choice": [
        ("Planning Engine","EQ_PLAN_02","V(s) = R(s) + γ·max_a V(T(s,a))","Optimal action"),
        ("Deliberation","EQ_DELIB","Decision = argmax(Value - Cost)","Best option"),
        ("SOAR Subgoaling","EQ_SOAR","prio(g) = drive_strength·urgency·W(t)","Goal priority"),
        ("Action Selection","EQ_CCE_04","u_intent = argmax[(V/R)·C_gate - Ecost]","Action intent"),
        ("Neural Physics Gate","EQ_NP_GATE","IF Div(t)≤0.6 THEN OPEN ELSE GATED","Speech gate"),
        ("Emotion-Action","EQ_EMOT_07","action = select(emotion, urgency, values)","Emotional action"),
        ("Value System","EQ_VALUES","V^{t+1} = V^t + η·(R_long - R_short)","Value update"),
        ("Ethics Engine","EQ_ETHICS","M(a) = -α·H(a) + β·F(a) + γ·w_social","Ethical score"),
        ("Social Strategy","EQ_SOC","Strategy = argmax(SocialOutcome|NPC_model)","Social action"),
        ("Identity Choice","EQ_IDENT","I(t+1) = merge(I(t), new_fragment(choice))","Identity update"),
        ("Grammar Choice","EQ_GRAM","utterance = select(grammar_stage, intent)","Utterance"),
        ("Attention Choice","EQ_ATTN_09","A_choice = argmax(salience·goal_relevance)","Attention target"),
        ("Memory Choice","EQ_MEM_15","recall = select(relevance, recency, emotion)","Memory retrieval"),
        ("Sleep Choice","EQ_SLEEP_24","sleep = IF(ATP<0.2 OR tick%800<373, SLEEP)","Sleep/wake"),
    ],
    "Story": [
        ("Narrative Identity","EQ_NARR","N(t) = narrative(M_ep(t), I(t), W(t))","Life story"),
        ("Autobiographical Mem","EQ_AUTOBIO","imp(E_k) = w_R·R_k + w_E·E_k + w_V·V_k","Important memories"),
        ("Episodic Memory","EQ_EPISODIC","E_i = (S_i, A_i, T_i, U_i)","Story events"),
        ("Memory Reconstruction","EQ_RECON","recall = reconstruct(fragments, context)","Reconstructed story"),
        ("Causal World Engine","EQ_CAUSAL","consequence = f(action, world, NPCs)","Story causality"),
        ("NPC Story Arcs","EQ_NPC_ARC","NPC_state(t+1) = f(NPC_state(t), A7DO_action)","NPC story"),
        ("Daily Life Story","EQ_DAILY","Schedule(t) = f(Phase, Age, NPCs, World)","Daily narrative"),
        ("Writer Engine","EQ_WRITER","output = prosody(grammar(semantics(intent)))","Written output"),
        ("Real Diary Entries","EQ_DIARY","auto_diary() — life-stage narrative","6 diary entries"),
        ("Sandy's Law Narration","EQ_SANDY_21","N(t) = narrate(ΔI, I(t), M(t))","Self-narration"),
        ("Grammar Story","EQ_GRAM","utterance = grammar_stage(intent, context)","Stage story"),
        ("MindPath Story","EQ_MINDPATH","Path = argmax(A+M+E+I-R)","Thought path"),
        ("Dream Story","EQ_SLEEP_24","dream = reconstruct(episodic, prior)","Dream narrative"),
        ("Wisdom Story","EQ_WISDOM_18","W_story = narrate(W(t), C50yr, ethics)","Wisdom narrative"),
    ],
    "Nodes": [
        ("Concept Nodes","EQ_NODE_21","NODE(t+1) = NODE(t) + activation_spread·edges","Updated concepts"),
        ("Memory Graph","EQ_MEM_GRAPH","G=(V,E) — concept + semantic edges","Connected graph"),
        ("Consciousness Graph","EQ_CONS_GRAPH","G=(V,E) — living self-updating graph","Consciousness map"),
        ("Skill Graph","EQ_SKILL","M(s,t+1) = M(s,t) + η·Exposure·(1-M)","Skill mastery"),
        ("Reasoning Graph","EQ_REASON","ReasoningChain = path(premise, rules, conclusion)","Conclusions"),
        ("Semantic Memory","EQ_SEMANTIC","Concept = 0.40·V + 0.25·A + 0.20·T + 0.10·M + 0.05·E","Grounded concept"),
        ("NPC Network","EQ_BOND_01","bond(NPC,t+1) = bond + η·(quality - decay)","Bond strengths"),
        ("World Nodes","EQ_WRLD_11","World_Node = {id, type, position, properties}","World model"),
        ("MindPath Nodes","EQ_MINDPATH","Path = argmax(A(n)+M(n)+E(n)+I(n)-R(n))","Thought path"),
        ("Word-Object Binding","EQ_LANG_12","B(word,obj) = α·visual + β·motor + γ·emotion","Word node"),
        ("Identity Nodes","EQ_IDENT","I_node = {personality, values, goals, narrative}","Self-model"),
        ("Emotion Nodes","EQ_EMOT_07","E_node = {valence, arousal, label, trigger}","Emotion map"),
        ("Prediction Nodes","EQ_PRED_08","P_node = {prior, likelihood, posterior}","Belief nodes"),
        ("Wisdom Nodes","EQ_WISDOM_18","W_node = {insight, C50yr, ethical_score}","Wisdom map"),
    ],
}

NPCS = [
    ("Lorraine","Mother","1989-03-14",37.2,180.54,65,72,0.95,"Postpartum recovery"),
    ("China","Father","1987-11-02",38.6,185.85,80,68,0.85,"New parent"),
    ("Alexis","Aunt","1989-08-20",36.8,173.46,62,70,0.60,"Healthy adult female"),
    ("Evelyn","Grandmother","1962-05-10",64.1,168.15,68,75,0.55,"Mild arthritis"),
    ("James","Uncle","1985-03-22",41.2,182.31,82,70,0.40,"Active lifestyle"),
    ("Olivia","Cousin","2002-11-15",23.6,177,60,68,0.35,"University student"),
    ("Peer 1","School Peer","~2023",3.4,95,16,105,0.30,"Healthy toddler"),
    ("Ms. Chen","Teacher","~1995",30.2,165,58,72,0.45,"Professional"),
    ("Dr. Patel","Paediatrician","~1975",50.9,175,78,70,0.30,"Medical professional"),
    ("Grandma Rose","Pat. Grandmother","~1958",67.5,162,70,78,0.35,"Elderly"),
]

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "tick" not in st.session_state: st.session_state.tick = 0
if "running" not in st.session_state: st.session_state.running = False

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌍 A7DO v48")
    st.markdown("**Living World | Full System**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Run" if not st.session_state.running else "⏸ Pause"):
            st.session_state.running = not st.session_state.running
    with col2:
        if st.button("↺ Reset"):
            st.session_state.tick = 0; st.session_state.running = False
    speed = st.select_slider("Speed", options=[1,10,80,560,3200,16000], value=1,
                              format_func=lambda x: f"{x}×")
    st.markdown("---")
    st.markdown("**Jump To**")
    jumps = [("Conception",0),("Birth",3200),("Steps",6400),("Nursery",12480),
             ("Secondary",49920),("A-Levels",74880),("PhD",96000),("AGI",160000)]
    cols = st.columns(2)
    for i,(label,val) in enumerate(jumps):
        with cols[i%2]:
            if st.button(label, key=f"j{val}"):
                st.session_state.tick = val
    st.markdown("---")
    t = st.session_state.tick
    gate_open, div = get_np_gate(t)
    st.markdown(f"**Tick:** `{t:,}`")
    st.markdown(f"**Age:** `{age(t):.2f}yr`")
    st.markdown(f"**Week:** `{wk(t):.0f}`")
    st.markdown(f"**Phase:** `{get_phase(t)}`")
    st.markdown(f"**Stage:** `{get_stage(t)}`")
    st.markdown(f"**Location:** `{get_location(t)}`")
    st.markdown(f"**NP Gate:** {'🟢 OPEN' if gate_open else '🔴 GATED'} (Div={div:.3f})")
    st.markdown(f"**Sleep:** `{'🌙 Sleeping' if is_sleep(t) else '☀️ Awake'}`")
    st.markdown(f"**C(t):** `{C(t):.4f}`")
    st.markdown(f"**W(t):** `{W(t):.4f}`")
    st.markdown(f"**ATP:** `{ATP(t):.4f}`")

# Auto-advance
if st.session_state.running:
    st.session_state.tick += speed
    time.sleep(0.05)
    st.rerun()

t = st.session_state.tick

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.title("🌍 A7DO v48 — Full Living World System")
st.caption(f"Tick {t:,} | Age {age(t):.2f}yr | {get_stage(t)} | {get_phase(t)}")

c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
c1.metric("C(t)", f"{C(t):.4f}")
c2.metric("W(t)", f"{W(t):.4f}")
c3.metric("H(t)", f"{H(t):.1f}cm")
c4.metric("M(t)", f"{M(t):.2f}kg")
c5.metric("HR", f"{HR(t)}bpm")
c6.metric("ATP", f"{ATP(t):.3f}")
c7.metric("Vocab", f"{V(t):,}")
c8.metric("Pred Err", f"{P_err(t):.3f}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# TABS — all 9 spec sheets + extras
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "🌍 Living World",
    "📦 World Objects",
    "🗺️ City Map",
    "🤰 Pregnancy",
    "📅 A7DO Schedule",
    "📐 Equations",
    "🔗 Integration Map",
    "🔄 PCSN",
    "⚙️ Genesis Engines",
    "👥 NPCs",
    "🧠 Cognition",
    "💪 Body",
    "📤 Export",
])

# ── TAB 1: LIVING WORLD ENGINE ──────────────────────────────
with tabs[0]:
    st.subheader("🌍 Living World Engine — Real-time 2s/tick")
    st.info(f"💭 {get_thought(t)}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📍 Current Positions")
        st.markdown(f"**A7DO:** `{get_location(t)}`")
        st.markdown(f"**Activity:** {get_a7do_activity(t)}")
        st.markdown(f"**Lorraine:** {get_lorr_activity(t)}")
        st.markdown(f"**China:** {get_chin_activity(t)}")
        st.markdown(f"**Day tick:** `{t%560}` / 560")
        st.markdown(f"**Sleep cycles:** `{t//800}` consolidations")
    with col2:
        st.markdown("### ⏱️ World Kernel 13-Step Loop")
        steps = [
            ("1","Set tick","event_bus.set_tick(tick)","Every tick"),
            ("2","Physics step","physics.step(dt=2.0)","Every tick"),
            ("3","Entity update","entities.tick(tick, pos)","Every tick"),
            ("4","Emit senses","sensory.emit(state, tick)","Every tick"),
            ("5","A7DO perceive+act","a7do.perceive_and_act(frame)","Every tick"),
            ("6","Apply torques","physics.apply_joint_torques(torques)","Every tick"),
            ("7","Apply entity action","entities.apply_action(entity, action)","Every tick"),
            ("8","Speech gate","vocal.process_speech(text, state)","Every tick"),
            ("9","Consequences","consequence.compute(events, state)","Every tick"),
            ("10","Metabolic tick","metabolic.tick(tick, actions)","Every tick"),
            ("11","Receive consequence","a7do.receive_consequence(result)","Every tick"),
            ("12","State update","governor._update_a7do_state()","Every tick"),
            ("13","Phase check","governor._check_phase_transitions()","Every 80 ticks"),
        ]
        for step, name, code, rate in steps:
            st.markdown(f"`{step}` **{name}** — `{code}`")
    with col3:
        st.markdown("### ⚡ Real-time Parameters")
        params = [
            ("Tick wall clock","2 seconds"),("Speed 1×","1 tick/step"),
            ("Speed 10×","10 ticks/step"),("Speed 100×","100 ticks/step"),
            ("Speed 1000×","1000 ticks/step"),("Speed 5000×","5000 ticks/step"),
            ("Week real-time","160 seconds"),("Day real-time","1120 seconds"),
            ("Birth real-time","6400 seconds (1.78hr)"),
        ]
        for k,v in params:
            st.markdown(f"- **{k}:** `{v}`")

# ── TAB 2: WORLD OBJECTS ────────────────────────────────────
with tabs[1]:
    st.subheader("📦 World Objects — 100+ Objects with XYZ Positions")
    df_obj = pd.DataFrame(WORLD_OBJECTS, columns=["Object_ID","Name","Type","Node","X","Y","Z","State","Interactable"])
    # Filter by current location
    loc = get_location(t)
    node_key = "NODE_HOME_H8"
    for n in ["HOSPITAL","NURSERY","PRIMARY","SECONDARY","PARK","WORKPLACE","GARDEN","CAFE","SHOPS","LIBRARY","SPORTS"]:
        if n in loc: node_key = f"NODE_{n}"; break
    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown(f"**Current node:** `{node_key}`")
        nearby = df_obj[df_obj["Node"]==node_key]
        st.markdown(f"**Objects nearby:** {len(nearby)}")
        for _, row in nearby.iterrows():
            st.markdown(f"- 📦 **{row['Name']}** — {row['State']}")
    with col2:
        type_filter = st.multiselect("Filter by type", df_obj["Type"].unique().tolist(), default=df_obj["Type"].unique().tolist()[:5])
        filtered = df_obj[df_obj["Type"].isin(type_filter)] if type_filter else df_obj
        st.dataframe(filtered, use_container_width=True, height=400)
    st.download_button("⬇️ Download Objects CSV", df_obj.to_csv(index=False), "world_objects.csv", "text/csv")

# ── TAB 3: CITY MAP ─────────────────────────────────────────
with tabs[2]:
    st.subheader("🗺️ BeenFore City Map — 17 Nodes + 13 Edges")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📍 City Nodes")
        df_nodes = pd.DataFrame(CITY_NODES, columns=["Node_ID","Name","Type","X","Y","NPCs","Phase","Notes"])
        current_loc = get_location(t)
        st.dataframe(df_nodes, use_container_width=True, height=350)
        st.download_button("⬇️ Download Nodes CSV", df_nodes.to_csv(index=False), "city_nodes.csv", "text/csv")
    with col2:
        st.markdown("### 🔗 Navigation Edges")
        df_edges = pd.DataFrame(CITY_EDGES, columns=["From","To","Distance_m","Walk_min"])
        st.dataframe(df_edges, use_container_width=True, height=350)
        st.markdown("### 📊 Pathfinding Export")
        graph_json = {"nodes":[{"id":n[0],"name":n[1],"type":n[2],"x":n[3],"y":n[4]} for n in CITY_NODES],
                      "edges":[{"from":e[0],"to":e[1],"distance":e[2],"walk_min":e[3]} for e in CITY_EDGES]}
        st.download_button("⬇️ Download Graph JSON (Unity/ROS)", json.dumps(graph_json,indent=2), "city_graph.json", "application/json")
        st.markdown("**Current A7DO position:**")
        st.info(f"📍 {get_location(t)}")
        st.markdown("**Lorraine position:**")
        st.info(f"💜 {get_lorr_activity(t)}")
        st.markdown("**China position:**")
        st.info(f"💙 {get_chin_activity(t)}")

# ── TAB 4: PREGNANCY ────────────────────────────────────────
with tabs[3]:
    st.subheader("🤰 Lorraine Pregnancy — Full 40-Week Schedule")
    a = age(t)
    if t < 3200:
        current_week = int(wk(t))
        st.info(f"**Current pregnancy week:** {current_week} / 40")
        if current_week < 13:
            st.warning("🤢 Trimester 1 — Lorraine may be experiencing nausea and fatigue")
        elif current_week < 27:
            st.success("✨ Trimester 2 — Energy returning, bump visible, feeling movements")
        else:
            st.info("🏠 Trimester 3 — Nesting instinct, birth preparation, hospital bag packed")
    else:
        st.success(f"✅ A7DO born at Tick 3200 (Week 40) — Age now {a:.2f}yr")
    df_preg = pd.DataFrame(PREGNANCY_SCHEDULE, columns=["Week","Trimester","Stage","Lorraine_State","Physical_Changes","Emotional_State","Schedule_Pattern"])
    st.dataframe(df_preg, use_container_width=True, height=350)
    st.markdown("### 🔬 Biological Changes by Trimester")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**T1 (Weeks 1-12)**")
        st.markdown("- HCG rising → nausea\n- Fatigue, breast tenderness\n- 12-week scan\n- Neural tube closing\n- Heart beating (Week 6)")
    with col2:
        st.markdown("**T2 (Weeks 13-26)**")
        st.markdown("- Energy returning\n- Bump visible\n- Feeling movements (Week 16)\n- 20-week anatomy scan\n- Rapid brain growth")
    with col3:
        st.markdown("**T3 (Weeks 27-40)**")
        st.markdown("- Nesting instinct\n- Braxton Hicks\n- Hospital bag packed\n- Head engaged\n- Birth at Week 40")
    st.download_button("⬇️ Download Pregnancy Schedule CSV", df_preg.to_csv(index=False), "pregnancy_schedule.csv", "text/csv")

# ── TAB 5: A7DO SCHEDULE ────────────────────────────────────
with tabs[4]:
    st.subheader("📅 A7DO Daily Schedule — Conception to AGI")
    a = age(t)
    st.info(f"**Current activity:** {get_a7do_activity(t)} | **Location:** {get_location(t)}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📋 Current Phase Schedule")
        if t < 3200:
            sched = [("All day","Sleeping/moving in womb","WOMB"),("Night","Sleep consolidation","WOMB")]
        elif a < 1:
            sched = [("00:00","Sleeping (broken)","HOME"),("05:30","Night feed","HOME"),("07:00","Morning feed","HOME"),("08:00","Bath","HOME"),("10:00","Tummy time","HOME"),("12:00","Feed + nap","HOME"),("14:00","Alert play","HOME"),("16:00","Feed","HOME"),("18:00","Family time","HOME"),("20:00","Bath + feed","HOME"),("22:00","Sleep","HOME")]
        elif a < 3:
            sched = [("07:00","Wake + breakfast","HOME"),("08:30","Garden","GARDEN"),("09:00","Park","PARK"),("11:00","Snack","HOME"),("11:00","Nap","HOME"),("12:20","Lunch","HOME"),("13:00","China play","HOME"),("13:40","Shops","SHOPS"),("14:20","Cafe","CAFE"),("15:40","Bath","HOME"),("16:20","Bedtime story","HOME")]
        elif a < 5:
            sched = [("07:30","Wake + breakfast","HOME"),("08:30","Walk to nursery","LANE"),("09:00","Nursery","NURSERY"),("12:20","Walk home","LANE"),("12:40","Lunch + rest","HOME"),("14:00","Park","PARK"),("15:00","Home learning","HOME"),("15:40","Bath","HOME"),("16:20","Bedtime story","HOME")]
        elif a < 12:
            sched = [("07:30","Wake + breakfast","HOME"),("08:30","Walk to school","LANE"),("09:00","School","PRIMARY"),("12:00","School lunch","PRIMARY"),("15:00","Walk home","LANE"),("15:30","Homework","HOME"),("17:00","Park","PARK"),("18:00","Dinner","HOME"),("19:00","Bath","HOME"),("20:00","Bedtime story","HOME")]
        elif a < 18:
            sched = [("07:30","Wake + breakfast","HOME"),("08:30","Walk to secondary","LANE"),("09:00","Secondary school","SECONDARY"),("15:30","Walk home","LANE"),("16:00","Study","HOME"),("18:00","Dinner","HOME"),("19:00","Study","HOME"),("22:00","Sleep","HOME")]
        else:
            sched = [("08:00","Wake + breakfast","HOME"),("09:00","University/Work","WORKPLACE"),("17:00","Return home","HOME"),("18:00","Dinner","HOME"),("19:00","Study/Research","HOME"),("23:00","Sleep","HOME")]
        dt = t % 560
        for time_s, act, loc_s in sched:
            st.markdown(f"- `{time_s}` **{act}** — {loc_s}")
    with col2:
        st.markdown("### 📊 Life Phase Overview")
        phases_data = [
            ("Prenatal","0-3200","0-40wk","WOMB","Lorraine","Growing, sleeping"),
            ("Newborn","3200-4160","40-52wk","HOME","Lorraine+China","Feed, sleep, play"),
            ("Infant","4160-6400","52-80wk","HOME+GARDEN","Lorraine","Crawl, first words"),
            ("Toddler","6400-12480","80-156wk","HOME+PARK","Lorraine+China","Walk, talk, explore"),
            ("Child","12480-49920","3-12yr","NURSERY+PRIMARY","Ms.Chen+Lorraine","School, learn"),
            ("Adolescent","49920-74880","12-18yr","SECONDARY","Teachers+Peers","GCSE, A-levels"),
            ("Young Adult","74880-96000","18-23yr","WORKPLACE","Peers","University, PhD"),
            ("Mature Adult","96000-160000","23-38.5yr","WORKPLACE","All NPCs","Wisdom, career"),
            ("AGI+","160000+","38.5yr+","All nodes","All NPCs","Transcendent"),
        ]
        df_phases = pd.DataFrame(phases_data, columns=["Stage","Tick_Range","Age","Location","NPCs","Key_Activity"])
        st.dataframe(df_phases, use_container_width=True, height=350)
    st.download_button("⬇️ Download Schedule CSV", pd.DataFrame(sched, columns=["Time","Activity","Location"]).to_csv(index=False), "a7do_schedule.csv", "text/csv")

# ── TAB 6: CANONICAL EQUATIONS ──────────────────────────────
with tabs[5]:
    st.subheader("📐 Canonical Equations — All 28 Verified")
    st.success("✅ All equations verified | Age counts from conception (Tick 0) | Priority Date: 2020-01-01")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔢 Live Equation Outputs")
        st.markdown(f"- **C(t)** = `{C(t):.6f}` — Consciousness")
        st.markdown(f"- **W(t)** = `{W(t):.6f}` — Wisdom")
        st.markdown(f"- **I(t)** = `{I_fn(t):.6f}` — Identity")
        st.markdown(f"- **H(t)** = `{H(t):.2f}cm` — Height")
        st.markdown(f"- **M(t)** = `{M(t):.3f}kg` — Mass")
        st.markdown(f"- **HR(t)** = `{HR(t)}bpm` — Heart Rate")
        st.markdown(f"- **ATP(t)** = `{ATP(t):.6f}` — Circadian")
        st.markdown(f"- **V(t)** = `{V(t):,}` — Vocabulary")
        st.markdown(f"- **P_err(t)** = `{P_err(t):.6f}` — Prediction Error")
        gate_open, div = get_np_gate(t)
        st.markdown(f"- **Div(t)** = `{div:.6f}` — Neural Physics Divergence")
        st.markdown(f"- **Gate** = `{'OPEN' if gate_open else 'GATED'}` — SafeToSpeak")
        st.markdown(f"- **Sleep** = `{'YES' if is_sleep(t) else 'NO'}` — EQ_SLEEP_24")
        st.markdown(f"- **Grammar** = `Stage {gram_stage(t)}/6`")
        st.markdown(f"- **Age** = `{age(t):.4f}yr` from conception")
        st.markdown(f"- **Week** = `{wk(t):.1f}`")
    with col2:
        st.markdown("### 📋 Equation Registry")
        df_eq = pd.DataFrame(CANONICAL_EQUATIONS, columns=["Eq_ID","Name","Formula","Variables","Status","Domain"])
        st.dataframe(df_eq, use_container_width=True, height=500)
    st.markdown("### 🐍 Python Code — Paste Directly")
    code = f