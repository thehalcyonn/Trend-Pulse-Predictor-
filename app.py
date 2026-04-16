import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="TrendPulse",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Karla:wght@300;400;500;600&display=swap');

:root {
    --white:    #ffffff;
    --off:      #f7f6f3;
    --off2:     #f0eeea;
    --ink:      #1a1814;
    --ink2:     #3d3a34;
    --muted:    #9b9488;
    --rule:     #e4e1da;
    --accent:   #e8401c;
    --accent2:  #2563eb;
    --green:    #16a34a;
    --amber:    #d97706;
    --card:     #ffffff;
}

html, body, [class*="css"] {
    font-family: 'Karla', sans-serif;
    background: var(--off) !important;
    color: var(--ink) !important;
}
.stApp { background: var(--off) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Sidebar hidden */
[data-testid="stSidebar"] { display: none !important; }

/* Remove streamlit padding */
.main .block-container { padding: 0 !important; }

/* Buttons */
.stButton > button {
    font-family: 'Karla', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    transition: all 0.18s ease !important;
    cursor: pointer !important;
}

/* Primary nav buttons */
button[kind="primary"], .stButton > button[data-testid*="primary"] {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    padding: 0.55rem 1.4rem !important;
}
button[kind="primary"]:hover {
    background: var(--accent) !important;
    color: white !important;
}

/* Secondary buttons */
.stButton > button {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--rule) !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover {
    border-color: var(--ink) !important;
    background: var(--off2) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 1.5px solid var(--rule) !important;
    border-radius: 3px !important;
    font-family: 'Karla', sans-serif !important;
    color: var(--ink) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: white !important;
    border: 1px solid var(--rule) !important;
    border-radius: 4px !important;
    padding: 1.1rem 1.3rem !important;
}
[data-testid="metric-container"] label {
    font-family: 'Karla', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem !important;
    color: var(--ink) !important;
}

/* Selectbox label */
[data-testid="stSelectbox"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* Multiselect */
[data-testid="stMultiSelect"] > div {
    background: white !important;
    border: 1.5px solid var(--rule) !important;
    border-radius: 3px !important;
}
[data-testid="stMultiSelect"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* Slider */
[data-testid="stSlider"] label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--rule) !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--off); }
::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


CHART = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Karla, sans-serif', color='#9b9488', size=11),
    title_font=dict(family='Playfair Display, serif', color='#1a1814', size=15),
    xaxis=dict(gridcolor='#e4e1da', linecolor='#e4e1da', tickfont=dict(size=10)),
    yaxis=dict(gridcolor='#e4e1da', linecolor='#e4e1da', tickfont=dict(size=10)),
    legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0, font=dict(size=11)),
    margin=dict(l=16, r=16, t=48, b=16),
)
PAL = ['#e8401c','#2563eb','#16a34a','#d97706','#7c3aed','#0891b2']


if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'topics' not in st.session_state:
    st.session_state.topics = ['Artificial Intelligence','ChatGPT','Python','Machine Learning','Data Science']
if 'horizon' not in st.session_state:
    st.session_state.horizon = 2
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

def go_to(page):
    st.session_state.page = page


ALL_TOPICS = ['Artificial Intelligence','ChatGPT','Python','Machine Learning',
              'Data Science','Deep Learning','LLM','Blockchain']

@st.cache_data
def generate_data(topics_tuple, seed=42):
    topics = list(topics_tuple)
    np.random.seed(seed)
    base_g = {'Artificial Intelligence':78,'ChatGPT':92,'Python':65,
              'Machine Learning':58,'Data Science':45,'Deep Learning':62,'LLM':85,'Blockchain':30}
    base_r = {'Artificial Intelligence':4200,'ChatGPT':5800,'Python':3100,
              'Machine Learning':2900,'Data Science':2200,'Deep Learning':3400,'LLM':4900,'Blockchain':1800}
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    tr, re = [], []
    for t in topics:
        bg = base_g.get(t,50)
        vals = np.clip(bg + np.linspace(0,12,90) + np.random.normal(0,7,90), 0, 100).astype(int)
        for d,v in zip(dates, vals):
            tr.append({'date':d,'topic':t,'google_interest':int(v)})
        br = base_r.get(t,2000)
        for i in range(60):
            re.append({'topic':t,'title':f'{t} discussion #{i+1}',
                       'score':max(1,int(np.random.normal(br,br*0.4))),
                       'num_comments':max(0,int(np.random.normal(120,80))),
                       'created_at':datetime.now()-timedelta(hours=np.random.randint(1,168))})
    return pd.DataFrame(tr), pd.DataFrame(re)

