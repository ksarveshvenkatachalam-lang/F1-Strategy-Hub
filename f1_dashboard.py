"""
F1 STRATEGY DASHBOARD - COMPLETE EDITION
All 5 Phases: Circuits | Pit Stops | Performance | Qualifying | Lap Analysis
Built with Streamlit & Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="F1 Strategy Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 10px; color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric label { color: white !important; font-weight: bold; }
    .stMetric [data-testid="stMetricValue"] { color: white; font-size: 2rem; }
    h1 { color: #E10600; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    h2, h3 { color: #333; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# LOAD DATA FUNCTIONS
# ============================================================================
@st.cache_data
def load_circuits():
    try:
        circuits = pd.read_csv('circuits.csv')
        circuits.columns = circuits.columns.str.strip().str.lower()
        if circuits.columns[0] == 's':
            circuits.columns = ['circuitid'] + list(circuits.columns[1:])
        circuits = circuits.dropna(subset=['lat', 'lng'])
        return circuits
    except: return None

@st.cache_data
def load_races():
    try:
        races = pd.read_csv('races.csv')
        races.columns = races.columns.str.strip().str.lower()
        races['date'] = pd.to_datetime(races['date'], errors='coerce')
        return races
    except: return None

@st.cache_data
def load_pit_stops():
    try:
        pit_stops = pd.read_csv('pit_stops.csv')
        pit_stops.columns = pit_stops.columns.str.strip().str.lower()
        if 'duration' in pit_stops.columns:
            pit_stops['duration'] = pd.to_numeric(pit_stops['duration'], errors='coerce')
        if 'milliseconds' in pit_stops.columns:
            pit_stops['milliseconds'] = pd.to_numeric(pit_stops['milliseconds'], errors='coerce')
            if 'duration' not in pit_stops.columns or pit_stops['duration'].isna().sum() > len(pit_stops) * 0.5:
                pit_stops['duration'] = pit_stops['milliseconds'] / 1000
        pit_stops['lap'] = pd.to_numeric(pit_stops['lap'], errors='coerce')
        pit_stops['stop'] = pd.to_numeric(pit_stops['stop'], errors='coerce')
        pit_stops = pit_stops.dropna(subset=['duration'])
        return pit_stops
    except: return None

@st.cache_data
def load_constructors():
    try:
        constructors = pd.read_csv('constructors.csv')
        constructors.columns = constructors.columns.str.strip().str.lower()
        return constructors
    except: return None

@st.cache_data
def load_results():
    try:
        results = pd.read_csv('results.csv')
        results.columns = results.columns.str.strip().str.lower()
        results['position'] = pd.to_numeric(results['position'], errors='coerce')
        results['points'] = pd.to_numeric(results['points'], errors='coerce').fillna(0)
        results['grid'] = pd.to_numeric(results.get('grid', 0), errors='coerce')
        return results
    except: return None

@st.cache_data
def load_qualifying():
    try:
        qualifying = pd.read_csv('qualifying.csv')
        qualifying.columns = qualifying.columns.str.strip().str.lower()
        qualifying['position'] = pd.to_numeric(qualifying['position'], errors='coerce')
        return qualifying
    except: return None

@st.cache_data
def load_drivers():
    try:
        drivers = pd.read_csv('drivers.csv')
        drivers.columns = drivers.columns.str.strip().str.lower()
        # Create full name
        if 'forename' in drivers.columns and 'surname' in drivers.columns:
            drivers['fullname'] = drivers['forename'] + ' ' + drivers['surname']
        return drivers
    except: return None

@st.cache_data
def load_lap_times():
    try:
        lap_times = pd.read_csv('lap_times.csv')
        lap_times.columns = lap_times.columns.str.strip().str.lower()
        # Convert time to numeric (milliseconds)
        if 'milliseconds' in lap_times.columns:
            lap_times['milliseconds'] = pd.to_numeric(lap_times['milliseconds'], errors='coerce')
        lap_times['lap'] = pd.to_numeric(lap_times['lap'], errors='coerce')
        lap_times['position'] = pd.to_numeric(lap_times['position'], errors='coerce')
        return lap_times
    except: return None

# Load data
circuits = load_circuits()
races = load_races()
pit_stops = load_pit_stops()
constructors = load_constructors()
results = load_results()
qualifying = load_qualifying()
drivers = load_drivers()
lap_times = load_lap_times()

if circuits is None or races is None:
    st.error("❌ Required files missing: circuits.csv and races.csv")
    st.stop()

# Merge datasets
races_with_circuits = races.merge(circuits, on='circuitid', how='left', suffixes=('_race', '_circuit'))

# ============================================================================
# HEADER
# ============================================================================
st.title("🏎️ F1 STRATEGY DASHBOARD")
st.markdown("### Complete Analysis: 5 Phases of Strategic Insights")
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.header("🎯 Filters & Navigation")

# Year filter
available_years = sorted(races['year'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    "Select Season(s):",
    options=available_years,
    default=[available_years[0]] if len(available_years) > 0 else []
)

# Apply filters
if selected_years:
    filtered_races = races_with_circuits[races_with_circuits['year'].isin(selected_years)]
    filtered_races_ids = filtered_races['raceid'].unique() if 'raceid' in filtered_races.columns else []
else:
    filtered_races = races_with_circuits
    filtered_races_ids = races['raceid'].unique() if 'raceid' in races.columns else []

# Dashboard section
st.sidebar.markdown("---")
dashboard_section = st.sidebar.radio(
    "📊 Navigate Dashboard:",
    ["Overview", "Phase 1: Circuits", "Phase 2: Pit Stops", "Phase 3: Performance", 
     "Phase 4: Qualifying", "Phase 5: Lap Analysis"]
)

# Data status
st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Data Status")
st.sidebar.write("✅ Circuits" if circuits is not None else "❌ Circuits")
st.sidebar.write("✅ Races" if races is not None else "❌ Races")
st.sidebar.write("✅ Pit Stops" if pit_stops is not None else "❌ Pit Stops")
st.sidebar.write("✅ Constructors" if constructors is not None else "⚠️ Constructors")
st.sidebar.write("✅ Results" if results is not None else "❌ Results")
st.sidebar.write("✅ Qualifying" if qualifying is not None else "⚠️ Qualifying")
st.sidebar.write("✅ Drivers" if drivers is not None else "⚠️ Drivers")
st.sidebar.write("✅ Lap Times" if lap_times is not None else "⚠️ Lap Times")

# ============================================================================
# OVERVIEW METRICS
# ============================================================================
st.subheader("📊 Dashboard Overview")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🏁 Circuits", len(circuits))
with col2:
    st.metric("🏆 Races", f"{len(filtered_races):,}")
with col3:
    if pit_stops is not None:
        ps_count = len(pit_stops[pit_stops['raceid'].isin(filtered_races_ids)])
        st.metric("🔧 Pit Stops", f"{ps_count:,}")
    else:
        st.metric("🔧 Pit Stops", "N/A")
with col4:
    if results is not None:
        res_count = len(results[results['raceid'].isin(filtered_races_ids)])
        st.metric("🎯 Results", f"{res_count:,}")
    else:
        st.metric("🎯 Results", "N/A")
with col5:
    st.metric("🌍 Countries", circuits['country'].nunique())

st.markdown("---")

# ============================================================================
# PHASE 1: CIRCUITS
# ============================================================================
if dashboard_section in ["Overview", "Phase 1: Circuits"]:
    st.header("🗺️ Phase 1: Circuit Foundation")
    
    # World Map
    races_per_circuit = filtered_races.groupby('circuitid').size().reset_index(name='race_count')
    map_data = circuits.merge(races_per_circuit, on='circuitid', how='left')
    map_data['race_count'] = map_data['race_count'].fillna(0)
    
    fig_map = px.scatter_geo(map_data, lat='lat', lon='lng', hover_name='name',
        size='race_count', size_max=30, color='country', projection='natural earth')
    fig_map.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_map, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏆 Most Raced Circuits")
        top_circuits = filtered_races.groupby('name_circuit').size().reset_index(name='races').sort_values('races', ascending=False).head(10)
        fig = px.bar(top_circuits, x='races', y='name_circuit', orientation='h', color='races', color_continuous_scale='Reds')
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌍 Races by Country")
        races_by_country = filtered_races.groupby('country').size().reset_index(name='races').sort_values('races', ascending=False).head(10)
        fig = px.bar(races_by_country, x='races', y='country', orientation='h', color='races', color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# ============================================================================
# PHASE 2: PIT STOPS
# ============================================================================
if dashboard_section in ["Overview", "Phase 2: Pit Stops"] and pit_stops is not None:
    st.header("🔧 Phase 2: Pit Stop Strategy")
    
    filtered_pit_stops = pit_stops[
        (pit_stops['raceid'].isin(filtered_races_ids)) &
        (pit_stops['duration'].notna()) & 
        (pit_stops['duration'] > 0) &
        (pit_stops['duration'] < 300)
    ].copy()
    
    if len(filtered_pit_stops) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚡ Avg Pit Stop", f"{filtered_pit_stops['duration'].mean():.3f}s")
        with col2:
            st.metric("🏆 Fastest Stop", f"{filtered_pit_stops['duration'].min():.3f}s")
        with col3:
            st.metric("🔢 Total Stops", f"{len(filtered_pit_stops):,}")
        with col4:
            st.metric("📊 Stops/Race", f"{len(filtered_pit_stops) / len(filtered_races_ids):.1f}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⚡ Duration Distribution")
            valid = filtered_pit_stops[(filtered_pit_stops['duration'] >= 0.5) & (filtered_pit_stops['duration'] <= 60)]
            fig = px.histogram(valid, x='duration', nbins=50, color_discrete_sequence=['#E10600'])
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔢 Stop Strategy")
            stop_counts = filtered_pit_stops.groupby('stop').size().reset_index(name='count')
            fig = px.bar(stop_counts, x='stop', y='count', color='count', color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 🏆 Top 10 Fastest Pit Stops")
        fastest = filtered_pit_stops.nsmallest(10, 'duration')[['raceid', 'driverid', 'stop', 'lap', 'duration']]
        st.dataframe(fastest, use_container_width=True, hide_index=True)
    
    st.markdown("---")

# ============================================================================
# PHASE 3: PERFORMANCE
# ============================================================================
if dashboard_section in ["Overview", "Phase 3: Performance"] and results is not None:
    st.header("🏁 Phase 3: Circuit-Team Performance")
    
    if constructors is None:
        st.warning("⚠️ Upload `constructors.csv` to enable full Phase 3 analysis")
    else:
        filtered_results = results[results['raceid'].isin(filtered_races_ids)]
        
        if len(filtered_results) > 0:
            perf_data = filtered_results.merge(
                races[['raceid', 'circuitid', 'year']], on='raceid', how='left'
            ).merge(
                constructors[['constructorid', 'name']], on='constructorid', how='left'
            ).merge(
                circuits[['circuitid', 'name']], on='circuitid', how='left',
                suffixes=('_constructor', '_circuit')
            )
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Results", f"{len(filtered_results):,}")
            with col2:
                st.metric("⭐ Points", f"{filtered_results['points'].sum():,.0f}")
            with col3:
                st.metric("🏆 Winners", filtered_results[filtered_results['position'] == 1]['driverid'].nunique())
            with col4:
                st.metric("🏗️ Teams", filtered_results['constructorid'].nunique())
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🏆 Top Constructors")
                top_const = perf_data.groupby('name_constructor')['points'].sum().reset_index().sort_values('points', ascending=False).head(10)
                fig = px.bar(top_const, x='points', y='name_constructor', orientation='h', color='points', color_continuous_scale='Reds')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Position Distribution")
                pos_dist = filtered_results[filtered_results['position'] <= 10]['position'].value_counts().sort_index()
                fig = px.bar(x=pos_dist.index, y=pos_dist.values, color=pos_dist.values, color_continuous_scale='Blues')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# ============================================================================
# PHASE 4: QUALIFYING VS RACE
# ============================================================================
if dashboard_section in ["Overview", "Phase 4: Qualifying"] and qualifying is not None and results is not None:
    st.header("⚡ Phase 4: Qualifying vs Race Strategy")
    
    if drivers is None:
        st.warning("⚠️ Upload `drivers.csv` to see driver names")
    
    # Filter data
    filtered_quali = qualifying[qualifying['raceid'].isin(filtered_races_ids)]
    filtered_results = results[results['raceid'].isin(filtered_races_ids)]
    
    if len(filtered_quali) > 0 and len(filtered_results) > 0:
        # Merge qualifying and race results
        quali_race = filtered_quali.merge(
            filtered_results[['raceid', 'driverid', 'position', 'points']],
            on=['raceid', 'driverid'],
            how='inner',
            suffixes=('_quali', '_race')
        )
        
        # Calculate position changes
        quali_race['position_change'] = quali_race['position_quali'] - quali_race['position_race']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_change = quali_race['position_change'].mean()
            st.metric("📊 Avg Position Change", f"{avg_change:+.2f}")
        with col2:
            best_overtaker = quali_race['position_change'].max()
            st.metric("🏆 Best Gain", f"+{int(best_overtaker)}")
        with col3:
            worst_loss = quali_race['position_change'].min()
            st.metric("📉 Worst Loss", f"{int(worst_loss)}")
        with col4:
            improvers = (quali_race['position_change'] > 0).sum()
            pct = improvers / len(quali_race) * 100 if len(quali_race) > 0 else 0
            st.metric("🔼 Improvers", f"{pct:.1f}%")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Position Change Distribution")
            fig = px.histogram(quali_race, x='position_change', nbins=30, color_discrete_sequence=['#667eea'])
            fig.update_layout(height=400, xaxis_title="Position Change", yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Qualifying vs Race Position")
            sample_data = quali_race.sample(min(500, len(quali_race)))
            fig = px.scatter(sample_data, x='position_quali', y='position_race', 
                opacity=0.6, color_discrete_sequence=['#E10600'])
            fig.add_trace(go.Scatter(x=[1, 20], y=[1, 20], mode='lines', 
                line=dict(dash='dash', color='gray'), name='Perfect Conversion'))
            fig.update_layout(height=400, xaxis_title="Qualifying Position", yaxis_title="Race Position")
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Improvers
        st.markdown("#### 🏆 Top 10 Position Gainers")
        top_gainers = quali_race.nlargest(10, 'position_change')[
            ['raceid', 'driverid', 'position_quali', 'position_race', 'position_change', 'points']
        ].copy()
        top_gainers.columns = ['Race ID', 'Driver ID', 'Quali Pos', 'Race Pos', 'Gained', 'Points']
        st.dataframe(top_gainers, use_container_width=True, hide_index=True)
    
    st.markdown("---")

# ============================================================================
# PHASE 5: LAP ANALYSIS
# ============================================================================
if dashboard_section in ["Overview", "Phase 5: Lap Analysis"]:
    st.header("🔥 Phase 5: Advanced Lap Time Analysis")
    
    if lap_times is None:
        st.warning("⚠️ Upload `lap_times.csv` (5.2 MB) to enable Phase 5")
        st.info("""
        **Phase 5 Features:**
        - Lap time evolution analysis
        - Pace comparison between drivers
        - Stint performance analysis
        - Fastest lap analysis
        - Race pace trends
        """)
    else:
        filtered_laps = lap_times[lap_times['raceid'].isin(filtered_races_ids)].copy()
        
        if len(filtered_laps) > 0:
            # Convert milliseconds to seconds
            filtered_laps['time_seconds'] = filtered_laps['milliseconds'] / 1000
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏱️ Total Laps", f"{len(filtered_laps):,}")
            with col2:
                st.metric("🏆 Fastest Lap", f"{filtered_laps['time_seconds'].min():.3f}s")
            with col3:
                st.metric("📊 Avg Lap Time", f"{filtered_laps['time_seconds'].mean():.3f}s")
            with col4:
                st.metric("🎯 Unique Drivers", filtered_laps['driverid'].nunique())
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ⏱️ Lap Time Distribution")
                # Filter reasonable lap times (30s to 150s)
                valid_laps = filtered_laps[
                    (filtered_laps['time_seconds'] >= 30) & 
                    (filtered_laps['time_seconds'] <= 150)
                ]
                fig = px.histogram(valid_laps, x='time_seconds', nbins=50, 
                    color_discrete_sequence=['#E10600'])
                fig.update_layout(height=400, xaxis_title="Lap Time (seconds)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 Lap Time Evolution")
                # Sample data for performance
                sample_laps = filtered_laps.sample(min(1000, len(filtered_laps)))
                sample_laps = sample_laps[(sample_laps['time_seconds'] >= 30) & 
                                         (sample_laps['time_seconds'] <= 150)]
                
                fig = px.scatter(sample_laps, x='lap', y='time_seconds', 
                    opacity=0.3, color_discrete_sequence=['#667eea'])
                fig.update_layout(height=400, xaxis_title="Lap Number", yaxis_title="Lap Time (s)")
                st.plotly_chart(fig, use_container_width=True)
            
            # Fastest laps
            st.markdown("#### 🏆 Top 10 Fastest Laps")
            fastest_laps = filtered_laps.nsmallest(10, 'time_seconds')[
                ['raceid', 'driverid', 'lap', 'position', 'time_seconds']
            ].copy()
            fastest_laps['time_seconds'] = fastest_laps['time_seconds'].round(3)
            fastest_laps.columns = ['Race ID', 'Driver ID', 'Lap', 'Position', 'Time (s)']
            st.dataframe(fastest_laps, use_container_width=True, hide_index=True)
        else:
            st.info("No lap time data for selected filters")
    
    st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p style='font-size: 1.2em; margin-bottom: 10px;'>
            🏎️ <strong>F1 STRATEGY DASHBOARD - COMPLETE EDITION</strong>
        </p>
        <p style='font-size: 0.9em;'>
            Phase 1: Circuits | Phase 2: Pit Stops | Phase 3: Performance<br>
            Phase 4: Qualifying | Phase 5: Lap Analysis
        </p>
        <p style='font-size: 0.8em; margin-top: 10px;'>
            Built with Streamlit & Plotly | Portfolio Project 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
