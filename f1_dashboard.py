"""
F1 STRATEGY DASHBOARD - Phase 1: Circuit Foundation
Interactive F1 analytics focusing on circuits and race strategy
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
# LOAD DATA WITH ROBUST ERROR HANDLING
# ============================================================================
@st.cache_data
def load_circuits():
    """Load and clean circuit data"""
    try:
        circuits = pd.read_csv('circuits.csv')
        
        # Clean column names - remove extra spaces and standardize
        circuits.columns = circuits.columns.str.strip().str.lower()
        
        # Show columns for debugging
        st.sidebar.write("🔍 Circuits columns:", list(circuits.columns))
        
        # Check for required columns
        required_cols = ['circuitid', 'name', 'location', 'country', 'lat', 'lng']
        missing = [col for col in required_cols if col not in circuits.columns]
        
        if missing:
            st.error(f"❌ Missing columns in circuits.csv: {missing}")
            st.error(f"Available columns: {list(circuits.columns)}")
            st.stop()
        
        # Remove circuits without coordinates
        circuits = circuits.dropna(subset=['lat', 'lng'])
        
        return circuits
    except FileNotFoundError:
        st.error("❌ circuits.csv not found! Please upload the file to your repository.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading circuits.csv: {e}")
        st.stop()

@st.cache_data
def load_races():
    """Load and clean race data"""
    try:
        races = pd.read_csv('races.csv')
        
        # Clean column names - remove extra spaces and standardize
        races.columns = races.columns.str.strip().str.lower()
        
        # Show columns for debugging
        st.sidebar.write("🔍 Races columns:", list(races.columns))
        
        # Check for required columns
        required_cols = ['raceid', 'year', 'circuitid', 'name', 'date']
        missing = [col for col in required_cols if col not in races.columns]
        
        if missing:
            st.error(f"❌ Missing columns in races.csv: {missing}")
            st.error(f"Available columns: {list(races.columns)}")
            st.stop()
        
        # Convert date to datetime
        races['date'] = pd.to_datetime(races['date'], errors='coerce')
        
        return races
    except FileNotFoundError:
        st.error("❌ races.csv not found! Please upload the file to your repository.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading races.csv: {e}")
        st.stop()

# Load data
circuits = load_circuits()
races = load_races()

# Merge circuits with races to get complete info
races_with_circuits = races.merge(
    circuits, 
    on='circuitid',  # Now using lowercase
    how='left', 
    suffixes=('_race', '_circuit')
)

# ============================================================================
# HEADER
# ============================================================================
st.title("🏎️ F1 STRATEGY DASHBOARD")
st.markdown("### Circuit Analysis & Strategic Insights")
st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.header("🎯 Filters")
st.sidebar.markdown("Customize your analysis")

# Year filter
available_years = sorted(races['year'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    "Select Season(s):",
    options=available_years,
    default=[available_years[0]] if len(available_years) > 0 else [],
    help="Choose F1 seasons to analyze"
)

# Apply year filter
if selected_years:
    filtered_races = races_with_circuits[races_with_circuits['year'].isin(selected_years)]
else:
    filtered_races = races_with_circuits

# Country filter
countries = sorted(circuits['country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Country/Countries:",
    options=countries,
    default=[],
    help="Filter circuits by country"
)

if selected_countries:
    filtered_circuits = circuits[circuits['country'].isin(selected_countries)]
    filtered_races = filtered_races[filtered_races['country'].isin(selected_countries)]
else:
    filtered_circuits = circuits

# Info box
st.sidebar.markdown("---")
st.sidebar.info(f"""
📊 **Data Summary**
- **Total Circuits:** {len(circuits)}
- **Countries:** {circuits['country'].nunique()}
- **Years:** {int(races['year'].min())} - {int(races['year'].max())}
- **Total Races:** {len(races):,}
""")

# ============================================================================
# KEY METRICS ROW
# ============================================================================
st.subheader("📊 Key Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_circuits = len(filtered_circuits)
    st.metric(
        label="🏁 Circuits",
        value=total_circuits,
        help="Total number of F1 circuits"
    )

with col2:
    countries_count = filtered_circuits['country'].nunique()
    st.metric(
        label="🌍 Countries",
        value=countries_count,
        help="Countries hosting F1 races"
    )

with col3:
    total_races = len(filtered_races)
    st.metric(
        label="🏆 Races",
        value=f"{total_races:,}",
        help="Total races in selected period"
    )

with col4:
    if len(filtered_races) > 0:
        avg_races_per_year = filtered_races.groupby('year').size().mean()
        st.metric(
            label="📅 Avg Races/Year",
            value=f"{avg_races_per_year:.1f}",
            help="Average races per season"
        )
    else:
        st.metric(label="📅 Avg Races/Year", value="N/A")

with col5:
    if len(filtered_races) > 0:
        most_races_circuit = filtered_races.groupby('name_circuit').size().idxmax()
        most_races_count = filtered_races.groupby('name_circuit').size().max()
        st.metric(
            label="⭐ Most Races",
            value=int(most_races_count),
            help=f"Circuit: {most_races_circuit}"
        )
    else:
        st.metric(label="⭐ Most Races", value="N/A")

st.markdown("---")

# ============================================================================
# WORLD MAP - INTERACTIVE CIRCUIT LOCATIONS
# ============================================================================
st.subheader("🗺️ F1 Circuits Around the World")

# Count races per circuit for sizing
races_per_circuit = filtered_races.groupby('circuitid').size().reset_index(name='race_count')
map_data = filtered_circuits.merge(races_per_circuit, on='circuitid', how='left')
map_data['race_count'] = map_data['race_count'].fillna(0)

# Create hover text
map_data['hover_text'] = (
    '<b>' + map_data['name'] + '</b><br>' +
    map_data['location'] + ', ' + map_data['country']
)

# Create world map
fig_map = px.scatter_geo(
    map_data,
    lat='lat',
    lon='lng',
    hover_name='name',
    hover_data={
        'country': True,
        'location': True,
        'race_count': True,
        'lat': False,
        'lng': False
    },
    size='race_count',
    size_max=30,
    color='country',
    title='',
    projection='natural earth'
)

fig_map.update_layout(
    height=500,
    geo=dict(
        showland=True,
        landcolor='rgb(243, 243, 243)',
        coastlinecolor='rgb(204, 204, 204)',
        showocean=True,
        oceancolor='rgb(230, 245, 255)',
        showcountries=True,
        countrycolor='rgb(204, 204, 204)'
    ),
    showlegend=False
)

st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ============================================================================
# ROW: CIRCUIT ANALYSIS
# ============================================================================
st.subheader("🏁 Circuit Insights")

col1, col2 = st.columns(2)

with col1:
    # Top 10 circuits by number of races
    st.markdown("#### 🏆 Most Raced Circuits")
    
    if len(filtered_races) > 0:
        top_circuits = (
            filtered_races.groupby('name_circuit')
            .size()
            .reset_index(name='races')
            .sort_values('races', ascending=False)
            .head(10)
        )
        
        fig_top_circuits = px.bar(
            top_circuits,
            x='races',
            y='name_circuit',
            orientation='h',
            labels={'races': 'Number of Races', 'name_circuit': 'Circuit'},
            color='races',
            color_continuous_scale='Reds'
        )
        fig_top_circuits.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_top_circuits, use_container_width=True)
    else:
        st.info("No data available for selected filters")

with col2:
    # Races by country
    st.markdown("#### 🌍 Races by Country")
    
    if len(filtered_races) > 0:
        races_by_country = (
            filtered_races.groupby('country')
            .size()
            .reset_index(name='races')
            .sort_values('races', ascending=False)
            .head(10)
        )
        
        fig_countries = px.bar(
            races_by_country,
            x='races',
            y='country',
            orientation='h',
            labels={'races': 'Number of Races', 'country': 'Country'},
            color='races',
            color_continuous_scale='Blues'
        )
        fig_countries.update_layout(
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_countries, use_container_width=True)
    else:
        st.info("No data available for selected filters")

st.markdown("---")

# ============================================================================
# TIMELINE - RACES PER YEAR
# ============================================================================
st.subheader("📈 F1 Calendar Evolution")

if len(filtered_races) > 0:
    races_per_year = (
        filtered_races.groupby('year')
        .size()
        .reset_index(name='races')
        .sort_values('year')
    )
    
    fig_timeline = px.line(
        races_per_year,
        x='year',
        y='races',
        markers=True,
        labels={'year': 'Year', 'races': 'Number of Races'},
        title='Number of Races per Season'
    )
    fig_timeline.update_traces(
        line_color='#E10600',
        line_width=3,
        marker=dict(size=8, color='#E10600')
    )
    fig_timeline.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("No data available for selected filters")

st.markdown("---")

# ============================================================================
# DETAILED CIRCUIT TABLE
# ============================================================================
st.subheader("📋 Circuit Details")

# Prepare display data
display_circuits = filtered_circuits[['name', 'location', 'country', 'lat', 'lng']].copy()

# Add altitude if available
if 'alt' in filtered_circuits.columns:
    display_circuits['alt'] = filtered_circuits['alt']
    display_circuits.columns = ['Circuit Name', 'Location', 'Country', 'Latitude', 'Longitude', 'Altitude (m)']
else:
    display_circuits.columns = ['Circuit Name', 'Location', 'Country', 'Latitude', 'Longitude']

# Add race count
circuit_race_counts = filtered_races.groupby('circuitid').size().reset_index(name='Total Races')
display_circuits = display_circuits.merge(
    circuits[['name', 'circuitid']], 
    left_on='Circuit Name', 
    right_on='name', 
    how='left'
).merge(circuit_race_counts, on='circuitid', how='left')
display_circuits['Total Races'] = display_circuits['Total Races'].fillna(0).astype(int)
display_circuits = display_circuits.drop(['name', 'circuitid'], axis=1)

# Sort by total races
display_circuits = display_circuits.sort_values('Total Races', ascending=False)

st.dataframe(
    display_circuits,
    use_container_width=True,
    hide_index=True,
    height=400
)

# ============================================================================
# INSIGHTS SECTION
# ============================================================================
st.markdown("---")
st.subheader("💡 Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    if len(filtered_circuits) > 0 and 'alt' in filtered_circuits.columns:
        # Highest altitude circuit
        highest_circuit = filtered_circuits.loc[filtered_circuits['alt'].idxmax()]
        st.info(f"""
        **⛰️ Highest Elevation**
        
        **{highest_circuit['name']}**
        
        {highest_circuit['location']}, {highest_circuit['country']}
        
        Altitude: {highest_circuit['alt']:,}m
        """)
    else:
        st.info("**⛰️ Altitude data not available**")

with col2:
    if len(filtered_races) > 0:
        # Most races in a single year
        races_per_year_temp = filtered_races.groupby('year').size().reset_index(name='races')
        max_races_year = races_per_year_temp.loc[races_per_year_temp['races'].idxmax()]
        st.success(f"""
        **📅 Most Races in a Season**
        
        **{int(max_races_year['year'])}**
        
        Total races: {int(max_races_year['races'])}
        
        Busiest F1 calendar!
        """)
    else:
        st.success("**📅 Select filters to see insights**")

with col3:
    if len(filtered_circuits) > 0:
        # Geographic spread
        lat_range = filtered_circuits['lat'].max() - filtered_circuits['lat'].min()
        st.warning(f"""
        **🌍 Geographic Spread**
        
        **{countries_count} Countries**
        
        Latitude range: {lat_range:.1f}°
        
        Truly global sport!
        """)
    else:
        st.warning("**🌍 Select filters to see insights**")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p style='font-size: 1.1em; margin-bottom: 10px;'>
            🏎️ <strong>F1 Strategy Dashboard - Phase 1: Circuit Foundation</strong>
        </p>
        <p style='font-size: 0.9em;'>
            Built with Streamlit & Plotly | Next: Pit Stop Strategy Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
