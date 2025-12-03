"""
GreenGL Studio - Carbon-Aware Job Scheduler
A Streamlit app for scheduling computational jobs to minimize carbon emissions.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import pandas as pd
import time
import random
from get_best_start_time import get_best_start_time, _generate_mock_forecast
from cats.forecast import WindowedForecast

# Page configuration
st.set_page_config(
    page_title="GreenGL Studio",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f9f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    .dirty-card {
        background-color: #fff3f3;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .clean-card {
        background-color: #f0f9f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E7D32;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

def create_comparison_graph(duration_minutes, ci_now, ci_optimal, optimal_time):
    """
    Create a comparison bar chart showing carbon intensity for 'Now' vs 'Optimal'
    
    Args:
        duration_minutes: Job duration in minutes
        ci_now: Carbon intensity if started now
        ci_optimal: Carbon intensity at optimal time
        optimal_time: Datetime of optimal start time
    """
    # Calculate CO2 emissions (assuming 300W computer)
    power_kw = 0.3
    duration_hours = duration_minutes / 60
    
    co2_now = ci_now * power_kw * duration_hours
    co2_optimal = ci_optimal * power_kw * duration_hours
    savings = co2_now - co2_optimal
    savings_percent = (savings / co2_now * 100) if co2_now > 0 else 0
    
    # Create comparison data
    categories = ['If you run NOW<br>(Dirty)', f'If you run at {optimal_time.strftime("%I:%M %p")}<br>(Clean)']
    ci_values = [ci_now, ci_optimal]
    co2_values = [co2_now, co2_optimal]
    colors = ['#f44336', '#4CAF50']  # Red for now, Green for optimal
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add carbon intensity bars
    fig.add_trace(go.Bar(
        name='Carbon Intensity',
        x=categories,
        y=ci_values,
        marker_color=colors,
        text=[f'{ci:.1f} gCO2/kWh' for ci in ci_values],
        textposition='outside',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{x}</b><br>' +
                      'Carbon Intensity: %{y:.2f} gCO2/kWh<br>' +
                      '<extra></extra>',
        yaxis='y1'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'Carbon Impact Comparison - {duration_minutes} Minute Job',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2E7D32', 'family': 'Arial Black'}
        },
        xaxis={
            'title': '',
            'tickfont': {'size': 16}
        },
        yaxis={
            'title': 'Carbon Intensity (gCO2eq/kWh)',
            'titlefont': {'size': 16},
            'tickfont': {'size': 14}
        },
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    # Add gridlines
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig, co2_now, co2_optimal, savings, savings_percent


def create_forecast_chart_with_zones(duration_minutes, optimal_time):
    """
    Create a line chart showing the 24-hour carbon intensity forecast
    with RED ZONE (dirty) and GREEN ZONE (clean) highlighting
    """
    forecast = _generate_mock_forecast()
    
    # Extract data for plotting
    times = [point.datetime for point in forecast[:48]]  # 24 hours
    intensities = [point.value for point in forecast[:48]]
    
    # Define thresholds for red/green zones
    DIRTY_THRESHOLD = 180  # Above this = RED ZONE
    CLEAN_THRESHOLD = 120  # Below this = GREEN ZONE
    
    # Create figure
    fig = go.Figure()
    
    # Add red zone background (high carbon intensity)
    fig.add_hrect(
        y0=DIRTY_THRESHOLD,
        y1=max(intensities) + 20,
        fillcolor='rgba(244, 67, 54, 0.1)',
        layer='below',
        line_width=0,
        annotation_text='🔴 RED ZONE (Dirty Grid)',
        annotation_position='top right'
    )
    
    # Add green zone background (low carbon intensity)
    fig.add_hrect(
        y0=0,
        y1=CLEAN_THRESHOLD,
        fillcolor='rgba(76, 175, 80, 0.1)',
        layer='below',
        line_width=0,
        annotation_text='🟢 GREEN ZONE (Clean Grid)',
        annotation_position='bottom right'
    )
    
    # Add yellow zone (moderate)
    fig.add_hrect(
        y0=CLEAN_THRESHOLD,
        y1=DIRTY_THRESHOLD,
        fillcolor='rgba(255, 193, 7, 0.05)',
        layer='below',
        line_width=0,
        annotation_text='🟡 MODERATE',
        annotation_position='right'
    )
    
    # Color the line based on zones
    colors = []
    for intensity in intensities:
        if intensity < CLEAN_THRESHOLD:
            colors.append('#4CAF50')  # Green
        elif intensity > DIRTY_THRESHOLD:
            colors.append('#f44336')  # Red
        else:
            colors.append('#FFC107')  # Yellow
    
    # Add forecast line with gradient effect
    fig.add_trace(go.Scatter(
        x=times,
        y=intensities,
        mode='lines+markers',
        name='Carbon Intensity',
        line=dict(color='#2196F3', width=4),
        marker=dict(
            size=6,
            color=colors,
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{x|%H:%M}</b><br>' +
                      'CI: %{y:.1f} gCO2/kWh<br>' +
                      '<extra></extra>'
    ))
    
    # Highlight optimal window with a more prominent style
    optimal_end = optimal_time + timedelta(minutes=duration_minutes)
    fig.add_vrect(
        x0=optimal_time,
        x1=optimal_end,
        fillcolor='rgba(76, 175, 80, 0.25)',
        layer='above',
        line=dict(width=2, color='#2E7D32', dash='dash'),
        annotation_text='✨ OPTIMAL WINDOW ✨',
        annotation_position='top left',
        annotation=dict(font=dict(size=12, color='#1B5E20', family='Arial Black'))
    )
    
    # Add marker for current time
    now = datetime.now(timezone.utc)
    fig.add_shape(
        type='line',
        x0=now,
        x1=now,
        y0=0,
        y1=1,
        yref='paper',
        line=dict(
            color='red',
            width=3,
            dash='dash'
        )
    )
    fig.add_annotation(
        x=now,
        y=1,
        yref='paper',
        text='⏰ NOW',
        showarrow=False,
        yshift=10,
        font=dict(size=12, color='red', family='Arial Black')
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '🌍 Grid Carbon Forecast - Next 24 Hours',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#2E7D32', 'family': 'Arial Black'}
        },
        xaxis={
            'title': 'Time',
            'titlefont': {'size': 14}
        },
        yaxis={
            'title': 'Carbon Intensity (gCO2eq/kWh)',
            'titlefont': {'size': 14}
        },
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.3)')
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.3)')
    
    return fig


def generate_simulation_logs(optimal_time, ci_now, ci_optimal, duration_minutes):
    """
    Generate fake console logs showing the scheduler in action
    """
    now = datetime.now(timezone.utc).astimezone()
    optimal_local = optimal_time.astimezone()
    
    logs = []
    
    # Initial logs
    logs.append(f"[{now.strftime('%I:%M %p')}] 🚀 GreenGL Scheduler initialized")
    logs.append(f"[{now.strftime('%I:%M %p')}] 📊 Analyzing grid carbon intensity...")
    logs.append(f"[{now.strftime('%I:%M %p')}] ⚡ Current grid status: {ci_now:.0f} gCO2/kWh")
    
    # Decision logic
    if ci_now > 180:
        logs.append(f"[{now.strftime('%I:%M %p')}] 🔴 WARNING: Grid is DIRTY ({ci_now:.0f}g/kWh)")
        logs.append(f"[{now.strftime('%I:%M %p')}] ⏸️  Job execution PAUSED (fossil fuel heavy)")
        logs.append(f"[{now.strftime('%I:%M %p')}] 💤 Putting GPU to sleep...")
    else:
        logs.append(f"[{now.strftime('%I:%M %p')}] 🟡 Grid is MODERATE ({ci_now:.0f}g/kWh)")
        logs.append(f"[{now.strftime('%I:%M %p')}] ⚠️  Can run now, but not optimal")
    
    logs.append(f"[{now.strftime('%I:%M %p')}] 🔍 Scanning next 24 hours for clean energy...")
    logs.append(f"[{now.strftime('%I:%M %p')}] ✨ Found optimal window: {optimal_local.strftime('%I:%M %p')}")
    logs.append(f"[{now.strftime('%I:%M %p')}] 🟢 Expected CI: {ci_optimal:.0f}g/kWh (CLEAN ENERGY!)")
    
    # Calculate delay
    delay = optimal_time - datetime.now(timezone.utc)
    delay_hours = delay.total_seconds() / 3600
    
    if delay_hours > 1:
        logs.append(f"[{now.strftime('%I:%M %p')}] ⏰ Scheduling job for {optimal_local.strftime('%I:%M %p')} ({delay_hours:.1f}h delay)")
        logs.append(f"[{now.strftime('%I:%M %p')}] 💾 Job state saved to disk")
        logs.append(f"[{now.strftime('%I:%M %p')}] 📅 Wake-up alarm set")
        
        # Simulated future log
        logs.append("")
        logs.append(f"[{optimal_local.strftime('%I:%M %p')}] ⏰ WAKE UP! Optimal window reached")
        logs.append(f"[{optimal_local.strftime('%I:%M %p')}] 🌞 Grid powered by RENEWABLES")
        logs.append(f"[{optimal_local.strftime('%I:%M %p')}] 🚀 Waking up GPU...")
        logs.append(f"[{optimal_local.strftime('%I:%M %p')}] ⚡ Resuming job execution")
        logs.append(f"[{optimal_local.strftime('%I:%M %p')}] 🎯 Running at {ci_optimal:.0f}g/kWh (optimal!)")
    else:
        logs.append(f"[{now.strftime('%I:%M %p')}] 🚀 Optimal window is NOW! Starting job...")
        logs.append(f"[{now.strftime('%I:%M %p')}] ⚡ GPU at full power")
    
    # Completion estimate
    end_time = optimal_local + timedelta(minutes=duration_minutes)
    logs.append(f"[{optimal_local.strftime('%I:%M %p')}] 📊 Job progress: 0% → 100%")
    logs.append(f"[{end_time.strftime('%I:%M %p')}] ✅ Job completed successfully!")
    
    # Savings
    power_kw = 0.3
    duration_hours = duration_minutes / 60
    co2_now = ci_now * power_kw * duration_hours
    co2_optimal = ci_optimal * power_kw * duration_hours
    savings = co2_now - co2_optimal
    
    logs.append(f"[{end_time.strftime('%I:%M %p')}] 🌱 Carbon saved: {savings:.1f}g CO2")
    logs.append(f"[{end_time.strftime('%I:%M %p')}] 🎉 Efficiency: {((savings/co2_now)*100):.0f}% reduction")
    logs.append(f"[{end_time.strftime('%I:%M %p')}] 💚 Thank you for being carbon-aware!")
    
    return logs


def main():
    # Header
    st.markdown('<div class="main-header">🌱 GreenGL Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Carbon-Aware Job Scheduler - Run your code when the grid is greenest</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/2E7D32/FFFFFF?text=GreenGL+Studio", use_container_width=True)
        st.markdown("### About")
        st.info(
            "GreenGL Studio helps you schedule computational jobs to minimize carbon emissions. "
            "Upload your Python script, set the duration, and we'll find the greenest time to run it!"
        )
        
        st.markdown("### Carbon Intensity Guide")
        st.markdown("""
        - 🟢 **< 100**: Excellent (High renewables)
        - 🟡 **100-150**: Good (Moderate mix)
        - 🟠 **150-200**: Fair (Balanced)
        - 🔴 **> 200**: Poor (Fossil heavy)
        """)
        
        st.markdown("### Tips")
        st.success(
            "💡 Night hours (2-6 AM) typically have the lowest carbon intensity due to high renewable energy availability."
        )
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Step 1: Upload Your Script")
        uploaded_file = st.file_uploader(
            "Choose a Python file (.py)",
            type=['py'],
            help="Upload the Python script you want to schedule"
        )
        
        if uploaded_file is not None:
            # Display file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB",
                "File type": uploaded_file.type
            }
            st.success(f"✅ Loaded: {uploaded_file.name}")
            
            # Show file preview
            with st.expander("📄 Preview Script"):
                file_content = uploaded_file.read().decode('utf-8')
                st.code(file_content, language='python')
                # Reset file pointer
                uploaded_file.seek(0)
    
    with col2:
        st.markdown("### ⏱️ Step 2: Set Job Duration")
        duration_minutes = st.slider(
            "Select expected job duration (minutes)",
            min_value=15,
            max_value=480,
            value=60,
            step=15,
            help="Estimate how long your script will take to run"
        )
        
        # Display duration in human-readable format
        hours = duration_minutes // 60
        mins = duration_minutes % 60
        duration_text = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
        st.info(f"⏰ Job duration: **{duration_text}**")
        
        # Optional: Search window
        with st.expander("⚙️ Advanced Options"):
            search_window = st.slider(
                "Search window (hours ahead)",
                min_value=6,
                max_value=47,
                value=24,
                help="How far ahead to search for optimal time"
            )
    
    # Schedule button
    st.markdown("---")
    st.markdown("### 🚀 Step 3: Schedule Your Job")
    
    col_button1, col_button2, col_button3 = st.columns([1, 2, 1])
    with col_button2:
        schedule_button = st.button("🌍 Schedule Job", use_container_width=True)
    
    # Results section
    if schedule_button:
        if uploaded_file is None:
            st.error("⚠️ Please upload a Python file first!")
        else:
            with st.spinner("🔍 Finding the greenest time to run your job..."):
                # Get optimal schedule
                try:
                    optimal_time, ci_optimal = get_best_start_time(
                        duration_minutes=duration_minutes,
                        max_window_hours=search_window if 'search_window' in locals() else 24
                    )
                    
                    # Get current CI
                    forecast = _generate_mock_forecast()
                    wf = WindowedForecast(forecast, duration_minutes, datetime.now(timezone.utc))
                    ci_now = wf[0].value
                    
                    # Store in session state
                    st.session_state.results = {
                        'optimal_time': optimal_time,
                        'ci_optimal': ci_optimal,
                        'ci_now': ci_now,
                        'duration_minutes': duration_minutes,
                        'filename': uploaded_file.name
                    }
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    return
    
    # Display results if available
    if 'results' in st.session_state:
        results = st.session_state.results
        
        st.markdown("---")
        st.markdown("## 📊 Scheduling Results")
        
        # Key metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        optimal_local = results['optimal_time'].astimezone()
        delay = results['optimal_time'] - datetime.now(timezone.utc)
        delay_hours = delay.total_seconds() / 3600
        
        with col_m1:
            st.metric(
                label="🕐 Optimal Start Time",
                value=optimal_local.strftime("%I:%M %p"),
                delta=f"{optimal_local.strftime('%b %d')}"
            )
        
        with col_m2:
            st.metric(
                label="⏳ Recommended Delay",
                value=f"{int(delay_hours)}h {int((delay_hours % 1) * 60)}m",
                delta="Wait time" if delay_hours > 0 else "Start now"
            )
        
        with col_m3:
            savings_percent = ((results['ci_now'] - results['ci_optimal']) / results['ci_now'] * 100)
            st.metric(
                label="💰 Carbon Savings",
                value=f"{savings_percent:.1f}%",
                delta=f"{results['ci_now'] - results['ci_optimal']:.1f} gCO2/kWh"
            )
        
        with col_m4:
            if results['ci_optimal'] < 100:
                rating = "🟢 Excellent"
            elif results['ci_optimal'] < 150:
                rating = "🟡 Good"
            elif results['ci_optimal'] < 200:
                rating = "🟠 Fair"
            else:
                rating = "🔴 Poor"
            
            st.metric(
                label="📈 Optimal CI Rating",
                value=rating,
                delta=f"{results['ci_optimal']:.1f} gCO2/kWh"
            )
        
        # Comparison graph
        st.markdown("### 🔄 Dirty vs Clean Comparison")
        fig_comparison, co2_now, co2_optimal, savings, savings_percent = create_comparison_graph(
            results['duration_minutes'],
            results['ci_now'],
            results['ci_optimal'],
            optimal_local
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Detailed comparison cards
        col_card1, col_card2 = st.columns(2)
        
        with col_card1:
            st.markdown('<div class="dirty-card">', unsafe_allow_html=True)
            st.markdown("#### 🔴 If you run NOW (Dirty)")
            st.markdown(f"""
            - **Carbon Intensity**: {results['ci_now']:.2f} gCO2eq/kWh
            - **Estimated CO2**: {co2_now:.2f}g
            - **Status**: ⚠️ Higher emissions
            - **Grid**: Likely fossil fuel heavy
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_card2:
            st.markdown('<div class="clean-card">', unsafe_allow_html=True)
            st.markdown(f"#### 🟢 If you run at {optimal_local.strftime('%I:%M %p')} (Clean)")
            st.markdown(f"""
            - **Carbon Intensity**: {results['ci_optimal']:.2f} gCO2eq/kWh
            - **Estimated CO2**: {co2_optimal:.2f}g
            - **Savings**: ✅ {savings:.2f}g CO2 ({savings_percent:.1f}%)
            - **Grid**: More renewable energy
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Impact statement
        st.markdown("---")
        st.markdown("### 🌍 Environmental Impact")
        
        if savings_percent > 50:
            impact_emoji = "🎉"
            impact_text = "Excellent! Scheduling at this time will significantly reduce your carbon footprint."
        elif savings_percent > 25:
            impact_emoji = "👍"
            impact_text = "Great! You'll make a meaningful reduction in carbon emissions."
        elif savings_percent > 10:
            impact_emoji = "✓"
            impact_text = "Good! Every bit of carbon saved helps the environment."
        else:
            impact_emoji = "ℹ️"
            impact_text = "Current time is already quite optimal. Minor savings available."
        
        st.success(f"{impact_emoji} {impact_text}")
        
        # Annual impact if run daily
        daily_savings = savings
        annual_savings = daily_savings * 365
        st.info(
            f"💡 **Annual Impact**: If you run this job daily at the optimal time, "
            f"you could save approximately **{annual_savings:.1f}g CO2 per year** "
            f"(~{annual_savings/1000:.2f} kg CO2)"
        )
        
        # Forecast chart with zones
        st.markdown("---")
        st.markdown("### 📈 Grid Carbon Forecast - Red Zone vs Green Zone")
        st.markdown("*Watch how carbon intensity changes throughout the day*")
        fig_forecast = create_forecast_chart_with_zones(results['duration_minutes'], results['optimal_time'])
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Live Simulation Console
        st.markdown("---")
        st.markdown("### 🖥️ Live Scheduler Console")
        st.markdown("*See how GreenGL orchestrates your job for maximum carbon efficiency*")
        
        # Create console-like container
        console_container = st.container()
        with console_container:
            st.markdown("""
            <style>
                .console-box {
                    background-color: #0a0a0a;
                    color: #00ff00;
                    padding: 20px;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 14px;
                    max-height: 400px;
                    overflow-y: auto;
                    border: 2px solid #00ff00;
                    box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
                }
                .console-log {
                    margin: 5px 0;
                    line-height: 1.6;
                }
                .console-header {
                    color: #00ffff;
                    font-weight: bold;
                    border-bottom: 1px solid #00ff00;
                    padding-bottom: 10px;
                    margin-bottom: 10px;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Generate and display logs
            logs = generate_simulation_logs(
                results['optimal_time'],
                results['ci_now'],
                results['ci_optimal'],
                results['duration_minutes']
            )
            
            console_html = '<div class="console-box">'
            console_html += '<div class="console-header">🌿 GreenGL Scheduler v1.0 - Carbon-Aware GPU Orchestration</div>'
            
            for log in logs:
                if log == "":
                    console_html += '<div class="console-log">&nbsp;</div>'
                else:
                    console_html += f'<div class="console-log">{log}</div>'
            
            console_html += '</div>'
            st.markdown(console_html, unsafe_allow_html=True)
        
        # Add "typing" animation effect for wow factor
        if st.button("🎬 Replay Simulation", use_container_width=False):
            replay_container = st.empty()
            displayed_logs = []
            
            for log in logs:
                if log != "":
                    displayed_logs.append(log)
                    console_html = '<div class="console-box">'
                    console_html += '<div class="console-header">🌿 GreenGL Scheduler v1.0 - Live Simulation</div>'
                    for displayed_log in displayed_logs:
                        console_html += f'<div class="console-log">{displayed_log}</div>'
                    console_html += '</div>'
                    replay_container.markdown(console_html, unsafe_allow_html=True)
                    time.sleep(0.3)  # Typing effect delay
        
        # Action buttons
        st.markdown("---")
        col_action1, col_action2, col_action3 = st.columns([1, 1, 1])
        
        with col_action1:
            if st.button("📅 Export Schedule", use_container_width=True):
                schedule_text = f"""
GreenGL Studio - Job Schedule
================================
File: {results['filename']}
Duration: {results['duration_minutes']} minutes
Optimal Start: {optimal_local.strftime('%Y-%m-%d %H:%M:%S %Z')}
Carbon Intensity: {results['ci_optimal']:.2f} gCO2eq/kWh
Expected CO2: {co2_optimal:.2f}g
Savings vs Now: {savings:.2f}g ({savings_percent:.1f}%)
================================
Generated by GreenGL Studio
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                st.download_button(
                    label="Download Schedule",
                    data=schedule_text,
                    file_name=f"schedule_{results['filename']}.txt",
                    mime="text/plain"
                )
        
        with col_action2:
            if st.button("🔄 Schedule Another Job", use_container_width=True):
                del st.session_state.results
                st.rerun()
        
        with col_action3:
            if st.button("ℹ️ Learn More", use_container_width=True):
                st.info(
                    "GreenGL Studio uses real-time carbon intensity forecasts to schedule "
                    "computational jobs during periods of lower emissions. By running jobs "
                    "when renewable energy is more available, you can significantly reduce "
                    "your carbon footprint without changing your code!"
                )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🌱 GreenGL Studio | Powered by CATS (Climate-Aware Task Scheduler) | "
        f"Making computing greener, one job at a time"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