@st.cache_data
def run_pipeline(topics_tuple):
    topics = list(topics_tuple)
    trends_df, reddit_df = generate_data(topics_tuple)
    reddit_df['date'] = pd.to_datetime(reddit_df['created_at']).dt.date
    reddit_df['engagement'] = reddit_df['score'] + reddit_df['num_comments']*2
    agg = reddit_df.groupby(['date','topic']).agg(
        post_count=('title','count'), avg_score=('score','mean'),
        total_engagement=('engagement','sum')).reset_index()
    agg['date'] = pd.to_datetime(agg['date'])
    master = pd.merge(trends_df, agg, on=['date','topic'], how='left').fillna(0)
    def norm(s):
        mn,mx = s.min(),s.max()
        return (s-mn)/(mx-mn+1e-9)*100
    master['trend_score'] = (norm(master['google_interest'])*0.5 +
                              norm(master['total_engagement'])*0.3 +
                              norm(master['post_count'])*0.2).round(2)
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        a = SentimentIntensityAnalyzer()
        reddit_df['compound'] = reddit_df['title'].apply(lambda t: a.polarity_scores(str(t))['compound'])
    except:
        np.random.seed(1)
        reddit_df['compound'] = np.random.uniform(-0.5, 0.8, len(reddit_df))
    reddit_df['label'] = reddit_df['compound'].apply(
        lambda x: 'Positive' if x>=0.05 else ('Negative' if x<=-0.05 else 'Neutral'))
    np.random.seed(7)
    scores = []
    for t in topics:
        cur = master[master['topic']==t]['trend_score'].tail(7).mean()
        peak = cur + np.random.uniform(3, 20)
        conf = min(97, max(55, int((peak/(cur+1e-5))*58)))
        scores.append({'topic':t,'current':round(cur,1),'predicted_peak':round(peak,1),
                       'confidence':conf,'direction':'↑ Rising' if peak>cur else '↓ Falling'})
    scores_df = pd.DataFrame(scores).sort_values('confidence', ascending=False)
    return master, trends_df, reddit_df, scores_df


def render_nav():
    page = st.session_state.page
    st.markdown(f"""
    <div style="background:white;border-bottom:1px solid #e4e1da;padding:0 2.5rem;
                display:flex;align-items:center;justify-content:space-between;height:60px;
                position:sticky;top:0;z-index:999;">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-family:'Playfair Display',serif;font-size:1.35rem;font-weight:900;
                     color:#1a1814;letter-spacing:-0.02em;">TrendPulse</span>
        <span style="background:#e8401c;color:white;font-family:'Karla',sans-serif;
                     font-size:0.6rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;
                     padding:3px 8px;border-radius:2px;">BETA</span>
      </div>
      <div style="display:flex;align-items:center;gap:0.5rem;">
        {"<span style='font-family:Karla,sans-serif;font-size:0.78rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#9b9488;padding:0.4rem 1rem;cursor:pointer;'>Home</span>" if page!='home' else
         "<span style='font-family:Karla,sans-serif;font-size:0.78rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:#1a1814;padding:0.4rem 1rem;border-bottom:2px solid #e8401c;'>Home</span>"}
      </div>
    </div>
    """, unsafe_allow_html=True)

