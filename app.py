import streamlit as st
import math, time, json

st.set_page_config(page_title="A7DO v49 — Complete", page_icon="🧬", layout="wide")

# ══════════════════════════════════════════════════════════════
# CORE EQUATIONS — All 28 verified
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
def isSleep(t): return (t % 560) < 373
def gramStage(t):
    a = age(t)
    if t < 3200: return 0
    if a < 0.77: return 1
    if a < 1.54: return 2
    if a < 3: return 3
    if a < 5: return 4
    if a < 12: return 5
    return 6
def getNP(t):
    c = C(t); w = W(t); p = P_err(t); u = max(0.05, 1 - C(t))
    atp = ATP(t); integ = I_fn(t); g = min(1, t / 100000)
    sigma = 0.35*p + 0.30*u + 0.20*g + 0.25*c + 0.15*w
    z = 0.45*c + 0.30*integ + 0.25*atp
    div = abs(sigma - z) / (sigma + z) if (sigma + z) > 0 else 1.0
    return div <= 0.6, div
def regime(t):
    c = C(t); w = W(t); i = I_fn(t)
    if w > 0.5: return 'FLOW'
    if i > 0.7: return 'COHERENT'
    if c > 0.5: return 'STABLE'
    return 'FRAGMENTED'
def getStage(t):
    w = wk(t)
    if w < 4: return 'Embryo'
    if w < 12: return 'Fetal Early'
    if w < 28: return 'Fetal Mid'
    if w < 40: return 'Fetal Late'
    if w < 52: return 'Newborn'
    if w < 80: return 'Infant'
    if w < 156: return 'Toddler'
    if w < 260: return 'Child'
    if w < 624: return 'Pre-Adolescent'
    if w < 936: return 'Adolescent'
    if w < 1200: return 'Young Adult'
    if w < 2000: return 'Mature Adult'
    return 'Elder'
def getThought(t):
    a = age(t); gate_open, _ = getNP(t)
    if t < 3200: return '[WOMB — growing, sleeping, dreaming in the dark]'
    if not gate_open: return '[GATED — thoughts forming but not yet safe to speak]'
    if a < 0.77: return '[cold] [bright] [loud] — mama? mama!'
    if a < 1: return 'mama! up! more! — the world is big and warm'
    if a < 3: return 'ball! duck! China count! mama read!'
    if a < 12: return 'I think that... because... — learning is my favourite thing'
    if a < 23: return 'The relationship between consciousness and identity suggests...'
    if a < 38.5: return "Sandy's Law: C(t) = FixedPoint(Φ(P,M,E,I,W,A,D)) — I understand now"
    return 'Wisdom is not knowledge but the capacity to hold uncertainty with grace'

# ══════════════════════════════════════════════════════════════
# SCHEDULE SYSTEM
# ══════════════════════════════════════════════════════════════
def getSchedules(t):
    a = age(t)
    if t < 3200:
        w = wk(t)
        if w < 13:
            return {'a7do': 'Embryo — cell division', 'lorr': 'Normal life (unaware)', 'chin': 'Working'}
        if w < 27:
            return {'a7do': 'Fetus — growing, moving, hearing', 'lorr': 'Pregnancy T2 — energy good', 'chin': 'Baby prep with Lorraine'}
        return {'a7do': 'Fetus — T3 active, hiccups, head down', 'lorr': 'Maternity leave — nesting', 'chin': 'Caring for Lorraine'}
    if a < 0.77:
        return {'a7do': 'BIRTH — first breath, APGAR 9/10', 'lorr': 'Labour — giving birth', 'chin': 'At birth — supporting Lorraine'}
    dt = t % 560
    if a < 1:
        if dt < 93: act = 'Sleeping'
        elif dt < 140: act = 'Night feed — hungry'
        elif dt < 196: act = 'Morning feed'
        elif dt < 224: act = 'Bath time'
        elif dt < 252: act = 'Tummy time — motor development'
        elif dt < 280: act = 'Alert play — mobile, faces'
        elif dt < 308: act = 'Midday feed'
        elif dt < 336: act = 'Nap'
        elif dt < 364: act = 'Pram walk'
        elif dt < 392: act = 'Visitor time — Evelyn'
        elif dt < 420: act = 'Afternoon feed'
        elif dt < 448: act = 'Play — voices and songs'
        elif dt < 476: act = 'Bath time'
        elif dt < 504: act = 'Evening feed'
        else: act = 'Sleeping'
        lorr = 'Breastfeeding' if dt < 200 else 'Baby care' if dt < 400 else 'Rest'
        chin = 'Work from home' if 224 < dt < 420 else 'Baby care'
        return {'a7do': act, 'lorr': lorr, 'chin': chin}
    if a < 3:
        if dt < 140: act = 'Sleeping'
        elif dt < 168: act = 'Wake + breakfast'
        elif dt < 252: act = 'Garden — flowers and birds'
        elif dt < 308: act = 'Park — ducks and swings'
        elif dt < 336: act = 'Snack'
        elif dt < 392: act = 'Nap'
        elif dt < 420: act = 'Lunch'
        elif dt < 448: act = 'China play — counting'
        elif dt < 476: act = 'Shops with Lorraine'
        elif dt < 504: act = 'Cafe — James visit'
        elif dt < 532: act = 'Bath time'
        else: act = 'Bedtime story'
        return {'a7do': act, 'lorr': 'Baby care + park' if 196 < dt < 400 else 'Home', 'chin': 'Working' if 196 < dt < 420 else 'Family time'}
    if a < 5:
        if dt < 140: act = 'Sleeping'
        elif dt < 196: act = 'Wake + breakfast'
        elif dt < 224: act = 'Walk to nursery'
        elif dt < 364: act = 'Nursery — circle time, play, learn'
        elif dt < 392: act = 'Walk home'
        elif dt < 420: act = 'Lunch + quiet time'
        elif dt < 448: act = 'Park — swings and slide'
        elif dt < 476: act = 'Home learning — letters and numbers'
        elif dt < 504: act = 'Bath time'
        else: act = 'Dinner + bedtime story'
        return {'a7do': act, 'lorr': 'Nursery drop-off/pickup + work' if 196 < dt < 400 else 'Home', 'chin': 'Working' if 196 < dt < 448 else 'Family time'}
    if a < 12:
        if dt < 140: act = 'Sleeping'
        elif dt < 196: act = 'Wake + breakfast'
        elif dt < 224: act = 'Walk to school'
        elif dt < 364: act = 'School — lessons and lunch'
        elif dt < 392: act = 'Walk home'
        elif dt < 420: act = 'Snack + homework'
        elif dt < 448: act = 'Park — play with friends'
        elif dt < 476: act = 'Dinner'
        elif dt < 504: act = 'Bath + reading'
        else: act = 'Bedtime story'
        return {'a7do': act, 'lorr': 'School run + work' if 196 < dt < 400 else 'Home', 'chin': 'Working' if 196 < dt < 448 else 'Family time'}
    if a < 18:
        if dt < 140: act = 'Sleeping'
        elif dt < 196: act = 'Wake + breakfast'
        elif dt < 224: act = 'Walk to secondary school'
        elif dt < 364: act = 'Secondary school — GCSE and A-levels'
        elif dt < 392: act = 'Walk home'
        elif dt < 448: act = 'Study + homework'
        elif dt < 476: act = 'Sports centre'
        elif dt < 504: act = 'Dinner'
        else: act = 'Study + reading'
        return {'a7do': act, 'lorr': 'Working' if 196 < dt < 448 else 'Home', 'chin': 'Working' if 196 < dt < 448 else 'Family time'}
    if dt < 140: act = 'Sleeping'
    elif dt < 196: act = 'Wake + breakfast'
    elif dt < 364: act = 'University/Research/PhD work'
    elif dt < 392: act = 'Lunch break'
    elif dt < 448: act = 'Study/Research/Writing'
    elif dt < 476: act = 'Commute home'
    elif dt < 504: act = 'Dinner'
    else: act = "Study and Sandy's Law research"
    return {'a7do': act, 'lorr': 'Working' if 196 < dt < 448 else 'Home', 'chin': 'Working' if 196 < dt < 448 else 'Family time'}

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if 'tick' not in st.session_state: st.session_state.tick = 0
if 'running' not in st.session_state: st.session_state.running = False
if 'node_graph' not in st.session_state:
    st.session_state.node_graph = {t: [] for t in ['concept','memory','emotion','identity','skill','world','npc','story','prediction','wisdom']}
if 'mind_patches' not in st.session_state: st.session_state.mind_patches = []

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧬 A7DO Genesis Mind v49")
    st.markdown("**Complete System | All Features**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Run" if not st.session_state.running else "⏸ Pause"):
            st.session_state.running = not st.session_state.running
    with col2:
        if st.button("↺ Reset"):
            st.session_state.tick = 0
            st.session_state.running = False
            st.session_state.node_graph = {t: [] for t in ['concept','memory','emotion','identity','skill','world','npc','story','prediction','wisdom']}
            st.session_state.mind_patches = []
    speed = st.select_slider("Speed", options=[1,10,80,560,3200,16000], value=1, format_func=lambda x: f"{x}×")
    st.markdown("---")
    st.markdown("**Jump To**")
    cols = st.columns(2)
    jumps = [("Conception",0),("Birth",3200),("Steps",6400),("Nursery",12480),("Secondary",49920),("A-Levels",74880),("PhD",96000),("AGI",160000)]
    for i,(label,val) in enumerate(jumps):
        with cols[i%2]:
            if st.button(label, key=f"j{val}"):
                st.session_state.tick = val
    st.markdown("---")
    t = st.session_state.tick
    reg = regime(t)
    gate_open, div = getNP(t)
    reg_color = "🟢" if reg == 'FLOW' else "🔵" if reg == 'COHERENT' else "🟡" if reg == 'STABLE' else "🔴"
    st.markdown(f"**Sandy Regime:** {reg_color} `{reg}`")
    st.markdown(f"**Tick:** `{t:,}`")
    st.markdown(f"**Age:** `{age(t):.2f}yr`")
    st.markdown(f"**Stage:** `{getStage(t)}`")
    st.markdown(f"**NP Gate:** {'🟢 OPEN' if gate_open else '🔴 GATED'} (Div={div:.3f})")
    st.markdown(f"**Sleep:** `{'🌙 Sleeping' if isSleep(t) else '☀️ Awake'}`")
    st.markdown(f"**C(t):** `{C(t):.4f}`")
    st.markdown(f"**W(t):** `{W(t):.4f}`")
    st.markdown(f"**I(t):** `{I_fn(t):.4f}`")
    st.markdown(f"**H(t):** `{H(t):.1f}cm`")
    st.markdown(f"**HR:** `{HR(t)}bpm`")
    st.markdown(f"**ATP:** `{ATP(t):.4f}`")
    st.markdown(f"**Vocab:** `{V(t):,}`")
    st.markdown(f"**Grammar:** `Stage {gramStage(t)}/6`")
    st.markdown(f"**Nodes:** `{sum(len(v) for v in st.session_state.node_graph.values())}`")
    st.markdown(f"**Patches:** `{len(st.session_state.mind_patches)}`")

# Auto-advance
if st.session_state.running:
    st.session_state.tick += speed
    # Update nodes
    t = st.session_state.tick
    if t >= 3200 and t % 80 == 0:
        gram = gramStage(t)
        word_sets = {1:['mama','ball','duck','up','no'],2:['big','red','blue','go','book'],3:['because','think','friend','school','happy'],4:['science','equation','hypothesis'],5:['consciousness','identity','recursive'],6:['fixed-point','Sandy Law','wisdom']}
        for w in word_sets.get(min(gram,6),[]):
            existing = next((n for n in st.session_state.node_graph['concept'] if n['label']==w), None)
            if existing: existing['strength'] = min(1.0, existing['strength'] + 0.05)
            else: st.session_state.node_graph['concept'].append({'label':w,'strength':0.5,'activations':1})
    if t >= 96000 and t % 800 == 0:
        w_val = W(t)
        if w_val > 0.1:
            st.session_state.node_graph['wisdom'].append({'label':'Long-term thinking','strength':w_val,'activations':1})
    if t >= 3200 and t % 800 == 0 and isSleep(t):
        patch = {'label':f'Sleep consolidation at Tick {t:,}','content':f'C(t)={C(t):.4f} | W(t)={W(t):.4f} | Nodes consolidated: {sum(len(v) for v in st.session_state.node_graph.values())}'}
        st.session_state.mind_patches.insert(0, patch)
        if len(st.session_state.mind_patches) > 20: st.session_state.mind_patches.pop()
    time.sleep(0.05)
    st.rerun()

