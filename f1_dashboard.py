"""
F1 STRATEGY DASHBOARD - Complete Edition
Phases 1-3: Circuit Foundation + Pit Stop Strategy + Performance Analysis
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
# CUSTOM CSS - F1 Racing Theme
# ============================================================================
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: white !important;
        font-weight: bold;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white;
        font-size: 2rem;
    }
    h1 {
        color: #E10600;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    h2, h3 {
        color: #333;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# LOAD DATA FUNCTIONS
# ============================================================================
@st.cache_data
def load_circuits():
    """Load circuit data"""
    try:
        circuits = pd.read_csv('circuits.csv')
        circuits.columns = circuits.columns.str.strip().str.lower()
        if circuits.columns[0] == 's':
            circuits.columns = ['circuitid'] + list(circuits.columns[1:])
        circuits = circuits.dropna(subset=['lat', 'lng'])
        return circuits
    except Exception as e:
        st.error(f"Error loading circuits.csv: {e}")
        st.stop()

@st.cache_data
def load_races():
    """Load race data"""
    try:
        races = pd.read_csv('races.csv')
        races.columns = races.columns.str.strip().str.lower()
        races['date'] = pd.to_datetime(races['date'], errors='coerce')
        return races
    except Exception as e:
        st.error(f"Error loading races.csv: {e}")
        st.stop()

@st.cache_data
def load_pit_stops():
    """Load pit stop data"""
    try:
        pit_stops = pd.read_csv('pit_stops.csv')
        pit_stops.columns = pit_stops.columns.str.strip().str.lower()
        # Convert duration to seconds if in milliseconds
        if 'milliseconds' in pit_stops.columns and 'duration' not in pit_stops.columns:
            pit_stops['duration'] = pit_stops['milliseconds'] / 1000
        return pit_stops
    except Exception as e:
        st.error(f"Error loading pit_stops.csv: {e}")
        return None

@st.cache_data
def load_constructors():
    """Load constructor data"""
    try:
        constructors = pd.read_csv('constructors.csv')
        constructors.columns = constructors.columns.str.strip().str.lower()
        return constructors
    except Exception as e:
        st.error(f"Error loading constructors.csv: {e}")
        return None

@st.cache_data
def load_results():
    """Load race results data"""
    try:
        results = pd.read_csv('results.csv')
        results.columns = results.columns.str.strip().str.lower()
        # Convert position to numeric
        results['position'] = pd.to_numeric(results['position'], errors='coerce')
        results['points'] = pd.to_numeric(results['points'], errors='coerce')
        return results
    except Exception as e:
        st.error(f"Error loading results.csv: {e}")
        return None

# Load all data
circuits = load_circuits()
races = load_races()
pit_stops = load_pit_stops()
constructors = load_constructors()
results = load_results()

# Merge datasets
races_with_circuits = races.merge(circuits, on='circuitid', how='left', suffixes=('_race', '_circuit'))

# ============================================================================
# HEADER
# ============================================================================
st.title("🏎️ F1 STRATEGY DASHBOARD")
st.markdown("### Complete Analysis: Circuits | Pit Stops | Performance")
st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.header("🎯 Dashboard Filters")

# Year filter
available_years = sorted(races['year'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    "Select Season(s):",
    options=available_years,
    default=[available_years[0]] if len(available_years) > 0 else [],
    help="Choose F1 seasons"
)

# Apply filters
if selected_years:
    filtered_races = races_with_circuits[races_with_circuits['year'].isin(selected_years)]
    filtered_races_ids = filtered_races['raceid'].unique() if 'raceid' in filtered_races.columns else []
else:
    filtered_races = races_with_circuits
    filtered_races_ids = races['raceid'].unique() if 'raceid' in races.columns else []

# Country filter
countries = sorted(circuits['country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries:",
    options=countries,
    default=[]
)

if selected_countries:
    filtered_circuits = circuits[circuits['country'].isin(selected_countries)]
    filtered_races = filtered_races[filtered_races['country'].isin(selected_countries)]
else:
    filtered_circuits = circuits

# Dashboard section selector
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Navigate Dashboard")
dashboard_section = st.sidebar.radio(
    "Jump to Section:",
    ["Overview", "Circuit Analysis", "Pit Stop Strategy", "Performance Analysis"]
)

# Summary stats
st.sidebar.markdown("---")
st.sidebar.info(f"""
📊 **Data Loaded**
- Circuits: {len(circuits)}
- Races: {len(races):,}
- Pit Stops: {len(pit_stops):,} if pit_stops is not None else "N/A"
- Results: {len(results):,} if results is not None else "N/A"
""")

# ============================================================================
# KEY METRICS ROW
# ============================================================================
st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🏁 Circuits", len(filtered_circuits))

with col2:
    st.metric("🏆 Races", f"{len(filtered_races):,}")

with col3:
    if pit_stops is not None:
        filtered_pit_stops = pit_stops[pit_stops['raceid'].isin(filtered_races_ids)]
        st.metric("🔧 Pit Stops", f"{len(filtered_pit_stops):,}")
    else:
        st.metric("🔧 Pit Stops", "N/A")

with col4:
    if results is not None:
        filtered_results = results[results['raceid'].isin(filtered_races_ids)]
        st.metric("🎯 Results", f"{len(filtered_results):,}")
    else:
        st.metric("🎯 Results", "N/A")

with col5:
    st.metric("🌍 Countries", circuits['country'].nunique())

st.markdown("---")

# ============================================================================
# PHASE 1: CIRCUIT ANALYSIS
# ============================================================================
if dashboard_section in ["Overview", "Circuit Analysis"]:
    st.header("🗺️ Phase 1: Circuit Foundation")
    
    # World Map
    st.subheader("F1 Circuits Around the World")
    races_per_circuit = filtered_races.groupby('circuitid').size().reset_index(name='race_count')
    map_data = filtered_circuits.merge(races_per_circuit, on='circuitid', how='left')
    map_data['race_count'] = map_data['race_count'].fillna(0)
    
    fig_map = px.scatter_geo(
        map_data,
        lat='lat',
        lon='lng',
        hover_name='name',
        size='race_count',
        size_max=30,
        color='country',
        projection='natural earth'
    )
    fig_map.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Circuit Analysis Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Most Raced Circuits")
        if len(filtered_races) > 0:
            top_circuits = (
                filtered_races.groupby('name_circuit')
                .size()
                .reset_index(name='races')
                .sort_values('races', ascending=False)
                .head(10)
            )
            
            fig = px.bar(
                top_circuits,
                x='races',
                y='name_circuit',
                orientation='h',
                color='races',
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌍 Races by Country")
        if len(filtered_races) > 0:
            races_by_country = (
                filtered_races.groupby('country')
                .size()
                .reset_index(name='races')
                .sort_values('races', ascending=False)
                .head(10)
            )
            
            fig = px.bar(
                races_by_country,
                x='races',
                y='country',
                orientation='h',
                color='races',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# ============================================================================
# PHASE 2: PIT STOP STRATEGY
# ============================================================================
if dashboard_section in ["Overview", "Pit Stop Strategy"] and pit_stops is not None:
    st.header("🔧 Phase 2: Pit Stop Strategy Analysis")
    
    # Filter pit stops for selected races
    filtered_pit_stops = pit_stops[pit_stops['raceid'].isin(filtered_races_ids)]
    
    if len(filtered_pit_stops) > 0:
        # Pit Stop Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_duration = filtered_pit_stops['duration'].mean()
            st.metric("⚡ Avg Pit Stop", f"{avg_duration:.3f}s")
        
        with col2:
            fastest_stop = filtered_pit_stops['duration'].min()
            st.metric("🏆 Fastest Stop", f"{fastest_stop:.3f}s")
        
        with col3:
            total_stops = len(filtered_pit_stops)
            st.metric("🔢 Total Stops", f"{total_stops:,}")
        
        with col4:
            avg_stops_per_race = len(filtered_pit_stops) / len(filtered_races_ids) if len(filtered_races_ids) > 0 else 0
            st.metric("📊 Stops/Race", f"{avg_stops_per_race:.1f}")
        
        st.markdown("---")
        
        # Analysis Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚡ Pit Stop Duration Distribution")
            fig = px.histogram(
                filtered_pit_stops[filtered_pit_stops['duration'] < 60],  # Filter outliers
                x='duration',
                nbins=50,
                labels={'duration': 'Duration (seconds)'},
                color_discrete_sequence=['#E10600']
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔢 Pit Stop Strategy")
            stop_counts = filtered_pit_stops.groupby('stop').size().reset_index(name='count')
            fig = px.bar(
                stop_counts,
                x='stop',
                y='count',
                labels={'stop': 'Stop Number', 'count': 'Frequency'},
                color='count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Analysis Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⏱️ Pit Stop Timing (Lap)")
            lap_stops = filtered_pit_stops.groupby('lap').size().reset_index(name='stops')
            fig = px.line(
                lap_stops,
                x='lap',
                y='stops',
                markers=True,
                labels={'lap': 'Lap Number', 'stops': 'Number of Stops'},
                color_discrete_sequence=['#E10600']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Pit Stop Efficiency Trend")
            # Average duration by lap
            if 'lap' in filtered_pit_stops.columns:
                efficiency = filtered_pit_stops.groupby('lap')['duration'].mean().reset_index()
                fig = px.scatter(
                    efficiency,
                    x='lap',
                    y='duration',
                    trendline="lowess",
                    labels={'lap': 'Lap Number', 'duration': 'Avg Duration (s)'},
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 Fastest Pit Stops
        st.markdown("#### 🏆 Top 10 Fastest Pit Stops")
        fastest_stops = filtered_pit_stops.nsmallest(10, 'duration')[['raceid', 'driverid', 'stop', 'lap', 'duration']]
        fastest_stops['duration'] = fastest_stops['duration'].round(3)
        st.dataframe(fastest_stops, use_container_width=True, hide_index=True)
        
    else:
        st.info("No pit stop data available for selected filters")
    
    st.markdown("---")

# ============================================================================
# PHASE 3: PERFORMANCE ANALYSIS
# ============================================================================
if dashboard_section in ["Overview", "Performance Analysis"] and results is not None and constructors is not None:
    st.header("🏁 Phase 3: Circuit-Team Performance")
    
    # Filter results for selected races
    filtered_results = results[results['raceid'].isin(filtered_races_ids)]
    
    if len(filtered_results) > 0:
        # Merge with constructors and circuits
        perf_data = filtered_results.merge(
            races[['raceid', 'circuitid', 'year']],
            on='raceid',
            how='left'
        ).merge(
            constructors[['constructorid', 'name']],
            on='constructorid',
            how='left'
        ).merge(
            circuits[['circuitid', 'name']],
            on='circuitid',
            how='left',
            suffixes=('_constructor', '_circuit')
        )
        
        # Performance Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_results = len(filtered_results)
            st.metric("📊 Total Results", f"{total_results:,}")
        
        with col2:
            total_points = filtered_results['points'].sum()
            st.metric("⭐ Total Points", f"{total_points:,.0f}")
        
        with col3:
            unique_winners = filtered_results[filtered_results['position'] == 1]['driverid'].nunique()
            st.metric("🏆 Unique Winners", unique_winners)
        
        with col4:
            unique_constructors = filtered_results['constructorid'].nunique()
            st.metric("🏗️ Teams", unique_constructors)
        
        st.markdown("---")
        
        # Analysis Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Constructors by Points")
            if 'name_constructor' in perf_data.columns:
                top_constructors = (
                    perf_data.groupby('name_constructor')['points']
                    .sum()
                    .reset_index()
                    .sort_values('points', ascending=False)
                    .head(10)
                )
                
                fig = px.bar(
                    top_constructors,
                    x='points',
                    y='name_constructor',
                    orientation='h',
                    color='points',
                    color_continuous_scale='Reds',
                    labels={'name_constructor': 'Constructor', 'points': 'Total Points'}
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Position Distribution")
            position_dist = filtered_results[filtered_results['position'] <= 10]['position'].value_counts().sort_index()
            position_df = pd.DataFrame({'position': position_dist.index, 'count': position_dist.values})
            
            fig = px.bar(
                position_df,
                x='position',
                y='count',
                labels={'position': 'Finishing Position', 'count': 'Frequency'},
                color='count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Analysis Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏎️ Constructor Performance by Circuit")
            if 'name_constructor' in perf_data.columns and 'name_circuit' in perf_data.columns:
                # Top 5 constructors
                top_5_constructors = (
                    perf_data.groupby('name_constructor')['points']
                    .sum()
                    .nlargest(5)
                    .index
                )
                
                circuit_perf = (
                    perf_data[perf_data['name_constructor'].isin(top_5_constructors)]
                    .groupby(['name_circuit', 'name_constructor'])['points']
                    .sum()
                    .reset_index()
                )
                
                # Top 10 circuits by total points
                top_circuits = (
                    circuit_perf.groupby('name_circuit')['points']
                    .sum()
                    .nlargest(10)
                    .index
                )
                
                circuit_perf_filtered = circuit_perf[circuit_perf['name_circuit'].isin(top_circuits)]
                
                fig = px.bar(
                    circuit_perf_filtered,
                    x='name_circuit',
                    y='points',
                    color='name_constructor',
                    barmode='stack',
                    labels={'name_circuit': 'Circuit', 'points': 'Points', 'name_constructor': 'Constructor'}
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Points vs Finishing Position")
            if 'position' in filtered_results.columns and 'points' in filtered_results.columns:
                pos_points = filtered_results[filtered_results['position'] <= 20].copy()
                
                fig = px.scatter(
                    pos_points,
                    x='position',
                    y='points',
                    opacity=0.6,
                    labels={'position': 'Finishing Position', 'points': 'Points Scored'},
                    color_discrete_sequence=['#E10600']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Performance Table
        st.markdown("#### 📋 Constructor Championship Standings")
        if 'name_constructor' in perf_data.columns:
            standings = (
                perf_data.groupby('name_constructor')
                .agg({
                    'points': 'sum',
                    'position': lambda x: (x == 1).sum()  # Wins
                })
                .reset_index()
            )
            standings.columns = ['Constructor', 'Total Points', 'Wins']
            standings = standings.sort_values('Total Points', ascending=False).head(15)
            standings['Total Points'] = standings['Total Points'].round(0).astype(int)
            standings['Wins'] = standings['Wins'].astype(int)
            st.dataframe(standings, use_container_width=True, hide_index=True)
    
    else:
        st.info("No performance data available for selected filters")
    
    st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p style='font-size: 1.1em; margin-bottom: 10px;'>
            🏎️ <strong>F1 Strategy Dashboard - Complete Edition</strong>
        </p>
        <p style='font-size: 0.9em;'>
            Phase 1: Circuits | Phase 2: Pit Stops | Phase 3: Performance
        </p>
        <p style='font-size: 0.8em; margin-top: 10px;'>
            Built with Streamlit & Plotly | Portfolio Project
        </p>
    </div>
    """, unsafe_allow_html=True)