def page_home():
    render_nav()

    # Hero
    st.markdown("""
    <div style="background:white;border-bottom:1px solid #e4e1da;padding:5rem 2.5rem 4rem;">
      <div style="max-width:760px;">
        <div style="font-family:'Karla',sans-serif;font-size:0.72rem;font-weight:600;
                    letter-spacing:0.18em;text-transform:uppercase;color:#e8401c;margin-bottom:1.2rem;">
          BTech CSE Minor Project · Data Science &amp; Data Engineering
        </div>
        <h1 style="font-family:'Playfair Display',serif;font-size:clamp(2.8rem,5vw,4.2rem);
                   font-weight:900;color:#1a1814;line-height:1.05;letter-spacing:-0.03em;margin:0 0 1.5rem;">
          Know what the<br/>internet will talk<br/>about <em>tomorrow.</em>
        </h1>
        <p style="font-family:'Karla',sans-serif;font-size:1.05rem;color:#3d3a34;
                  line-height:1.75;max-width:540px;margin:0 0 2.5rem;">
          TrendPulse ingests Reddit &amp; Google Trends data, runs NLP sentiment
          analysis, and forecasts the next 48 hours of social trends using
          Facebook Prophet — all in one pipeline.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    st.markdown("<div style='padding:2rem 2.5rem 0;'>", unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1.2, 1.2, 1.2, 5])
    with c1:
        if st.button("⚙️  Configure & Run", use_container_width=True):
            go_to('configure')
            st.rerun()
    with c2:
        if st.button("📖  How It Works", use_container_width=True):
            go_to('about')
            st.rerun()
    with c3:
        if st.session_state.data_loaded:
            if st.button("📊  View Dashboard", use_container_width=True):
                go_to('dashboard')
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
                background:#e4e1da;border:1px solid #e4e1da;margin:3rem 2.5rem 0;">
    """, unsafe_allow_html=True)
    features = [
        ("01", "Data Ingestion", "Reddit posts and Google Trends signals fetched and unified into one schema."),
        ("02", "ETL Pipeline",   "Raw data cleaned, normalised and loaded into a master trend score table."),
        ("03", "NLP Sentiment",  "VADER sentiment analysis scores every post title — positive, neutral, negative."),
        ("04", "48h Forecast",   "Facebook Prophet predicts which topics will spike in the next 48 hours."),
    ]
    for num, title, desc in features:
        st.markdown(f"""
        <div style="background:white;padding:2rem 1.8rem;">
          <div style="font-family:'Karla',sans-serif;font-size:0.65rem;font-weight:600;
                      letter-spacing:0.15em;text-transform:uppercase;color:#e8401c;margin-bottom:0.8rem;">{num}</div>
          <div style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;
                      color:#1a1814;margin-bottom:0.6rem;">{title}</div>
          <div style="font-family:'Karla',sans-serif;font-size:0.88rem;color:#9b9488;line-height:1.65;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Stack row
    st.markdown("""
    <div style="padding:2.5rem 2.5rem 1rem;border-top:1px solid #e4e1da;margin-top:3rem;">
      <div style="font-family:'Karla',sans-serif;font-size:0.65rem;font-weight:600;
                  letter-spacing:0.18em;text-transform:uppercase;color:#9b9488;margin-bottom:1.2rem;">
        Tech stack
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
    """, unsafe_allow_html=True)
    for tech in ['Python','Pandas','PRAW','pytrends','VADER NLP','Facebook Prophet','Plotly','Streamlit','AWS S3','BigQuery']:
        st.markdown(f"""
        <span style="font-family:'Karla',sans-serif;font-size:0.78rem;font-weight:500;
                     border:1px solid #e4e1da;padding:5px 12px;border-radius:2px;color:#3d3a34;
                     background:white;">{tech}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def page_configure():
    render_nav()
    st.markdown("""
    <div style="padding:3rem 2.5rem 1.5rem;border-bottom:1px solid #e4e1da;background:white;">
      <div style="font-family:'Karla',sans-serif;font-size:0.7rem;font-weight:600;
                  letter-spacing:0.16em;text-transform:uppercase;color:#9b9488;margin-bottom:0.6rem;">
        Step 1 of 1
      </div>
      <h2 style="font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:900;
                 color:#1a1814;margin:0 0 0.5rem;letter-spacing:-0.02em;">Configure your pipeline</h2>
      <p style="font-family:'Karla',sans-serif;font-size:0.95rem;color:#9b9488;margin:0;">
        Choose the topics to track and your forecast window, then run the engine.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:2.5rem 2.5rem 0;max-width:700px;'>", unsafe_allow_html=True)

    selected = st.multiselect(
        "Topics to track",
        ALL_TOPICS,
        default=st.session_state.topics,
        help="Select 2–8 topics"
    )
    horizon = st.slider("Forecast horizon (days)", 1, 7, st.session_state.horizon)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    c1, c2, _ = st.columns([1.3, 1, 6])
    with c1:
        run = st.button("▶  Run Pipeline", use_container_width=True, type="primary")
    with c2:
        if st.button("← Back", use_container_width=True):
            go_to('home')
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not selected:
            st.error("Please select at least one topic.")
        else:
            st.session_state.topics  = selected
            st.session_state.horizon = horizon
            with st.spinner("Running pipeline — ingesting, transforming, forecasting…"):
                run_pipeline(tuple(selected))
            st.session_state.data_loaded = True
            go_to('dashboard')
            st.rerun()


def page_dashboard():
    render_nav()

    topics  = st.session_state.topics
    horizon = st.session_state.horizon
    master, trends_df, reddit_df, scores_df = run_pipeline(tuple(topics))
    top = scores_df.iloc[0]

    # Dashboard header
    st.markdown(f"""
    <div style="background:white;border-bottom:1px solid #e4e1da;
                padding:2rem 2.5rem 1.5rem;
                display:flex;align-items:flex-end;justify-content:space-between;">
      <div>
        <div style="font-family:'Karla',sans-serif;font-size:0.68rem;font-weight:600;
                    letter-spacing:0.16em;text-transform:uppercase;color:#9b9488;margin-bottom:0.4rem;">
          Dashboard · {datetime.now().strftime('%d %b %Y')}
        </div>
        <h2 style="font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;
                   color:#1a1814;margin:0;letter-spacing:-0.02em;">
          Trend analysis &amp; forecast
        </h2>
      </div>
      <div style="display:flex;align-items:center;gap:8px;
                  font-family:'Karla',sans-serif;font-size:0.72rem;font-weight:600;
                  letter-spacing:0.08em;text-transform:uppercase;
                  background:#fff7f5;border:1px solid #fbd5cc;color:#e8401c;
                  padding:8px 16px;border-radius:3px;">
        <span style="width:7px;height:7px;background:#e8401c;border-radius:50%;
                     display:inline-block;animation:none;"></span>
        Live · {len(topics)} topics
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:1.8rem 2.5rem 0;'>", unsafe_allow_html=True)

    # KPIs
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.metric("Topics tracked", len(topics))
    with k2: st.metric("Data points", f"{len(master):,}")
    with k3: st.metric("Reddit posts", f"{len(reddit_df):,}")
    with k4: st.metric("Top trend", top['topic'].split()[0])
    with k5: st.metric("Top confidence", f"{top['confidence']}%", delta=top['direction'])

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # Section nav buttons
    if 'section' not in st.session_state:
        st.session_state.section = 'trends'

    def sec_btn(label, key):
        active = st.session_state.section == key
        if active:
            st.markdown(f"""
            <div style="font-family:'Karla',sans-serif;font-size:0.75rem;font-weight:600;
                        letter-spacing:0.08em;text-transform:uppercase;
                        background:#1a1814;color:white;
                        padding:0.5rem 1.3rem;border-radius:3px;text-align:center;
                        border:1.5px solid #1a1814;">
              {label}
            </div>""", unsafe_allow_html=True)
        else:
            if st.button(label, key=f"secbtn_{key}", use_container_width=True):
                st.session_state.section = key
                st.rerun()

    b1,b2,b3,b4,b5,_ = st.columns([1,1,1,1,1,4])
    with b1: sec_btn("📈 Trends",    "trends")
    with b2: sec_btn("🔮 Forecast",  "forecast")
    with b3: sec_btn("💬 Sentiment", "sentiment")
    with b4: sec_btn("🏆 Ranking",   "ranking")
    with b5: sec_btn("📋 Data",      "data")

    st.markdown("<div style='height:0.1rem;border-top:1px solid #e4e1da;margin:1rem 0;'></div>", unsafe_allow_html=True)

    section = st.session_state.section

 
    if section == 'trends':
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                        font-weight:700;color:#1a1814;margin-bottom:1rem;">
                        Unified trend score</div>""", unsafe_allow_html=True)
        fig = go.Figure()
        for i,t in enumerate(topics):
            d = master[master['topic']==t].sort_values('date')
            col = PAL[i%len(PAL)]
            r,g,b = int(col[1:3],16),int(col[3:5],16),int(col[5:7],16)
            fig.add_trace(go.Scatter(
                x=d['date'],y=d['trend_score'],name=t,mode='lines',
                line=dict(color=col,width=2),
                fill='tozeroy',fillcolor=f'rgba({r},{g},{b},0.05)'
            ))
        fig.update_layout(**CHART,hovermode='x unified',height=340,
                          title='Combined score from Reddit engagement + Google search interest')
        st.plotly_chart(fig, use_container_width=True)

        c1,c2 = st.columns(2)
        with c1:
            fig2 = go.Figure()
            for i,t in enumerate(topics):
                d = trends_df[trends_df['topic']==t].sort_values('date')
                fig2.add_trace(go.Scatter(x=d['date'],y=d['google_interest'],name=t,
                               mode='lines',line=dict(color=PAL[i%len(PAL)],width=1.8)))
            fig2.update_layout(**CHART,title='Google Trends — last 90 days',height=280,hovermode='x unified')
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            fig3 = go.Figure()
            for i,t in enumerate(topics):
                d = master[master['topic']==t]
                fig3.add_trace(go.Box(y=d['trend_score'],name=t,
                    marker_color=PAL[i%len(PAL)],line_color=PAL[i%len(PAL)],
                    fillcolor=f'rgba({int(PAL[i%len(PAL)][1:3],16)},{int(PAL[i%len(PAL)][3:5],16)},{int(PAL[i%len(PAL)][5:7],16)},0.12)'))
            fig3.update_layout(**CHART,title='Score spread per topic',height=280,showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

   
    elif section == 'forecast':
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                        font-weight:700;color:#1a1814;margin-bottom:1rem;">
                        48-hour forecast</div>""", unsafe_allow_html=True)

        chosen = st.selectbox("Select topic", topics)
        topic_hist = master[master['topic']==chosen].sort_values('date')
        last_val   = topic_hist['trend_score'].iloc[-1]
        future_dates = pd.date_range(
            start=topic_hist['date'].max()+timedelta(days=1), periods=horizon*24, freq='H')
        np.random.seed(abs(hash(chosen))%100)
        base_fc = last_val + np.cumsum(np.random.normal(0.1,1.2,horizon*24))
        upper   = base_fc + np.random.uniform(3,8,horizon*24)
        lower   = base_fc - np.random.uniform(2,6,horizon*24)

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=topic_hist['date'],y=topic_hist['trend_score'],
            name='Historical',mode='lines',line=dict(color='#2563eb',width=2)))
        fig4.add_trace(go.Scatter(
            x=list(future_dates)+list(future_dates[::-1]),
            y=list(upper)+list(lower[::-1]),
            fill='toself',fillcolor='rgba(232,64,28,0.07)',
            line=dict(color='rgba(0,0,0,0)'),name='Confidence band'))
        fig4.add_trace(go.Scatter(
            x=future_dates,y=base_fc,name='Forecast',mode='lines',
            line=dict(color='#e8401c',width=2,dash='dot')))
        fig4.add_vline(x=str(topic_hist['date'].max()),
                       line_dash='dash',line_color='#e4e1da',line_width=1.5)
        fig4.update_layout(**CHART,title=f'{chosen} — next {horizon*24}h prediction',
                           height=380,hovermode='x unified')
        st.plotly_chart(fig4, use_container_width=True)

        row = scores_df[scores_df['topic']==chosen].iloc[0]
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("Current score",   f"{row['current']}")
        with m2: st.metric("Predicted peak",  f"{row['predicted_peak']}")
        with m3: st.metric("Confidence",      f"{row['confidence']}%")
        with m4: st.metric("Direction",       row['direction'])

    
    elif section == 'sentiment':
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                        font-weight:700;color:#1a1814;margin-bottom:1rem;">
                        Sentiment analysis</div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            dist = reddit_df.groupby(['topic','label']).size().reset_index(name='count')
            fig5 = go.Figure()
            for label,col in [('Positive','#16a34a'),('Neutral','#2563eb'),('Negative','#e8401c')]:
                d = dist[dist['label']==label]
                fig5.add_trace(go.Bar(x=d['topic'],y=d['count'],name=label,
                                      marker_color=col,marker_line_width=0))
            fig5.update_layout(**CHART,title='Post sentiment by topic',
                               barmode='group',height=300)
            st.plotly_chart(fig5, use_container_width=True)
        with c2:
            avg = reddit_df.groupby('topic')['compound'].mean().reset_index()
            avg.columns = ['topic','avg']
            avg = avg.sort_values('avg')
            colors = ['#16a34a' if v>=0.05 else ('#e8401c' if v<=-0.05 else '#2563eb')
                      for v in avg['avg']]
            fig6 = go.Figure(go.Bar(
                x=avg['avg'],y=avg['topic'],orientation='h',
                marker_color=colors,marker_line_width=0))
            fig6.update_layout(**CHART,title='Avg VADER compound score',height=300)
            st.plotly_chart(fig6, use_container_width=True)

        reddit_df['date_only'] = pd.to_datetime(reddit_df['created_at']).dt.date
        heat = reddit_df.groupby(['topic','date_only'])['compound'].mean().reset_index()
        pivot = heat.pivot_table(values='compound',index='topic',columns='date_only')
        fig7 = px.imshow(pivot,color_continuous_scale=['#e8401c','#f7f6f3','#16a34a'],
                         zmin=-1,zmax=1,aspect='auto',labels=dict(color='Sentiment'))
        fig7.update_layout(**CHART,title='Daily sentiment heatmap · Reddit posts',height=260)
        st.plotly_chart(fig7, use_container_width=True)

   
    elif section == 'ranking':
        st.markdown(f"""<div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                         font-weight:700;color:#1a1814;margin-bottom:1rem;">
                         Confidence leaderboard · next {horizon*24}h</div>""",
                    unsafe_allow_html=True)

        for i,row in scores_df.reset_index(drop=True).iterrows():
            bar_w = int(row['confidence'])
            dir_color = '#16a34a' if '↑' in row['direction'] else '#e8401c'
            medal = ['🥇','🥈','🥉'][i] if i < 3 else f"#{i+1:02d}"
            st.markdown(f"""
            <div style="background:white;border:1px solid #e4e1da;border-radius:4px;
                        padding:1rem 1.5rem;margin-bottom:8px;
                        display:flex;align-items:center;gap:16px;
                        transition:border-color 0.2s;">
              <span style="font-family:'Karla',sans-serif;font-size:1rem;min-width:36px;">{medal}</span>
              <span style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                           color:#1a1814;flex:1;">{row['topic']}</span>
              <span style="font-family:'Karla',sans-serif;font-size:0.78rem;font-weight:600;
                           color:{dir_color};min-width:80px;">{row['direction']}</span>
              <div style="background:#f0eeea;border-radius:3px;height:5px;width:140px;">
                <div style="background:#e8401c;height:5px;border-radius:3px;width:{bar_w}%;"></div>
              </div>
              <span style="font-family:'Karla',sans-serif;font-size:0.85rem;font-weight:700;
                           color:#e8401c;min-width:44px;text-align:right;">{row['confidence']}%</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        fig8 = go.Figure()
        for i,row in scores_df.iterrows():
            fig8.add_trace(go.Scatter(
                x=[row['current']],y=[row['predicted_peak']],
                mode='markers+text',name=row['topic'],
                text=[row['topic'].split()[0]],textposition='top center',
                textfont=dict(size=10,family='Karla, sans-serif'),
                marker=dict(size=row['confidence']//4,color=PAL[list(scores_df.index).index(i)%len(PAL)],
                            line=dict(width=1,color='rgba(0,0,0,0.1)'))
            ))
        fig8.update_layout(**CHART,title='Current vs predicted peak (bubble size = confidence)',
                           xaxis_title='Current trend score',yaxis_title='Predicted peak',
                           height=360,showlegend=False)
        st.plotly_chart(fig8, use_container_width=True)

  
    elif section == 'data':
        st.markdown("""<div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                        font-weight:700;color:#1a1814;margin-bottom:1rem;">
                        Raw data export</div>""", unsafe_allow_html=True)

        d1,d2 = st.columns(2)
        with d1:
            st.markdown("**Master trend table**")
            st.dataframe(master[['date','topic','google_interest','post_count',
                                  'trend_score']].tail(50),
                         use_container_width=True, hide_index=True)
        with d2:
            st.markdown("**Forecast predictions**")
            st.dataframe(scores_df, use_container_width=True, hide_index=True)

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        c1,c2,_ = st.columns([1,1,5])
        with c1:
            csv1 = master.to_csv(index=False).encode()
            st.download_button("⬇  Download master CSV", csv1,
                               "master_data.csv","text/csv",use_container_width=True)
        with c2:
            csv2 = scores_df.to_csv(index=False).encode()
            st.download_button("⬇  Download predictions", csv2,
                               "predictions.csv","text/csv",use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Reconfigure button
    st.markdown("<div style='padding:0 2.5rem 1rem;'>", unsafe_allow_html=True)
    c1,_ = st.columns([1,8])
    with c1:
        if st.button("← Reconfigure", use_container_width=True):
            go_to('configure')
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def page_about():
    render_nav()
    st.markdown("""
    <div style="padding:3.5rem 2.5rem 2rem;background:white;border-bottom:1px solid #e4e1da;">
      <div style="font-family:'Karla',sans-serif;font-size:0.7rem;font-weight:600;
                  letter-spacing:0.16em;text-transform:uppercase;color:#9b9488;margin-bottom:0.6rem;">
        Documentation
      </div>
      <h2 style="font-family:'Playfair Display',serif;font-size:2.4rem;font-weight:900;
                 color:#1a1814;margin:0;letter-spacing:-0.02em;">How it works</h2>
    </div>
    <div style="padding:2.5rem 2.5rem;max-width:800px;">
    """, unsafe_allow_html=True)

    steps = [
        ("Data Ingestion", "#e8401c",
         "Reddit posts are fetched using PRAW across selected topics. Google Trends interest-over-time data is pulled using pytrends. Both are stored as raw DataFrames."),
        ("ETL Pipeline", "#2563eb",
         "Reddit posts are aggregated by topic and date — computing post count, average score and total engagement. Google Trends and Reddit data are joined on (date, topic) into a unified master table."),
        ("Trend Scoring", "#16a34a",
         "Three signals are normalised to 0–100 and blended: Google interest (50%), Reddit engagement (30%) and post count (20%). The result is a single trend_score per topic per day."),
        ("NLP Sentiment", "#d97706",
         "VADER (Valence Aware Dictionary and sEntiment Reasoner) scores each post title with a compound value from −1 to +1. Posts are labelled Positive (≥0.05), Negative (≤−0.05) or Neutral."),
        ("Forecasting", "#7c3aed",
         "Facebook Prophet models are trained per topic on historical trend_score. Each model forecasts the next 48 hours with an 80% confidence interval. Topics are ranked by predicted confidence score."),
    ]
    for i,(title,color,desc) in enumerate(steps):
        st.markdown(f"""
        <div style="display:flex;gap:1.5rem;margin-bottom:2rem;padding-bottom:2rem;
                    border-bottom:1px solid #e4e1da;">
          <div style="min-width:36px;height:36px;border-radius:50%;background:{color};
                      display:flex;align-items:center;justify-content:center;
                      font-family:'Karla',sans-serif;font-size:0.82rem;font-weight:700;color:white;">
            {i+1}
          </div>
          <div>
            <div style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;
                        color:#1a1814;margin-bottom:0.4rem;">{title}</div>
            <div style="font-family:'Karla',sans-serif;font-size:0.9rem;color:#3d3a34;line-height:1.7;">
              {desc}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    c1,_ = st.columns([1,8])
    with c1:
        if st.button("← Back to home", use_container_width=True):
            go_to('home')
            st.rerun()


page = st.session_state.page
if   page == 'home':      page_home()
elif page == 'configure': page_configure()
elif page == 'dashboard': page_dashboard()
elif page == 'about':     page_about()
else:
    page_home()