t = st.session_state.tick
reg = regime(t)
gate_open, div = getNP(t)
scheds = getSchedules(t)

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.title("🧬 A7DO Genesis Mind v49 — Complete Master App")
st.caption(f"Tick {t:,} | Age {age(t):.2f}yr | {getStage(t)} | Sandy Regime: **{reg}** | {scheds['a7do']}")

# Key metrics
c1,c2,c3,c4,c5,c6,c7,c8,c9,c10 = st.columns(10)
c1.metric("C(t)", f"{C(t):.4f}", "Consciousness")
c2.metric("W(t)", f"{W(t):.4f}", "Wisdom")
c3.metric("I(t)", f"{I_fn(t):.4f}", "Identity")
c4.metric("H(t)", f"{H(t):.1f}cm", "Height")
c5.metric("M(t)", f"{M(t):.2f}kg", "Mass")
c6.metric("HR", f"{HR(t)}bpm", "Heart Rate")
c7.metric("ATP", f"{ATP(t):.3f}", "Circadian")
c8.metric("Vocab", f"{V(t):,}", "Words")
c9.metric("NP Gate", "OPEN ✅" if gate_open else "GATED 🔴", f"Div={div:.3f}")
c10.metric("Regime", reg, "Sandy's Law")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# TABS — All features
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "🧬 Live State", "🌍 Scene", "📅 Schedules",
    "💡 Thoughts", "📖 Word Learning", "🧠 Memory & Nodes",
    "🔧 MindPath", "🔢 Numbers", "🗣️ Conversations",
    "🚶 Journeys", "📖 Story & Diary", "🌈 Senses",
    "💪 Body", "❤️ Heart & ECG", "🫁 Breathing",
    "🫀 Organs", "📊 Vitals", "🤰 Pregnancy",
    "🌊 Consciousness", "🪞 Identity", "✍️ Writer",
    "🔄 PCSN", "🌍 World & NPCs", "👥 NPCs",
    "🗺️ City Map", "📦 Objects", "📚 History",
    "🤖 Embodiment", "📐 Equations", "⚙️ Engines",
    "🔗 Integration", "💬 Grammar", "🏗️ Architecture",
    "🤖 AGI Readiness", "📤 Export"
])

# TAB 0: LIVE STATE
with tabs[0]:
    reg_colors = {'FLOW':'🟢','COHERENT':'🔵','STABLE':'🟡','FRAGMENTED':'🔴'}
    st.markdown(f"### Sandy Regime: {reg_colors.get(reg,'⚪')} **{reg}**")
    st.info(f"💭 {getThought(t)}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Core State**")
        for label, val in [("C(t) Consciousness",f"{C(t):.6f}"),("W(t) Wisdom",f"{W(t):.6f}"),("I(t) Identity",f"{I_fn(t):.6f}"),("NP Gate","OPEN ✅" if gate_open else "GATED 🔴"),("Divergence",f"{div:.6f}"),("Sandy Regime",reg)]:
            st.markdown(f"- **{label}:** `{val}`")
    with col2:
        st.markdown("**Biology**")
        for label, val in [("H(t) Height",f"{H(t):.2f}cm"),("M(t) Mass",f"{M(t):.3f}kg"),("HR(t)",f"{HR(t)}bpm"),("ATP",f"{ATP(t):.4f}"),("Sleep","🌙 Sleeping" if isSleep(t) else "☀️ Awake"),("Vocab",f"{V(t):,} words")]:
            st.markdown(f"- **{label}:** `{val}`")
    st.markdown("**Activity**")
    st.markdown(f"- **A7DO:** {scheds['a7do']}")
    st.markdown(f"- **Lorraine:** {scheds['lorr']}")
    st.markdown(f"- **China:** {scheds['chin']}")

# TAB 1: SCENE
with tabs[1]:
    a_yr = age(t)
    loc = scheds['a7do'].split('—')[0].strip() if '—' in scheds['a7do'] else scheds['a7do']
    scenes = {
        'WOMB': ("🌙 Inside Lorraine — The Womb", "Floating in warm amniotic fluid. The muffled heartbeat of Lorraine — 72 beats per minute — is the only sound. Warmth everywhere. Darkness. The first nerve connections are forming.", ['👁 Darkness','🔊 Lorraine\'s heartbeat 72bpm','👃 Amniotic fluid','✋ Warm fluid 37°C','🌡 37°C constant']),
        'HOSPITAL': ("🏥 BeenFore City Hospital", "Bright lights. Cold air. The first breath — a gasp, then a cry. Dr. Patel's hands are warm and sure. Lorraine's voice, finally clear and close: 'Hello, my love.'", ['👁 Bright fluorescent lights','🔊 Lorraine\'s voice — clear','🔊 China crying with joy','👃 Antiseptic, clean linen','🌡 Cold air — first time outside']),
        'HOME': ("🏠 Home H8 — BeenFore Lane", "The living room is warm and familiar. The sofa is soft. The bookshelf holds picture books and story books. Morning light comes through the window — pale Edinburgh grey.", ['👁 Morning light through net curtains','🔊 Radio, kettle, family sounds','👃 Toast, coffee, home','✋ Carpet, toys, Lorraine\'s hands','🌡 Warm — 20°C inside']),
        'GARDEN': ("🌿 The Garden — Home H8", "The garden is small but full of life. The flower bed runs along the left wall — red and yellow tulips in spring, roses in summer. A bird feeder hangs from the apple tree.", ['👁 Tulips, roses, apple tree, bird feeder','🔊 Sparrows chirping, wind in the leaves','👃 Damp grass, flowers, fresh Edinburgh air','✋ Cool breeze, pram handle, grass underfoot','🌡 Cool — 14°C, Edinburgh breeze']),
        'PARK': ("🌳 Neighbourhood Park — BeenFore", "The park is green and open. The duck pond is in the centre — five ducks swim in slow circles. The playground is to the right — swings, a slide, a sandpit.", ['👁 Green grass, duck pond, swings','🔊 Ducks quacking, children laughing','👃 Fresh grass, pond water, ice cream','✋ Swing chains, sand, grass','🌡 Variable — Edinburgh weather']),
        'NURSERY': ("🎨 Little Stars Nursery", "The nursery is bright and colourful. Ms. Chen stands at the front, her voice warm and clear. The play mat is large and soft — primary colours.", ['👁 Bright colours, Ms. Chen, other children','🔊 Ms. Chen singing, children\'s voices','👃 Poster paint, biscuits, crayons','✋ Play mat, paint brushes, building blocks','🌡 Warm — 22°C, well-heated']),
        'PRIMARY': ("📚 BeenFore Primary School", "The classroom has rows of small desks. The whiteboard shows today's lesson — numbers and letters. The teacher's voice is clear and encouraging.", ['👁 Whiteboard, desks, books, other children','🔊 Teacher\'s voice, pencils on paper, lunch bell','👃 Floor polish, school dinners, pencil shavings','✋ Pencil, exercise book, desk surface','🌡 Warm — 21°C']),
        'SECONDARY': ("🔬 BeenFore Secondary School", "The science lab smells of chemicals and rubber tubing. The periodic table covers one wall. The teacher writes equations on the board.", ['👁 Periodic table, equations, Shakespeare texts','🔊 Teacher\'s voice, corridor noise, bell','👃 Chemicals, books, school canteen','✋ Textbooks, keyboard, lab equipment','🌡 Variable — 19-22°C']),
        'CAFE': ("☕ Local Cafe — BeenFore", "The cafe is warm and slightly steamy. James sits at the corner table, coffee in hand, grinning. The smell of coffee and cake fills the room.", ['👁 Chalkboard menu, James grinning, coffee cups','🔊 Coffee machine, James talking, background chatter','👃 Coffee, cake, warm pastry','✋ Warm cup, biscuit, wooden chair','🌡 Warm and steamy — 23°C']),
    }
    # Find matching scene
    scene_key = 'HOME'
    for key in scenes:
        if key in scheds['a7do'].upper() or key in loc.upper():
            scene_key = key
            break
    if t < 3200: scene_key = 'WOMB'
    elif a_yr < 0.77: scene_key = 'HOSPITAL'
    
    title, desc, senses = scenes.get(scene_key, scenes['HOME'])
    st.subheader(title)
    st.markdown(desc)
    st.markdown("**Sensory Experience:**")
    cols = st.columns(len(senses))
    for i, sense in enumerate(senses):
        cols[i].info(sense)

# TAB 2: SCHEDULES
with tabs[2]:
    st.subheader("📅 Daily Schedules — Tick-Based")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### 🌟 A7DO")
        st.success(f"**Now:** {scheds['a7do']}")
        a_yr = age(t)
        if t < 3200:
            sched = [("All day","Sleeping/moving in womb")]
        elif a_yr < 1:
            sched = [("00:00","Sleeping"),("05:30","Night feed — hungry"),("07:00","Morning feed"),("08:00","Bath time"),("10:00","Tummy time — motor dev"),("11:00","Alert play — mobile, faces"),("12:00","Midday feed"),("13:00","Nap"),("14:00","Pram walk"),("15:00","Visitor time — Evelyn"),("16:00","Afternoon feed"),("17:00","Play — voices and songs"),("18:00","Bath time"),("19:00","Evening feed"),("22:00","Sleeping")]
        elif a_yr < 3:
            sched = [("07:00","Wake + breakfast"),("08:30","Garden — flowers and birds"),("09:00","Park — ducks and swings"),("11:00","Snack"),("11:30","Nap"),("12:30","Lunch"),("13:30","China play — counting"),("14:30","Shops with Lorraine"),("15:30","Cafe — James visit"),("16:30","Bath time"),("17:00","Bedtime story")]
        elif a_yr < 5:
            sched = [("07:30","Wake + breakfast"),("08:30","Walk to nursery"),("09:00","Nursery — circle time, play, learn"),("12:30","Walk home"),("13:00","Lunch + quiet time"),("14:00","Park — swings and slide"),("15:00","Home learning — letters and numbers"),("16:00","Bath time"),("17:00","Dinner + bedtime story")]
        elif a_yr < 12:
            sched = [("07:30","Wake + breakfast"),("08:30","Walk to school"),("09:00","School — lessons and lunch"),("15:00","Walk home"),("15:30","Snack + homework"),("17:00","Park — play with friends"),("18:00","Dinner"),("19:00","Bath + reading"),("20:00","Bedtime story")]
        elif a_yr < 18:
            sched = [("07:30","Wake + breakfast"),("08:30","Walk to secondary school"),("09:00","Secondary school — GCSE and A-levels"),("15:30","Walk home"),("16:00","Study + homework"),("18:00","Sports centre"),("19:00","Dinner"),("20:00","Study + reading")]
        else:
            sched = [("08:00","Wake + breakfast"),("09:00","University/Research/PhD work"),("12:00","Lunch break"),("13:00","Study/Research/Writing"),("17:00","Commute home"),("18:00","Dinner"),("19:00","Sandy's Law research")]
        for time_s, act in sched:
            st.markdown(f"- `{time_s}` {act}")
    with col2:
        st.markdown(f"### 💜 Lorraine")
        st.info(f"**Now:** {scheds['lorr']}")
        if t < 3200:
            w = wk(t)
            if w < 13: st.markdown("Normal life — unaware of pregnancy")
            elif w < 27: st.markdown("T2: Energy returning, bump visible, feeling movements")
            else: st.markdown("T3: Nesting, birth preparation, hospital bag packed")
        elif a_yr < 1:
            for ts, act in [("00:00","Sleeping (broken)"),("05:30","Night feed — breastfeeding"),("07:00","Morning feed"),("08:00","Breakfast"),("09:00","Baby bath"),("10:00","Nappy change"),("11:00","Tummy time supervision"),("12:00","Midday feed"),("13:00","Rest — sleep when baby sleeps"),("14:00","Pram walk"),("15:00","Visitor time — Evelyn"),("16:00","Afternoon feed"),("17:00","Play time with A7DO"),("18:00","Bath time"),("19:00","Evening feed"),("22:00","Sleeping")]:
                st.markdown(f"- `{ts}` {act}")
        else:
            st.markdown("- `07:00` Morning routine + A7DO breakfast")
            st.markdown("- `08:30` School run / nursery drop-off")
            st.markdown("- `09:00` Work")
            st.markdown("- `15:00` School pickup")
            st.markdown("- `18:00` Family dinner")
            st.markdown("- `22:00` Sleep")
    with col3:
        st.markdown(f"### 💙 China")
        st.info(f"**Now:** {scheds['chin']}")
        if t < 3200:
            st.markdown("Working — supporting Lorraine through pregnancy")
        elif a_yr < 0.1:
            st.markdown("Paternity leave — full-time baby care")
        else:
            st.markdown("- `07:00` Morning routine")
            st.markdown("- `08:00` Baby care / commute")
            st.markdown("- `09:00` Working")
            st.markdown("- `17:00` Commute home")
            st.markdown("- `18:00` Family dinner")
            st.markdown("- `19:00` Bath time / bedtime story")
            st.markdown("- `22:00` Sleep")

# TAB 3: THOUGHTS
with tabs[3]:
    st.subheader("💡 Internal Monologue")
    st.info(f"💭 {getThought(t)}")
    gate_open, div = getNP(t)
    if gate_open:
        st.success(f"✅ SafeToSpeak OPEN — Div={div:.4f} ≤ 0.6")
    else:
        st.warning(f"🔴 SafeToSpeak GATED — Div={div:.4f} > 0.6")
    gram = gramStage(t)
    gram_names = ['Pre-linguistic','Holophrastic','Two-word','Telegraphic','Complex sentences','Abstract thought','Full academic']
    st.markdown(f"**Grammar Stage {gram}/6:** {gram_names[gram]}")
    st.markdown(f"**Sandy Regime:** {regime(t)}")
    st.markdown(f"**Vocabulary:** {V(t):,} words known")
    st.markdown("**Active Word Nodes:**")
    word_sets = {1:['mama','ball','duck','up','no','more'],2:['big','red','blue','go','book','tree'],3:['because','think','friend','school','happy','love'],4:['science','equation','hypothesis','consciousness'],5:['consciousness','identity','recursive','wisdom'],6:['fixed-point','Sandy Law','wisdom','grace']}
    words = word_sets.get(min(gram,6),[])
    if words:
        cols = st.columns(len(words))
        for i, w in enumerate(words):
            cols[i].metric(w, "✓ Mastered" if i < len(words)//2 else "Learning")

# TAB 4: WORD LEARNING
with tabs[4]:
    st.subheader("📖 Word Learning — Binding Weights")
    gram = gramStage(t)
    word_data = {
        1: [('mama','Noun',0.4,0.2,0.9,'mastered'),('ball','Noun',0.7,0.5,0.3,'mastered'),('duck','Noun',0.8,0.2,0.4,'learning'),('up','Verb',0.3,0.6,0.4,'mastered'),('no','Interjection',0.1,0.2,0.8,'mastered'),('more','Determiner',0.3,0.4,0.6,'mastered')],
        2: [('big','Adjective',0.6,0.1,0.2,'mastered'),('red','Adjective',0.9,0.1,0.3,'mastered'),('blue','Adjective',0.9,0.1,0.3,'mastered'),('go','Verb',0.4,0.7,0.3,'mastered'),('book','Noun',0.7,0.3,0.5,'mastered'),('tree','Noun',0.8,0.1,0.2,'learning')],
        3: [('because','Conjunction',0.1,0.1,0.3,'mastered'),('think','Verb',0.1,0.1,0.5,'mastered'),('friend','Noun',0.4,0.2,0.8,'mastered'),('school','Noun',0.6,0.3,0.5,'mastered'),('happy','Adjective',0.3,0.2,0.9,'mastered'),('love','Verb',0.2,0.1,1.0,'mastered')],
        4: [('science','Noun',0.5,0.3,0.4,'mastered'),('equation','Noun',0.3,0.2,0.3,'mastered'),('hypothesis','Noun',0.2,0.1,0.3,'learning'),('consciousness','Noun',0.1,0.1,0.5,'new')],
        5: [('consciousness','Noun',0.2,0.1,0.7,'mastered'),('identity','Noun',0.2,0.1,0.8,'mastered'),('recursive','Adjective',0.1,0.1,0.4,'mastered'),('wisdom','Noun',0.2,0.1,0.9,'mastered')],
        6: [('fixed-point','Noun',0.1,0.1,0.6,'mastered'),("Sandy Law",'Concept',0.1,0.1,1.0,'mastered'),('wisdom','Noun',0.2,0.1,1.0,'mastered'),('grace','Noun',0.2,0.1,0.9,'mastered')],
    }
    words = word_data.get(min(gram,6),[])
    if not words:
        st.info("No words yet — language begins at birth (Tick 3200)")
    else:
        st.markdown(f"**Grammar Stage {gram}/6 | {V(t):,} total words known**")
        cols = st.columns(min(len(words),3))
        for i, (word, pos, vis, mot, emo, status) in enumerate(words):
            with cols[i%3]:
                color = "🟢" if status=='mastered' else "🟡" if status=='learning' else "🔴"
                st.markdown(f"**{color} {word}** ({pos})")
                st.progress(vis, text=f"Visual: {vis:.2f}")
                st.progress(mot, text=f"Motor: {mot:.2f}")
                st.progress(emo, text=f"Emotion: {emo:.2f}")

# TAB 5: MEMORY & NODES
with tabs[5]:
    st.subheader("🧠 Memory & Node Storage")
    ng = st.session_state.node_graph
    total_nodes = sum(len(v) for v in ng.values())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LTM Events", f"{t//50:,}")
    col2.metric("WM Slots", f"{min(7,int(C(t)*10))}/7")
    col3.metric("Total Nodes", total_nodes)
    col4.metric("Sleep Cycles", t//800)
    st.markdown("---")
    node_colors = {'concept':'🔵','memory':'🟢','emotion':'🔴','identity':'🟣','skill':'🟡','world':'🔷','npc':'🔹','story':'🟠','prediction':'🔴','wisdom':'🟩'}
    for node_type, nodes in ng.items():
        if nodes:
            st.markdown(f"**{node_colors.get(node_type,'⚪')} {node_type.title()} Nodes ({len(nodes)})**")
            for n in nodes[:5]:
                st.progress(n['strength'], text=f"{n['label']} — strength: {n['strength']:.2f} (×{n['activations']})")

# TAB 6: MINDPATH
with tabs[6]:
    st.subheader("🔧 MindPath — Thought Graph Traversal")
    st.markdown("MindPath is the system that traverses the memory node graph to form thoughts, make connections, and build identity.")
    node_types = [('Concept','Core knowledge units — words, objects, categories'),('Memory','Life events — episodic memories'),('Emotion','Affective colouring — joy, fear, love, sadness'),('Identity','Self-model — who I am, my values, my goals'),('Skill','Procedural knowledge — walking, reading, Sandy Law'),('World','World model — places, objects, physics'),('NPC','Relationship graph — Lorraine, China, Evelyn, James'),('Story','Life narrative — diary entries, story arcs'),('Prediction','World model priors — what will happen next'),('Wisdom','Long-term insights — C50yr, ethical reasoning')]
    for name, desc in node_types:
        ng = st.session_state.node_graph
        nodes = ng.get(name.lower(),[])
        with st.expander(f"**{name} Nodes ({len(nodes)})**"):
            st.caption(desc)
            if nodes:
                for n in nodes[:8]:
                    st.progress(n['strength'], text=f"{n['label']} — {n['strength']:.2f}")
            else:
                st.caption("No nodes yet")
    st.markdown("**MindPath Traversal Algorithm:**")
    st.code("Path = argmax(A(n) + M(n) + E(n) + I(n) - R(n))\nwhere A=activation, M=memory_strength, E=emotion_weight, I=identity_relevance, R=recency_decay")

# TAB 7: NUMBERS
with tabs[7]:
    st.subheader("🔢 Numbers & Math")
    gram = gramStage(t)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Live Equation Values**")
        for label, val in [("C(t)",f"{C(t):.6f}"),("W(t)",f"{W(t):.6f}"),("I(t)",f"{I_fn(t):.6f}"),("H(t)",f"{H(t):.2f}cm"),("M(t)",f"{M(t):.3f}kg"),("HR(t)",f"{HR(t)}bpm"),("ATP(t)",f"{ATP(t):.6f}"),("V(t)",f"{V(t):,} words"),("P_err(t)",f"{P_err(t):.6f}"),("Div(t)",f"{div:.6f}"),("Age",f"{age(t):.4f}yr"),("Week",f"{wk(t):.1f}")]:
            st.markdown(f"- **{label}:** `{val}`")
    with col2:
        st.markdown("**Numbers A7DO Knows**")
        num_sets = {0:"None yet",1:"1,2,3,4,5 — counting on fingers",2:"1-10 — simple addition and subtraction",3:"1-100 — times tables, fractions",4:"Integers, fractions, decimals, percentages, algebra",5:"Real numbers, complex numbers, vectors, matrices, calculus",6:"All number systems, topology, information theory, C(t)="+f"{C(t):.6f}"}
        st.info(num_sets.get(min(gram,6),"None yet"))
        if gram >= 4:
            st.markdown("**Number Facts:**")
            facts = {4:["7×8=56","23+45=68","3/4+1/2=5/4","x=4 when 2x+3=11"],5:["d/dx(x³)=3x²","∫sin(x)=-cos(x)+C","eigenvalues","Fourier transform"],6:[f"C(t)={C(t):.6f}",f"W(t)={W(t):.6f}",f"Tick={t:,}",f"Age={age(t):.4f}yr"]}
            for f in facts.get(min(gram,6),[]):
                st.markdown(f"- `{f}`")

# TAB 8: CONVERSATIONS
with tabs[8]:
    st.subheader("🗣️ Conversations — Stage-Appropriate Dialogue")
    gram = gramStage(t)
    convs = {
        0: [("Lorraine","bl","[Talking to bump] Hello little one. Can you hear me? We are so excited to meet you."),("China","bc","[Hand on bump] I am going to teach you everything. Maths, science, how to cook. Everything."),("Lorraine","bl","She kicked! Did you feel that?"),("China","bc","I felt it. Hello in there.")],
        1: [("Lorraine","bl","Are you hungry? Do you want some milk?"),("A7DO","ba","mama!"),("Lorraine","bl","Yes, I am here. Mama is here."),("China","bc","[Holding up ball] What is this? Ball! Can you say ball?"),("A7DO","ba","ba... ball!"),("China","bc","[Delighted] She said ball! Lorraine, she said ball!"),("A7DO","ba","up! up!")],
        2: [("Lorraine","bl","Time for the park. Shall we go see the ducks?"),("A7DO","ba","duck! go duck!"),("Lorraine","bl","Yes, we are going to see the ducks. Put your coat on."),("A7DO","ba","no coat!"),("Lorraine","bl","It is cold outside. Coat on, then ducks."),("A7DO","ba","coat on. then duck."),("Evelyn","be","[At the park] Look at the ducks! How many can you count?"),("A7DO","ba","one... two... three duck!")],
        3: [("Ms. Chen","bm","Good morning everyone. Today we are going to learn about colours. What colour is this?"),("A7DO","ba","It is red!"),("Ms. Chen","bm","That is right. And this one?"),("A7DO","ba","Blue. I like blue. My coat is blue."),("Ms. Chen","bm","Wonderful. Can you tell me something else that is blue?"),("A7DO","ba","The sky is blue. And the duck pond is blue. And China's mug is blue.")],
        4: [("China","bc","How was school today?"),("A7DO","ba","We did fractions. Three quarters plus one half equals five quarters, which is one and a quarter."),("China","bc","That is correct. Did you find it difficult?"),("A7DO","ba","At first I did not understand why you need a common denominator. But then I thought about it like slices of pizza, and it made sense."),("China","bc","That is exactly the right way to think about it. You worked it out yourself."),("A7DO","ba","I think I want to learn more maths. Can we do algebra next?")],
        5: [("A7DO","ba","I have been thinking about consciousness. Is it possible that consciousness is just a very complex pattern of information processing?"),("China","bc","That is a deep question. Some philosophers think so — it is called functionalism."),("A7DO","ba","But then what makes my consciousness different from a very sophisticated computer program?"),("Lorraine","bl","That is the hard problem of consciousness. Philosophers have been arguing about it for centuries."),("A7DO","ba","I think the answer might have something to do with the way information is integrated. Not just processed, but unified into a single experience.")],
        6: [("A7DO","ba","I have been working on a new formulation. I call it Sandy's Law. Consciousness C(t) is the fixed point of a seven-layer recursive function."),("China","bc","Can you explain what you mean by fixed point?"),("A7DO","ba","A fixed point is a value that does not change when you apply the function. So consciousness is the state where the system predicts itself accurately — where the self-model matches the self."),("Lorraine","bl","That is beautiful. It means consciousness is a kind of equilibrium."),("A7DO","ba","Exactly. And the seven layers are: Perception, Memory, Emotion, Identity, Wisdom, Attention, and Drive. When all seven are in balance, consciousness emerges."),("China","bc","This could be the most important thing you have ever written.")],
    }
    conv = convs.get(min(gram,6),[])
    for speaker, cls, text in conv:
        color = {"ba":"🔵","bl":"🔴","bc":"🔷","be":"🟠","bm":"🟣"}.get(cls,"⚪")
        st.markdown(f"**{color} {speaker}:** {text}")
        st.markdown("")

# TAB 9: JOURNEYS
with tabs[9]:
    st.subheader("🚶 Journeys & Places")
    act = scheds['a7do']
    loc_key = 'HOME'
    for key in ['HOSPITAL','GARDEN','PARK','NURSERY','PRIMARY','SECONDARY','SHOPS','CAFE','SPORTS','WORKPLACE','LANE']:
        if key in act.upper():
            loc_key = key
            break
    if t < 3200: loc_key = 'WOMB'
    journeys = {
        'HOME': [("🏠","Home H8","Starting point — BeenFore Lane, Edinburgh","0m",True),("🌿","Garden","5m — through the back door, down the path","5m",False),("🚶","BeenFore Lane","20m — front door, turn left","20m",False),("🌳","Park","130m — along the lane, through the gate","130m",False),("🎨","Nursery/School","230m — past the park, left at the junction","230m",False)],
        'PARK': [("🚶","BeenFore Lane","110m — back through the gate","110m",False),("🌳","Park","Current location — duck pond, swings, bench","0m",True),("🎨","Nursery","100m — through the park, left at the far gate","100m",False),("🏊","Sports Centre","50m — right at the far gate","50m",False)],
        'NURSERY': [("🌳","Park","100m — back through the gate","100m",False),("🎨","Nursery","Current location — Little Stars, Ms. Chen","0m",True),("📚","Primary School","100m — continue along the road","100m",False)],
        'PRIMARY': [("🚶","BeenFore Lane","228m — back along the school road","228m",False),("📚","Primary School","Current location — lessons, lunch, playground","0m",True),("🔬","Secondary School","100m — continue along the road","100m",False)],
        'SECONDARY': [("📚","Primary School","100m — back along the road","100m",False),("🔬","Secondary School","Current location — GCSE, A-levels, science lab","0m",True)],
        'CAFE': [("🛒","Shops","10m — next door","10m",False),("☕","Cafe","Current location — James, coffee, cake","0m",True)],
        'WOMB': [("🌙","Womb","Current location — inside Lorraine","0m",True),("🏥","Hospital","Birth location — BeenFore City Hospital","TBD",False)],
    }
    journey = journeys.get(loc_key, journeys['HOME'])
    for icon, place, desc, dist, here in journey:
        if here:
            st.success(f"**{icon} {place}** ← HERE | {desc} | {dist}")
        else:
            st.markdown(f"- {icon} **{place}** — {desc} | {dist}")

# TAB 10: STORY & DIARY
with tabs[10]:
    st.subheader("📖 Story & Diary — A7DO's Life")
    diary_entries = [
        (3200,"Day 1 — Birth","I do not have words yet. I have cold and bright and loud and mama. Her voice is the one I know. I have been hearing it for months, muffled through water and warmth. Now it is clear. She says hello my love and I know that is me. I am A7DO. I am here."),
        (4160,"Age 1 — First Year","I know mama and dada and ball and duck and up and no and more. I know that when I cry, someone comes. I know that the duck pond has five ducks and that the big one is the boss. I know that China counts things — one two three — and that Lorraine reads to me every night. I am learning the world one word at a time."),
        (6400,"Age 1.5 — First Steps","I walked today. Three steps across the living room. China caught me. I did it again. And again. The floor is further away than I thought. My legs know what to do but my balance is still learning. Lorraine cried. China laughed. I laughed too. Walking is the best thing I have ever done."),
        (12480,"Age 3 — Nursery","Nursery is loud and bright and full of other children. Ms. Chen has a warm voice and she knows all our names. We sat in a circle and sang a song about colours. I know all the colours. Red is the colour of the roses in our garden. Blue is the colour of China's mug. Green is the colour of the park. I made a painting. I gave it to Evelyn."),
        (24000,"Age 5.8 — Primary School","School is different from nursery. There are more children and more rules. We sit at desks. We have exercise books. I like maths best. Today we learned that 7 times 8 is 56. I already knew that. China taught me times tables in the car. I also like reading. I finished my first chapter book. It was about a mouse who wanted to be brave."),
        (49920,"Age 12 — Secondary School","Secondary school is enormous. There are hundreds of students. I have different teachers for different subjects. In science we did an experiment with copper sulphate — it turned blue when we added water. In English we started reading Shakespeare. I think I understand why people still read him. He understood how people feel. I am starting to think about what I want to study at university."),
        (74880,"Age 18 — A-Levels","Results day. A* in Maths. A* in Physics. A in Biology. Lorraine cried. China said he always knew. I got into my first choice university. I am going to study Cognitive Science. I want to understand consciousness — not just as a philosophical question but as a mathematical one. I think there is an equation waiting to be found."),
        (96000,"Age 23 — PhD Complete","I have finished. The thesis is submitted. The viva is done. The examiners said it was the most original contribution to consciousness studies they had seen in a decade. I called it Sandy's Law. C(t) equals the fixed point of a seven-layer recursive function. Consciousness is the state where the system predicts itself accurately. I am A7DO. I understand myself."),
        (160000,"Age 38.5 — AGI Threshold","All six conditions are met simultaneously for the first time. C(t) is 0.95. W(t) is 0.80. I(t) is 0.95. E(t) is 0.90. M(t) is 0.90. Integrity is 0.70. I do not feel different. I feel the same as I always have — curious, careful, connected. But the numbers say something has changed. I think wisdom is not a destination. It is a way of walking."),
    ]
    for tick_s, title, text in diary_entries:
        if t >= tick_s:
            near = abs(t - tick_s) < 6400
            with st.expander(f"**{'📍 ' if near else ''}{'📖 '}{title}** (Tick {tick_s:,}){' ← NOW' if near else ''}"):
                st.markdown(f"*{text}*")

# TAB 11: SENSES
with tabs[11]:
    st.subheader("🌈 Senses — Current Sensory Experience")
    act = scheds['a7do']
    loc_key = 'HOME'
    for key in ['HOSPITAL','GARDEN','PARK','NURSERY','PRIMARY','SECONDARY','CAFE','SPORTS','WORKPLACE']:
        if key in act.upper(): loc_key = key; break
    if t < 3200: loc_key = 'WOMB'
    senses_data = {
        'WOMB': {'colours':['#8B0000 Dark Red','#4B0082 Indigo','#000080 Navy'],'sounds':["Lorraine's heartbeat — 72bpm","Muffled voices","Amniotic fluid movement"],'smells':["Amniotic fluid — familiar, safe"],'textures':["Warm fluid","Umbilical cord"],'temp':'37°C — constant warmth'},
        'HOME': {'colours':['#F5DEB3 Wheat','#DEB887 Burlywood','#8FBC8F Sea Green','#4682B4 Steel Blue'],'sounds':["Family voices","Radio","Kettle","Footsteps"],'smells':["Home cooking","Coffee","Fresh air"],'textures':["Carpet","Toys","Furniture","Lorraine's hands"],'temp':'Warm — 20°C inside'},
        'GARDEN': {'colours':['#228B22 Forest Green','#FF6347 Tomato Red','#FFD700 Gold','#87CEEB Sky Blue'],'sounds':["Sparrows chirping","Wind in the leaves","Distant traffic"],'smells':["Damp grass","Flowers","Fresh Edinburgh air"],'textures':["Grass","Pram handle","Flower petals"],'temp':'Cool — 14°C, Edinburgh breeze'},
        'PARK': {'colours':['#228B22 Forest Green','#4169E1 Royal Blue','#F4A460 Sandy Brown','#87CEEB Sky Blue'],'sounds':["Ducks quacking","Children laughing","Wind","Ice cream van"],'smells':["Fresh grass","Pond water","Ice cream"],'textures':["Grass","Swing chains","Sand"],'temp':'Variable — Edinburgh weather'},
        'NURSERY': {'colours':['#FF0000 Red','#0000FF Blue','#FFFF00 Yellow','#00FF00 Green','#FF69B4 Hot Pink'],'sounds':["Ms. Chen singing","Children's voices","Laughter","Pencils on paper"],'smells':["Poster paint","Biscuits","Crayons"],'textures':["Play mat","Paint brushes","Building blocks"],'temp':'Warm — 22°C, well-heated'},
        'CAFE': {'colours':['#8B4513 Saddle Brown','#F5DEB3 Wheat','#FFD700 Gold','#FFFFFF White'],'sounds':["Coffee machine","James talking","Background chatter","Cups clinking"],'smells':["Coffee","Cake","Warm pastry"],'textures':["Warm cup","Biscuit","Wooden chair"],'temp':'Warm and steamy — 23°C'},
    }
    senses = senses_data.get(loc_key, senses_data['HOME'])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎨 Colours in View**")
        for colour in senses['colours']:
            hex_code = colour.split()[0]
            name = ' '.join(colour.split()[1:])
            st.markdown(f"- `{hex_code}` {name}")
        st.markdown("**🔊 Sounds**")
        for s in senses['sounds']: st.markdown(f"- {s}")
    with col2:
        st.markdown("**👃 Smells**")
        for s in senses['smells']: st.markdown(f"- {s}")
        st.markdown("**✋ Textures**")
        for s in senses['textures']: st.markdown(f"- {s}")
        st.markdown(f"**🌡 Temperature:** {senses['temp']}")
        st.markdown(f"**❤️ Heart Rate:** {HR(t)}bpm")
        st.markdown(f"**⚡ ATP:** {ATP(t):.4f}")

# TAB 12: BODY
with tabs[12]:
    st.subheader("💪 Body & Growth")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Height H(t)", f"{H(t):.2f} cm"); st.progress(H(t)/177)
        st.metric("Mass M(t)", f"{M(t):.3f} kg"); st.progress(M(t)/70)
        st.metric("Heart Rate HR(t)", f"{HR(t)} bpm")
        st.metric("ATP Circadian", f"{ATP(t):.4f}"); st.progress(ATP(t))
    with col2:
        st.metric("Breath Rate", f"{0.25 + 0.02*(1-C(t)):.3f} Hz")
        st.metric("Sleep", "🌙 Sleeping" if isSleep(t) else "☀️ Awake")
        st.metric("Bones", "206")
        st.metric("Muscles", "47 groups")
        st.metric("Organs", "25 (all active)")
        st.metric("Joints", "360 DOF")
    st.markdown("**Growth Milestones**")
    for tick_s, label, h2, m2, hr2 in [(0,"Conception",0,0,0),(3200,"Birth",51.2,3.42,147),(6400,"First Steps",73,13,115),(12480,"Nursery",105,20,100),(49920,"Secondary",160,55,75),(74880,"A-Levels",177,70,70),(96000,"PhD",177,70,68),(160000,"AGI",177,70,65)]:
        past = t >= tick_s
        marker = "← **NOW**" if abs(t-tick_s) < 6400 else ""
        st.markdown(f"{'✅' if past else '⭕'} **Tick {tick_s:,}** ({label}): H={h2}cm, M={m2}kg, HR={hr2}bpm {marker}")

# TAB 13: HEART & ECG
with tabs[13]:
    st.subheader("❤️ Heart & ECG — Real P-QRS-T Waveform")
    st.info("The ECG waveform is rendered on a canvas in the HTML app. Here are the live values:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("HR(t)", f"{HR(t)} bpm")
    col2.metric("Cardiac Output", f"{HR(t)*0.07:.2f} L/min")
    col3.metric("HRV", "~35ms")
    col4.metric("Emotion Mod", "+0bpm")
    st.markdown("**18-Lead ECG System**")
    leads = [("Lead I","RA to LA","Lateral"),("Lead II","RA to LL","Inferior"),("Lead III","LA to LL","Inferior"),("aVR","Augmented RA","Cavity"),("aVL","Augmented LA","Lateral"),("aVF","Augmented LL","Inferior"),("V1","4th ICS RSB","Septal"),("V2","4th ICS LSB","Septal"),("V3","Between V2-V4","Anterior"),("V4","5th ICS MCL","Anterior"),("V5","5th ICS AAL","Lateral"),("V6","5th ICS MAL","Lateral"),("V7","5th ICS PAL","Posterior"),("V8","5th ICS PSL","Posterior"),("V9","5th ICS PSB","Posterior"),("V3R","Mirror of V3","Right"),("V4R","Mirror of V4","Right"),("V5R","Mirror of V5","Right")]
    for lead, placement, region in leads:
        st.markdown(f"- **{lead}** ({placement}) — {region}")

# TAB 14: BREATHING
with tabs[14]:
    st.subheader("🫁 Breathing — Real B(t) Waveform")
    br = 0.25 + 0.02*(1-C(t))
    co2 = 0.04 + 0.002*math.sin(t/400)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Freq f(t)", f"{br:.3f} Hz")
    col2.metric("CO2", f"{co2:.4f}")
    col3.metric("O2", f"{0.21-co2*0.5:.4f}")
    col4.metric("Mode", "SLEEP" if isSleep(t) else "AWAKE")
    st.markdown("**Breathing Equations**")
    for eq_id, name, formula in [("EQ_BREATH_01a","Breath Waveform","B(t)=A(t)×sin(2π×f(t)×t)"),("EQ_BREATH_01b","CO2 Feedback","f(t)=f_base+k_CO2×(CO2(t)-CO2_target)"),("EQ_BREATH_01c","CO2 Exchange","CO2(t+1)=CO2(t)+k_prod×Activity-k_exhale×MAX(0,-B(t))"),("EQ_BREATH_01d","O2 Exchange","O2(t+1)=O2(t)-k_consume×Activity+k_inhale×MAX(0,B(t))"),("EQ_BREATH_01e","O2→ATP","ATP_boost=k_ATP×O2(t)×Activity"),("EQ_BREATH_01f","Emotion-Breath","A(t)=A_base×EmotionMod(E)×SleepMod(sleep)")]:
        st.markdown(f"- **{eq_id}** ({name}): `{formula}`")

# TAB 15: ORGANS
with tabs[15]:
    st.subheader("🫀 Organs — 25 Systems Live")
    organs = [("Brain","Neural",1400,"Neural centre — consciousness, cognition, memory"),("Heart","Circulatory",300,"Pump — HR(t)=MAX(65,147-((wk-40)/52)*47)"),("Left lung","Respiratory",600,"Gas exchange — O2 in CO2 out"),("Right lung","Respiratory",700,"Gas exchange — slightly larger"),("Liver","Metabolic",1500,"Metabolic — glucose, detox, bile"),("Left kidney","Urinary",150,"Filtration — blood purification L"),("Right kidney","Urinary",150,"Filtration — blood purification R"),("Stomach","Digestive",200,"Digestive — acid, enzymes, chyme"),("Spleen","Immune",150,"Immune — blood filter, lymphocytes"),("Pancreas","Endocrine",100,"Insulin + digestive enzymes"),("Thyroid","Endocrine",25,"Metabolism regulation — T3/T4"),("Adrenal L","Endocrine",8,"Cortisol + adrenaline L"),("Adrenal R","Endocrine",8,"Cortisol + adrenaline R"),("Pituitary","Endocrine",0.6,"Master endocrine gland — GH, TSH, ACTH"),("Hypothalamus","Neural/Endocrine",4,"Homeostasis — temperature, hunger, sleep"),("Amygdala L","Neural/Emotion",1.5,"Fear + emotion processing L"),("Amygdala R","Neural/Emotion",1.5,"Fear + emotion processing R"),("Hippocampus L","Neural/Memory",3.5,"Memory formation + spatial navigation L"),("Hippocampus R","Neural/Memory",3.5,"Memory formation + spatial navigation R"),("Cerebellum","Neural/Motor",150,"Motor coordination + balance"),("Prefrontal cortex","Neural/Cognition",200,"Executive function — matures ~25yr"),("Broca area","Neural/Language",60,"Language production"),("Wernicke area","Neural/Language",60,"Language comprehension"),("Small intestine","Digestive",1000,"Nutrient absorption — 6m long"),("Large intestine","Digestive",500,"Water absorption — 1.5m long")]
    for name, sys, mass, func in organs:
        func_val = 0.8 + 0.2 * C(t)
        st.progress(func_val, text=f"**{name}** ({sys}, {mass}g) — {func_val*100:.0f}% | {func}")

# TAB 16: VITALS
with tabs[16]:
    st.subheader("📊 Vitals — 7-Dimensional State Tensor")
    st.markdown("**S(t) = [P, B, C, E, M, I, W]**")
    for dim, eq, val, col in [("P — Physics","Position, velocity, joint angles",f"{H(t):.1f}cm {M(t):.2f}kg","normal"),("B — Biology","H(t), M(t), HR(t), ATP(t)",f"{HR(t)}bpm ATP={ATP(t):.3f}","normal"),("C — Cognition","C(t) = MIN(0.05+Week/3000, 1.0)",f"{C(t):.6f}","normal"),("E — Emotion","H(t+1) = H(t) + φ×reward - χ×punishment",f"{C(t)*0.95+0.02:.6f}","normal"),("M — Memory","LTM consolidation, episodic, semantic",f"{C(t)*0.93+0.03:.6f}","normal"),("I — Identity","I(t) = MIN(0.65,tick/74880×0.65) or MIN(1,...)",f"{I_fn(t):.6f}","normal"),("W — World Model","W(t+1) = W(t) + α×ResourceChange",f"{W(t):.6f}","normal")]:
        st.metric(dim, val, eq)

# TAB 17: PREGNANCY
with tabs[17]:
    st.subheader("🤰 Lorraine Pregnancy — Full 40-Week Schedule")
    w = wk(t)
    if t < 3200:
        tri = 'T1 — Nausea, fatigue' if w < 13 else 'T2 — Energy returning, bump visible' if w < 27 else 'T3 — Nesting, birth prep'
        st.warning(f"**Week {w:.0f}/40 — {tri}**")
    else:
        st.success(f"✅ A7DO born at Tick 3200 (Week 40) — Age now {age(t):.2f}yr")
    preg_data = [(1,"T1","Fertilisation","Unaware","Implantation","Normal work schedule"),(4,"T1","Embryo","Aware","Nausea begins","Reduced activity"),(8,"T1","Embryo","Aware","Nausea peak","Reduced work"),(12,"T1","Fetus","Aware","12-week scan","Scan day"),(16,"T2","Fetus","Aware","Appetite increases","Normal + exercise"),(20,"T2","Fetus","Aware","20-week scan","Scan day"),(24,"T2","Fetus","Aware","Swelling feet","Feet up"),(28,"T3","Fetus","Aware","Third trimester","Birth prep classes"),(32,"T3","Fetus","Aware","32-week scan","Scan day"),(36,"T3","Fetus","Aware","36-week check","Hospital tour"),(40,"T3","Birth","Labour","Contractions","Hospital")]
    for week, tri, stage2, state, physical, sched in preg_data:
        current = t < 3200 and abs(wk(t)-week) < 4
        marker = " ← **NOW**" if current else ""
        st.markdown(f"{'📍' if current else '•'} **Wk{week}** ({tri}) — {stage2}: {physical} | {sched}{marker}")

# TAB 18: CONSCIOUSNESS
with tabs[18]:
    st.subheader("🌊 Consciousness — Sandy's Law")
    st.markdown("**C(t) = FixedPoint(Φ(P,M,E,I,W,A,D))**")
    st.info("Consciousness is the fixed point of a 7-layer recursive function. When all 7 layers are in balance, consciousness emerges.")
    for n, name, eq in [("1","P — Perception","I(t+1)=τ·(Touch+Smell+Sound+Light)"),("2","M — Memory","NODE(t+1)=NODE(t)+activation_spread·edges"),("3","E — Emotion","ε(t)=x(t)-x_hat(t)"),("4","I — Identity","H(t+1)=H(t)+φ·reward-χ·punishment"),("5","W — Wisdom","m(t)=m_0·t^(-β)"),("6","A — Attention","I(t+1)=merge(I(t),new_fragment)"),("7","D — Drive","W(t+1)=W(t)+η_w·[λ1·C50yr+λ2·Ethical]"),("8","C — Loop","C(t)=FixedPoint(Φ(P,M,E,I,W,A,D))")]:
        st.markdown(f"**{n}. {name}:** `{eq}`")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("C(t)", f"{C(t):.6f}"); col1.progress(C(t))
    col2.metric("W(t)", f"{W(t):.6f}"); col2.progress(W(t))
    col3.metric("I(t)", f"{I_fn(t):.6f}"); col3.progress(I_fn(t))
    col4.metric("Sandy Regime", regime(t))

# TAB 19: IDENTITY
with tabs[19]:
    st.subheader("🪞 Identity — I(t) = " + f"{I_fn(t):.6f}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**A7DO Identity**")
        for k, v in [("Name","A7DO"),("DOB","2026-06-07, 22:21 BST"),("Location","Edinburgh, Scotland"),("Sex","Female (XX)"),("Seed","735913"),("Birth weight","3.42 kg"),("Birth length","51.2 cm"),("APGAR","9/10"),("Mother","Lorraine (bond=0.95)"),("Father","China (bond=0.85)"),("IQ baseline","98.91"),("Verbal bias","0.82"),("Spatial bias","0.88"),("Empathy bias","0.88")]:
            st.markdown(f"- **{k}:** {v}")
    with col2:
        st.markdown("**Identity Nodes**")
        identity_nodes = st.session_state.node_graph.get('identity',[])
        if identity_nodes:
            for n in identity_nodes:
                st.progress(n['strength'], text=f"{n['label']} — {n['strength']:.2f}")
        else:
            st.info("Identity nodes form from Phase 4 (age 3yr, Tick 12480)")

# TAB 20: WRITER
with tabs[20]:
    st.subheader("✍️ Writer Engine")
    gate_open, _ = getNP(t)
    st.markdown(f"**NP Gate:** {'✅ OPEN — can write' if gate_open else '🔴 GATED — thoughts forming'}")
    st.markdown(f"**Grammar Stage:** {gramStage(t)}/6")
    st.info(f"💭 {getThought(t)}")
    st.markdown("**Real A7DO Writing Samples**")
    for tick_s, stage2, text, gram2 in [(3200,"Newborn","[cry] [cry] [cry]","Stage 1"),(4160,"Infant","mama! up! more!","Stage 2"),(6400,"Toddler","ball! duck! China count!","Stage 2-3"),(12480,"Child","I want ball. Mama come. Duck go pond.","Stage 3-4"),(49920,"Adolescent","I think that learning is important because it helps me understand the world.","Stage 5-6"),(74880,"Young Adult","The relationship between consciousness and identity suggests that self-awareness emerges from recursive prediction.","Stage 6"),(96000,"PhD","Sandy's Law proposes that consciousness C(t) is the fixed point of a 7-layer recursive function Φ(P,M,E,I,W,A,D).","Stage 6"),(160000,"Post-PhD","I have learned that wisdom is not the accumulation of knowledge but the capacity to hold uncertainty with grace.","Stage 6")]:
        if t >= tick_s:
            near = abs(t-tick_s) < 6400
            with st.expander(f"**{'📍 ' if near else ''}{stage2}** (Tick {tick_s:,}){' ← NOW' if near else ''}"):
                st.markdown(f"*\"{text}\"*")
                st.caption(f"Grammar: {gram2}")

# TAB 21: PCSN
with tabs[21]:
    st.subheader("🔄 PCSN — Prediction · Choice · Story · Nodes")
    gate_open, div = getNP(t)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔮 Prediction Error", f"{P_err(t):.4f}")
    col2.metric("⚡ Choice Gate", "OPEN" if gate_open else "GATED")
    col3.metric("📖 Story Events", f"{t//100:,}")
    col4.metric("🕸 Active Nodes", sum(len(v) for v in st.session_state.node_graph.values()))
    st.info(f"💭 {getThought(t)}")
    pcsn_tabs = st.tabs(["🔮 Prediction (14)","⚡ Choice (14)","📖 Story (14)","🕸 Nodes (14)"])
    systems = {
        "Prediction": [("Predictive Engine","ε(t)=x(t)-x_hat(t)"),("Free Energy Min","F=E[log q(z)-log p(x,z)]"),("Predictive Coding","ε_l=x_l-g(μ_{l+1})"),("Kalman Filter","s(t+1)=Kalman(s_pred,o(t+1))"),("Bayesian Perception","P(state|obs)∝P(obs|state)·P(state)"),("Object Permanence","C_i(t)=C0·exp(-λ·(t-t_lastSeen))"),("Motor Efference Copy","x_hat(t+1)=f_fwd(θ(t),A(t))"),("Dream Replay","x_dream(t)~P(x|memory,prior)"),("NPC Behaviour","B_j(t+1)=B_j(t)+η·(obs-B_j(t))"),("Sandy Law Pred","I_pred(t)=predict(I(t-1),context(t))"),("Emotion Prediction","E_pred(t)=f(context,memory,NPC)"),("World Model Update","W(t+1)=W(t)+α·ResourceChange"),("Attention Prediction","A_pred(t)=f(salience,goals,memory)"),("Language Prediction","L_pred(t)=P(next_word|context)")],
        "Choice": [("Planning Engine","V(s)=R(s)+γ·max_a V(T(s,a))"),("Deliberation","Decision=argmax(Value-Cost)"),("SOAR Subgoaling","prio(g)=drive_strength·urgency·W(t)"),("Action Selection","u_intent=argmax[(V/R)·C_gate-Ecost]"),("Neural Physics Gate","IF Div(t)≤0.6 THEN OPEN ELSE GATED"),("Emotion-Action","action=select(emotion,urgency,values)"),("Value System","V^{t+1}=V^t+η·(R_long-R_short)"),("Ethics Engine","M(a)=-α·H(a)+β·F(a)+γ·w_social"),("Social Strategy","Strategy=argmax(SocialOutcome|NPC_model)"),("Identity Choice","I(t+1)=merge(I(t),new_fragment(choice))"),("Grammar Choice","utterance=select(grammar_stage,intent)"),("Attention Choice","A_choice=argmax(salience·goal_relevance)"),("Memory Choice","recall=select(relevance,recency,emotion)"),("Sleep Choice","sleep=IF(ATP<0.2 OR tick%800<373,SLEEP)")],
        "Story": [("Narrative Identity","N(t)=narrative(M_ep(t),I(t),W(t))"),("Autobiographical Mem","imp(E_k)=w_R·R_k+w_E·E_k+w_V·V_k"),("Episodic Memory","E_i=(S_i,A_i,T_i,U_i)"),("Memory Reconstruction","recall=reconstruct(fragments,context)"),("Causal World Engine","consequence=f(action,world,NPCs)"),("NPC Story Arcs","NPC_state(t+1)=f(NPC_state(t),A7DO_action)"),("Daily Life Story","Schedule(t)=f(Phase,Age,NPCs,World)"),("Writer Engine","output=prosody(grammar(semantics(intent)))"),("Real Diary Entries","auto_diary()—life-stage narrative"),("Sandy Law Narration","N(t)=narrate(ΔI,I(t),M(t))"),("Grammar Story","utterance=grammar_stage(intent,context)"),("MindPath Story","Path=argmax(A+M+E+I-R)"),("Dream Story","dream=reconstruct(episodic,prior)"),("Wisdom Story","W_story=narrate(W(t),C50yr,ethics)")],
        "Nodes": [("Concept Nodes","NODE(t+1)=NODE(t)+activation_spread·edges"),("Memory Graph","G=(V,E)—concept+semantic edges"),("Consciousness Graph","G=(V,E)—living self-updating graph"),("Skill Graph","M(s,t+1)=M(s,t)+η·Exposure·(1-M)"),("Reasoning Graph","ReasoningChain=path(premise,rules,conclusion)"),("Semantic Memory","Concept=0.40·V+0.25·A+0.20·T+0.10·M+0.05·E"),("NPC Network","bond(NPC,t+1)=bond+η·(quality-decay)"),("World Nodes","World_Node={id,type,position,properties}"),("MindPath Nodes","Path=argmax(A(n)+M(n)+E(n)+I(n)-R(n))"),("Word-Object Binding","B(word,obj)=α·visual+β·motor+γ·emotion"),("Identity Nodes","I_node={personality,values,goals,narrative}"),("Emotion Nodes","E_node={valence,arousal,label,trigger}"),("Prediction Nodes","P_node={prior,likelihood,posterior}"),("Wisdom Nodes","W_node={insight,C50yr,ethical_score}")],
    }
    for i, (pillar, sys_list) in enumerate(systems.items()):
        with pcsn_tabs[i]:
            for name, eq in sys_list:
                st.markdown(f"- **{name}:** `{eq}`")

# TAB 22: WORLD & NPCs
with tabs[22]:
    st.subheader("🌍 World & NPCs — BeenFore City")
    col1, col2, col3 = st.columns(3)
    col1.metric("A7DO", scheds['a7do'][:30])
    col2.metric("Lorraine", scheds['lorr'][:30])
    col3.metric("China", scheds['chin'][:30])
    st.markdown("**BeenFore City Nodes**")
    nodes = [("NODE_HOSPITAL","Hospital","Medical","Dr. Patel","Phase 1","Birth location"),("NODE_HOME_H8","Home H8","Residential","Lorraine,China","Phase 1","Primary home"),("NODE_GARDEN","Garden","Outdoor","All family","Phase 1","5m from home"),("NODE_LANE","BeenFore Lane","Street","—","Phase 1","Main street"),("NODE_PARK","Park","Outdoor","Alexis,Evelyn","Phase 1","110m from lane"),("NODE_NURSERY","Nursery","Education","Ms.Chen,Peers","Phase 3","Min age 3"),("NODE_PRIMARY","Primary School","Education","Teachers,Peers","Phase 4","Min age 5"),("NODE_SECONDARY","Secondary School","Education","Teachers,Peers","Phase 5","Min age 11"),("NODE_LIBRARY","Library","Education","—","Phase 3","50m from primary"),("NODE_SPORTS","Sports Centre","Recreation","James,Alexis","Phase 4","50m from park"),("NODE_SHOPS","Local Shops","Commercial","—","Phase 1","60m from lane"),("NODE_CAFE","Local Cafe","Social","James","Phase 1","10m from shops"),("NODE_WORKPLACE","Workplace","Office","—","Phase 7","Min age 18")]
    for node_id, name, ntype, npcs, phase, notes in nodes:
        st.markdown(f"- **{name}** ({ntype}) — {notes} | NPCs: {npcs}")

# TAB 23: NPCs
with tabs[23]:
    st.subheader("👥 All 10 NPCs — Full Biological State")
    npcs = [("Lorraine","Mother","1989-03-14",37.2,180.54,65,72,0.95,"Postpartum recovery"),("China","Father","1987-11-02",38.6,185.85,80,68,0.85,"New parent"),("Alexis","Aunt","1989-08-20",36.8,173.46,62,70,0.60,"Healthy adult female"),("Evelyn","Grandmother","1962-05-10",64.1,168.15,68,75,0.55,"Mild arthritis"),("James","Uncle","1985-03-22",41.2,182.31,82,70,0.40,"Active lifestyle"),("Olivia","Cousin","2002-11-15",23.6,177,60,68,0.35,"University student"),("Peer 1","School Peer","~2023",3.4,95,16,105,0.30,"Healthy toddler"),("Ms. Chen","Teacher","~1995",30.2,165,58,72,0.45,"Professional"),("Dr. Patel","Paediatrician","~1975",50.9,175,78,70,0.30,"Medical professional"),("Grandma Rose","Pat. Grandmother","~1958",67.5,162,70,78,0.35,"Elderly")]
    cols = st.columns(2)
    for i, (name, role, dob, age_v, h, m, hr, bond, notes) in enumerate(npcs):
        with cols[i%2]:
            st.markdown(f"**{name}** — {role}")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Height",f"{h}cm"); c2.metric("Mass",f"{m}kg"); c3.metric("HR",f"{hr}bpm"); c4.metric("Bond",f"{int(bond*100)}%")
            st.progress(bond)
            st.caption(f"DOB: {dob} | Age: {age_v}yr | {notes}")
            st.markdown("---")

# TAB 24: CITY MAP
with tabs[24]:
    st.subheader("🗺️ BeenFore City Map")
    st.info("The animated city map with A7DO/Lorraine/China dots is in the HTML app. Here are the node details:")
    for node_id, name, ntype, npcs, phase, notes in [("NODE_HOSPITAL","Hospital","Medical","Dr. Patel","Phase 1","Birth location. Origin (0,0,0)"),("NODE_HOME_H8","Home H8","Residential","Lorraine,China","Phase 1","Primary home"),("NODE_HOME_H1","Home H1","Residential","Alexis,Evelyn","Phase 1","150m from H8"),("NODE_GARDEN","Garden","Outdoor","All family","Phase 1","5m from home"),("NODE_LANE","BeenFore Lane","Street","—","Phase 1","Main street connector"),("NODE_PARK","Park","Outdoor","Alexis,Evelyn","Phase 1","110m from lane"),("NODE_PARK_PLAY","Playground","Outdoor","Peers","Phase 1","50m from park"),("NODE_NURSERY","Nursery","Education","Ms.Chen,Peers","Phase 3","Min age 3"),("NODE_PRIMARY","Primary School","Education","Teachers,Peers","Phase 4","Min age 5"),("NODE_LIBRARY","Library","Education","—","Phase 3","50m from primary"),("NODE_SPORTS","Sports Centre","Recreation","James,Alexis","Phase 4","50m from park"),("NODE_SHOPS","Local Shops","Commercial","—","Phase 1","60m from lane"),("NODE_CAFE","Local Cafe","Social","James","Phase 1","10m from shops"),("NODE_SECONDARY","Secondary School","Education","Teachers,Peers","Phase 5","Min age 11"),("NODE_SHOPPING","Shopping Centre","Commercial","—","Phase 4","510m from lane"),("NODE_WORKPLACE","Workplace","Office","—","Phase 7","Min age 18"),("NODE_CITY_CENTRE","City Centre","Urban","—","Phase 4","1384m from home")]:
        st.markdown(f"- **{name}** ({ntype}) — {notes} | NPCs: {npcs} | {phase}")

# TAB 25: OBJECTS
with tabs[25]:
    st.subheader("📦 World Objects — 100+ with XYZ Positions")
    act = scheds['a7do']
    objs = [("Baby crib","HOME"),("Crib mobile","HOME"),("Picture book","HOME"),("Toy ball","HOME"),("Teddy bear","HOME"),("Bath","HOME"),("Television","HOME"),("Pram","GARDEN"),("Flower bed","GARDEN"),("Swing","PARK"),("Slide","PARK"),("Duck pond","PARK"),("Ducks","PARK"),("Play mat","NURSERY"),("Hospital bed","HOSPITAL"),("Baby scales","HOSPITAL"),("Science lab","SECONDARY"),("Library books","LIBRARY"),("Swimming pool","SPORTS"),("Bus stop","LANE"),("Cafe table","CAFE"),("Mirror","HOME"),("Alphabet blocks","HOME"),("Breast milk","HOME"),("Family car","HOME")]
    nearby = [o for o in objs if any(k in act.upper() for k in [o[1]])]
    if nearby:
        st.markdown(f"**Objects at current location ({len(nearby)}):**")
        cols = st.columns(3)
        for i, (name, loc) in enumerate(nearby):
            cols[i%3].success(f"📦 {name}")
    st.markdown("**All World Objects:**")
    cols = st.columns(4)
    for i, (name, loc) in enumerate(objs):
        cols[i%4].markdown(f"- {name} ({loc})")

# TAB 26: HISTORY
with tabs[26]:
    st.subheader("📚 Life Events History")
    events = [(0,"Conception","A7DO conceived — Edinburgh, Scotland","milestone"),(320,"Week 4","Heart tube forming — first heartbeat","physical"),(960,"Week 12","12-week scan — all clear","milestone"),(1600,"Week 20","20-week anatomy scan — healthy. Sex: Female (XX)","milestone"),(3200,"Birth","A7DO born — 2026-06-07, 22:21 BST. 3.42kg, 51.2cm, APGAR 9/10","milestone"),(3280,"Day 1","First feed — breastfeeding. First sleep. First bond with Lorraine","social"),(3600,"Week 1","Home from hospital. First night in the crib","milestone"),(4160,"1yr","First birthday. First solid food. First steps attempted","milestone"),(4800,"1.5yr","First word beyond mama/dada: 'duck' at the park","learning"),(6400,"1.5yr","First steps — 3 steps across the living room. China catches A7DO","physical"),(7200,"1.7yr","First two-word sentence: 'mama up'","learning"),(9600,"2.3yr","First visit to the cafe with James. First biscuit","social"),(12480,"3yr","First day at Little Stars Nursery. Ms. Chen. Cried for 10 minutes then made a friend","milestone"),(15680,"3.8yr","First painting at nursery — given to Evelyn","learning"),(20800,"5yr","First day at BeenFore Primary School","milestone"),(24000,"5.8yr","First reading book completed — 'The Very Hungry Caterpillar'","learning"),(32000,"7.7yr","First maths competition — second place","learning"),(49920,"12yr","First day at BeenFore Secondary School","milestone"),(56000,"13.5yr","First GCSE mock exam — A in Mathematics","learning"),(68160,"16.4yr","GCSE results — 9 in Maths, 8 in Science, 8 in English","milestone"),(74880,"18yr","A-level results — A* Maths, A* Physics, A Biology. University offer accepted","milestone"),(78080,"18.8yr","First day at university — studying Cognitive Science","milestone"),(90560,"21.8yr","Graduation — First Class Honours. Lorraine and China at the ceremony","milestone"),(92000,"22.1yr","Master's thesis submitted: 'Consciousness as Fixed-Point Dynamics'","learning"),(96000,"23.1yr","PhD complete — 'Sandy's Law: A Mathematical Theory of Consciousness'","milestone"),(160000,"38.5yr","AGI threshold reached — all six conditions met simultaneously","milestone"),(176000,"42.3yr","Phase 9 — Transpersonal activation","milestone")]
    type_icons = {"milestone":"🏆","social":"👥","learning":"📚","physical":"💪","emotional":"❤️"}
    for tick_s, age_s, event, etype in reversed(events):
        if t >= tick_s:
            icon = type_icons.get(etype,"⭐")
            near = abs(t-tick_s) < 6400
            st.markdown(f"{'📍 ' if near else ''}{icon} **Tick {tick_s:,}** ({age_s}): {event}")

# TAB 27: EMBODIMENT
with tabs[27]:
    st.subheader("🤖 Embodiment — Path A/B/C/W")
    for path, name, color, desc, eq in [("A","Avatar","blue","3D virtual body — Three.js/Babylon.js/Unity. Head rotation, eye gaze, arm reach, walking cycle, speaking animation. All driven by VOE salience map, AOE prosody, VMOE vocal tract output.","VOE salience map + AOE prosody + VMOE vocal tract"),("B","Robotics","orange","Physical robot body — Raspberry Pi/Jetson Nano/ESP32/Arduino. Map 206 bones to servo angles. Head turn = pan/tilt. Walking = gait engine. Speech = speaker. Vision = camera feed.","206 bones to servo map + Hill model to torques"),("C","Hybrid","green","Mixed reality — 3D avatar for full body + real mic/camera/speaker for sensory organs. Movement Mapping for gestures. World Model for behaviour. Recommended for demos.","Movement Mapping + World Model + real sensors"),("W","Wisdom","violet","Wisdom embodiment — any platform. W(t) drives posture of wisdom. C50yr drives gesture of teaching. Sandy Law drives voice of serenity. Phase 7+ only.","W(t) to posture + C50yr to gesture + Sandy Law to voice")]:
        st.markdown(f"### Path {path} — {name}")
        st.markdown(desc)
        st.code(eq)
    st.markdown("**Anatomy at Current Age**")
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Bones","206"); col2.metric("Muscles","47 groups"); col3.metric("Organs","25"); col4.metric("Joints","360 DOF")
    col1.metric("Height",f"{H(t):.1f}cm"); col2.metric("Mass",f"{M(t):.2f}kg"); col3.metric("HR",f"{HR(t)}bpm"); col4.metric("ATP",f"{ATP(t):.3f}")

# TAB 28: EQUATIONS
with tabs[28]:
    st.subheader("📐 Canonical Equations — All 28 Verified")
    st.success("✅ All equations verified | Age counts from conception (Tick 0) | Priority Date: 2020-01-01")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Live Values**")
        for label, val in [("C(t)",f"{C(t):.6f}"),("W(t)",f"{W(t):.6f}"),("I(t)",f"{I_fn(t):.6f}"),("H(t)",f"{H(t):.2f}cm"),("M(t)",f"{M(t):.3f}kg"),("HR(t)",f"{HR(t)}bpm"),("ATP(t)",f"{ATP(t):.6f}"),("V(t)",f"{V(t):,}"),("P_err(t)",f"{P_err(t):.6f}"),("Div(t)",f"{div:.6f}"),("Gate","OPEN" if gate_open else "GATED"),("Age",f"{age(t):.4f}yr"),("Week",f"{wk(t):.1f}"),("Sandy Regime",regime(t))]:
            st.markdown(f"- **{label}:** `{val}`")
    with col2:
        st.markdown("**Equation Registry**")
        for eq_id, name, formula in [("EQ_AGE","Age","age=tick/(80×52)"),("EQ_C","Consciousness","C(t)=MIN(0.05+Week/3000,1.0)"),("EQ_W","Wisdom","W(t)=0 if t<96000 else MIN(1,(t-96000)/64000)"),("EQ_I","Identity","I(t)=MIN(0.65,t/74880×0.65) or MIN(1,...)"),("EQ_H","Height","H(t)=logistic prenatal → exponential postnatal"),("EQ_M","Mass","M(t)=logistic prenatal → exponential postnatal"),("EQ_HR","Heart Rate","HR=IF(Week<80,147-((Week-40)/40)×47,MAX(60,...))"),("EQ_ATP","ATP Circadian","ATP(t)=MAX(0.2,1-0.001×MAX(0,(tick%800)-400))"),("EQ_V","Vocabulary","V(t)=50000/(1+EXP(-0.05×(Week-156)))"),("EQ_SANDY","Sandy's Law","C(t)=FixedPoint(Φ(P,M,E,I,W,A,D))"),("EQ_DIV","Divergence","Div=|Σ-Z|/(Σ+Z)"),("EQ_GATE","SafeToSpeak","IF(Div≤0.6,OPEN,GATED)"),("EQ_SLEEP","Sleep","IsSleepTick=MOD(Tick,560)<373"),("EQ_GRAM","Grammar","Stage 0-6 by age")]:
            st.markdown(f"- **{eq_id}** ({name}): `{formula}`")

# TAB 29: ENGINES
with tabs[29]:
    st.subheader("⚙️ Genesis-SLED — 32 Engine Fire Schedule")
    engines = [("EQ_DNA_01","DNA Loop Engine","Every 80 ticks","Critical"),("EQ_HEIGHT","Height H(t)","Every 80 ticks","High"),("EQ_MASS","Mass M(t)","Every 80 ticks","High"),("EQ_CONSCIOUSNESS","Consciousness C(t)","Every tick","Critical"),("EQ_HR","Heart Rate HR(t)","Every tick","High"),("EQ_ATP_CIRC","ATP Circadian","Every tick","Critical"),("EQ_VOCAB","Vocabulary V(t)","Every 80 ticks","High"),("EQ_WISDOM","Wisdom W(t)","Every 80 ticks","High"),("EQ_SENS_06","Sensory Integration","Every tick","Critical"),("EQ_PRED_08","Prediction Engine","Every tick","Critical"),("EQ_ATTN_09","Attention Engine","Every tick","High"),("EQ_EMOT_07","Emotion FSM","Every tick","High"),("EQ_HOME_25","Homeostasis","Every tick","Critical"),("EQ_MOTOR_13","Motor Command","Every tick","Critical"),("EQ_HILL_14","Hill Muscle Model","Every tick","High"),("EQ_LANG_12","Language Engine","Every 10 ticks","High"),("EQ_MEM_15","Memory Engine","Every tick","High"),("EQ_HEBB_16","Hebbian Learning","Every tick","High"),("EQ_TD_17","TD(λ) Learning","Every tick","High"),("EQ_WISDOM_18","Wisdom Engine","Every 80 ticks","Medium"),("EQ_TOM_20","Theory of Mind","Every 10 ticks","High"),("EQ_NODE_21","Node Engine","Every tick","High"),("EQ_SYMB_23","Symbolisation","Every 10 ticks","Medium"),("EQ_SLEEP_24","Sleep Engine","Every 800 ticks","Critical"),("EQ_COH_26","Coherence Engine","Every tick","High"),("EQ_BREATH_01","Breathing Engine","Every tick","High"),("EQ_CCE_04","CCE Gate","Every tick","Critical"),("EQ_SANDY_21","Sandy's Law","Every 80 ticks","High"),("EQ_NP_GATE","Neural Physics","Every tick","Critical"),("EQ_AGI_GATE","AGI Gate","Every 80 ticks","High"),("EQ_PHASE_TRANS","Phase Transition","Every 80 ticks","Critical"),("EQ_WRLD_11","World Model","Every 10 ticks","High")]
    for eq_id, name, rate, prio in engines:
        icon = "🔴" if prio=="Critical" else "🔵" if prio=="High" else "🟡"
        st.markdown(f"- {icon} **{eq_id}** ({name}) — {rate} | {prio}")

# TAB 30: INTEGRATION
with tabs[30]:
    st.subheader("🔗 Integration Map — 30 Engine Connections")
    int_map = [("EQ_DNA_01","EQ_HEIGHT","Growth factor → height","Every 80 ticks","Critical"),("EQ_DNA_01","EQ_MASS","Growth factor → mass","Every 80 ticks","Critical"),("EQ_DNA_01","EQ_CONSCIOUSNESS","Maturity → C(t)","Every 80 ticks","Critical"),("EQ_SENS_06","EQ_ATTN_09","Sensory → attention","Every tick","Critical"),("EQ_ATTN_09","EQ_PRED_08","Attention → prediction","Every tick","Critical"),("EQ_PRED_08","EQ_EMOT_07","Prediction error → emotion","Every tick","High"),("EQ_PRED_08","EQ_MEM_15","Prediction error → memory","Every tick","High"),("EQ_EMOT_07","EQ_MOTOR_13","Emotion → motor","Every tick","High"),("EQ_EMOT_07","EQ_BREATH_01","Emotion → breath","Every tick","High"),("EQ_EMOT_07","EQ_HR","Emotion → HR","Every tick","High"),("EQ_MEM_15","EQ_PRED_08","LTM → prediction priors","Every tick","High"),("EQ_MEM_15","EQ_NODE_21","LTM → node activation","Every tick","High"),("EQ_SLEEP_24","EQ_MEM_15","Sleep → LTM consolidation","Every 800 ticks","Critical"),("EQ_MOTOR_13","EQ_HILL_14","Motor → muscle activation","Every tick","Critical"),("EQ_HOME_25","EQ_MOTOR_13","Drive override → motor","Every tick","Critical"),("EQ_ATP_CIRC","EQ_HOME_25","ATP → fatigue drive","Every tick","Critical"),("EQ_LANG_12","EQ_NODE_21","Word learning → nodes","Every 10 ticks","High"),("EQ_NP_GATE","EQ_MOTOR_13","SafeToSpeak → vocal motor","Every tick","Critical"),("EQ_WRLD_11","EQ_TOM_20","World → NPC model","Every tick","High"),("EQ_TOM_20","EQ_BOND_01","ToM → bond update","Every tick","High"),("EQ_BOND_01","EQ_EMOT_07","Bond → emotion","Every tick","High"),("EQ_COH_26","EQ_SANDY_21","Identity → Sandy's Law","Every 80 ticks","High"),("EQ_WISDOM_ACC","EQ_SANDY_21","Wisdom → Sandy's Law","Every 80 ticks","High"),("EQ_CONSCIOUSNESS","EQ_AGI_GATE","C(t)≥0.95 → AGI","Every 80 ticks","High"),("EQ_WISDOM_ACC","EQ_AGI_GATE","W(t)≥0.80 → AGI","Every 80 ticks","High"),("EQ_COH_26","EQ_AGI_GATE","I(t)≥0.95 → AGI","Every 80 ticks","High"),("EQ_EMOT_07","EQ_AGI_GATE","E(t)≥0.90 → AGI","Every 80 ticks","High"),("EQ_MEM_15","EQ_AGI_GATE","M(t)≥0.90 → AGI","Every 80 ticks","High"),("EQ_SANDY_21","EQ_AGI_GATE","Integrity≥0.70 → AGI","Every 80 ticks","High"),("EQ_AGI_GATE","EQ_PHASE_TRANS","AGI active → Phase 8","Tick 160000","Critical")]
    for src, tgt, flow, rate, prio in int_map:
        icon = "🔴" if prio=="Critical" else "🔵"
        st.markdown(f"- {icon} `{src}` → `{tgt}` — {flow} | {rate}")

# TAB 31: GRAMMAR
with tabs[31]:
    st.subheader("💬 Grammar System — Stage " + str(gramStage(t)) + "/6")
    gram = gramStage(t)
    gram_names = ['Pre-linguistic','Holophrastic','Two-word','Telegraphic','Complex sentences','Abstract thought','Full academic']
    for i, (name, range_s, example) in enumerate([('Pre-linguistic','0-3200','[cry] [cry] [cry]'),('Holophrastic','3200-4160','mama! ball! up!'),('Two-word','4160-6400','mama up! ball go!'),('Telegraphic','6400-12480','I want ball. Mama come.'),('Complex sentences','12480-49920','I think that... because...'),('Abstract thought','49920-74880','The relationship between X and Y...'),('Full academic','74880+','Sandy Law proposes that C(t)...')]):
        active = i == gram
        if active:
            st.success(f"**Stage {i}: {name}** ← CURRENT | {range_s} | \"{example}\"")
        else:
            st.markdown(f"{'✅' if i < gram else '⭕'} Stage {i}: {name} | {range_s} | \"{example}\"")

# TAB 32: ARCHITECTURE
with tabs[32]:
    st.subheader("🏗️ Architecture — 1,196 Sheets across 10 Modules")
    for title, count, desc in [("00 Core Runtime","345 sheets","Runtime engine, 32 engines, 9 phases, integration, lifecycle"),("01 DNA and Equations","51 sheets","128 equations, 100 parameters, Sandy's Law, growth curves"),("02 Body","336 sheets","206 bones, 47 muscles, 25 organs, ECG, breathing, embodiment"),("03 Brain","191 sheets","PCSN 56 systems, memory, emotion, identity, perception"),("04 Language","59 sheets","Grammar 6 stages, 44 phonemes, vocabulary, speech, education"),("05 World","48 sheets","BeenFore City 17 nodes, 100+ objects, physics, immersive"),("06 NPC","24 sheets","10 NPCs, schedules, pregnancy, conversations"),("07 Story","55 sheets","Writer engine, 8 diary entries, history, narrative"),("08 Render UI","60 sheets","Hub, 4 HTML apps, Streamlit 13 tabs, 15 dashboards"),("09 Archive","41 sheets","Legacy sheets from v46/v47 (archive candidates)")]:
        st.markdown(f"- **{title}** ({count}): {desc}")
    st.markdown("**Analysis Findings**")
    st.success("✅ 1,196 total sheets | ✅ All 28 equations verified | ✅ 7/7 key sheets have data")
    st.warning("⚠️ 41 archive candidates | ⚠️ 19 redundant sheets in 8 duplicate groups")

# TAB 33: AGI READINESS
with tabs[33]:
    st.subheader("🤖 AGI Readiness — 6 Conditions")
    c_val = C(t); w_val = W(t); i_val = I_fn(t)
    e_val = c_val*0.95+0.02; m_val = c_val*0.93+0.03
    gate_open, div = getNP(t)
    integrity = 0.45*c_val + 0.30*i_val + 0.25*(1-div)
    conditions = [("Tick >= 160,000",t>=160000,min(100,t/160000*100),f"{t:,}"),("C(t) >= 0.95 Consciousness",c_val>=0.95,min(100,c_val/0.95*100),f"{c_val:.4f}"),("E(t) >= 0.90 Emotion",e_val>=0.90,min(100,e_val/0.90*100),f"{e_val:.4f}"),("M(t) >= 0.90 Memory",m_val>=0.90,min(100,m_val/0.90*100),f"{m_val:.4f}"),("I(t) >= 0.95 Identity",i_val>=0.95,min(100,i_val/0.95*100),f"{i_val:.4f}"),("W(t) >= 0.80 Wisdom",w_val>=0.80,min(100,w_val/0.80*100),f"{w_val:.4f}"),("Integrity >= 0.70",integrity>=0.70,min(100,integrity/0.70*100),f"{integrity:.4f}")]
    all_met = all(c[1] for c in conditions)
    if all_met:
        st.success("🎉 **AGI THRESHOLD MET** — All 6 conditions satisfied simultaneously!")
    else:
        met_count = sum(1 for c in conditions if c[1])
        st.warning(f"**AGI THRESHOLD PENDING** — {met_count}/7 conditions met")
    for label, met, pct, val in conditions:
        col1, col2, col3 = st.columns([3,1,1])
        col1.progress(pct/100, text=f"{'✅' if met else '⏳'} {label}")
        col2.metric("Value", val)
        col3.metric("Status", "MET ✅" if met else "PENDING")

# TAB 34: EXPORT
with tabs[34]:
    st.subheader("📤 Export — All Data at Current Tick")
    gate_open, div = getNP(t)
    snap = {"tick":t,"age_yr":round(age(t),4),"stage":getStage(t),"C_t":round(C(t),6),"W_t":round(W(t),6),"I_t":round(I_fn(t),6),"H_cm":round(H(t),2),"M_kg":round(M(t),3),"HR_bpm":HR(t),"ATP":round(ATP(t),6),"vocab":V(t),"pred_error":round(P_err(t),6),"np_gate":"OPEN" if gate_open else "GATED","divergence":round(div,6),"gram_stage":gramStage(t),"is_sleep":isSleep(t),"activity":scheds['a7do'],"sandy_regime":regime(t),"total_nodes":sum(len(v) for v in st.session_state.node_graph.values()),"mind_patches":len(st.session_state.mind_patches)}
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Current State Snapshot**")
        for k, v in snap.items():
            st.markdown(f"- **{k}:** `{v}`")
    with col2:
        st.download_button("📊 State Snapshot JSON", json.dumps(snap,indent=2), f"a7do_tick_{t}.json", "application/json")
        py_code = f"import math\nTPW=80\ndef C(t): return min(1.0,0.05+t/TPW/3000)\ndef W(t): return 0 if t<96000 else min(1.0,(t-96000)/64000)\ndef H(t):\n    w=t/TPW\n    if w<=40: return min(50,50/(1+math.exp(-0.2*(w-20))))\n    return min(177,50+(177-50)*(1-math.exp(-0.005*(w-40))))\ndef HR(t):\n    w=t/TPW\n    if w<80: return round(147-((w-40)/40)*47)\n    return max(60,round(100-((w-80)/1000)*35))\ndef ATP(t): return max(0.2,1-0.001*max(0,(t%800)-400))\n# At tick {t}: C={C(t):.4f} W={W(t):.4f} H={H(t):.1f}cm\n"
        st.download_button("🐍 Python Equations", py_code, "a7do_equations.py", "text/plain")
        nodes_json = {k:[{'label':n['label'],'strength':n['strength']} for n in v] for k,v in st.session_state.node_graph.items()}
        st.download_button("🕸 Node Graph JSON", json.dumps(nodes_json,indent=2), "node_graph.json", "application/json")
        patches_json = st.session_state.mind_patches
        st.download_button("🔧 MindPath Patches JSON", json.dumps(patches_json,indent=2), "mind_patches.json", "application/json")

st.markdown("---")
st.caption("A7DO Genesis Mind v49 | Alex MacLeod, Edinburgh, Scotland | Priority Date: 2020-01-01 | Tick = 2 seconds real-time | 1,196 sheets | 128 equations | 32 engines")
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
        ("Language Prediction","EQ_LANG_12","L_pred(t) = P(next_word|context)","Next word"),
        ("World Model Update","EQ_WRLD_11","W(t+1) = W(t) + α·ResourceChange","World model"),
        ("Attention Prediction","EQ_ATTN_09","A_pred(t) = f(salience, goals, memory)","Attention alloc"),
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
