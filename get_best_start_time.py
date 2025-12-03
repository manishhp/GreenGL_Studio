"""
Simple function to get the best start time for a job using CATS internal logic.
This module uses mocked API responses to avoid requiring an API key.
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple
from cats.forecast import CarbonIntensityPointEstimate, WindowedForecast


def _generate_mock_forecast() -> list[CarbonIntensityPointEstimate]:
    """
    Generate a mock carbon intensity forecast for the next 48 hours.
    
    This simulates realistic carbon intensity patterns:
    - Low intensity during night hours (2-6 AM): 80-120 gCO2/kWh
    - Medium intensity during day (7 AM-5 PM): 150-200 gCO2/kWh
    - High intensity during evening peak (6-10 PM): 220-280 gCO2/kWh
    - Returns to low overnight
    
    Returns:
        List of CarbonIntensityPointEstimate objects covering 48 hours in 30-minute intervals
    """
    start_time = datetime.now(timezone.utc)
    # Round to nearest half hour
    if start_time.minute < 30:
        start_time = start_time.replace(minute=0, second=0, microsecond=0)
    else:
        start_time = start_time.replace(minute=30, second=0, microsecond=0)
    
    forecast = []
    
    # Generate 96 data points (48 hours in 30-minute intervals)
    for i in range(96):
        timestamp = start_time + timedelta(minutes=30 * i)
        hour = timestamp.hour
        
        # Simulate realistic carbon intensity patterns
        if 2 <= hour < 6:
            # Night: low carbon intensity (renewable energy dominates)
            base_intensity = 90
            variation = 20
        elif 6 <= hour < 9:
            # Morning: ramping up
            base_intensity = 150
            variation = 30
        elif 9 <= hour < 17:
            # Day: moderate intensity
            base_intensity = 180
            variation = 40
        elif 17 <= hour < 22:
            # Evening peak: high intensity
            base_intensity = 250
            variation = 30
        else:
            # Late evening: decreasing
            base_intensity = 140
            variation = 30
        
        # Add some pseudo-random variation based on the hour
        intensity = base_intensity + (i % 7 - 3) * (variation / 10)
        
        forecast.append(
            CarbonIntensityPointEstimate(
                value=intensity,
                datetime=timestamp
            )
        )
    
    return forecast


def get_best_start_time(
    duration_minutes: int,
    region: str = "GB",
    max_window_hours: int = 24
) -> Tuple[datetime, float]:
    """
    Find the optimal start time for a job to minimize carbon emissions.
    
    This function uses the CATS internal logic to find the best time window
    to run a job based on predicted carbon intensity of the electricity grid.
    The API response is mocked to avoid requiring an API key.
    
    Args:
        duration_minutes: Expected duration of the job in minutes
        region: Geographic region (currently only "GB" supported, parameter kept for API compatibility)
        max_window_hours: Maximum hours to look ahead for optimal time (default: 24, max: 47)
    
    Returns:
        Tuple containing:
        - datetime: The optimal start time (timezone-aware datetime object)
        - float: The average carbon intensity (gCO2eq/kWh) during that time window
    
    Raises:
        ValueError: If duration_minutes is invalid or window constraints are not met
    
    Example:
        >>> start_time, carbon_intensity = get_best_start_time(duration_minutes=60, region="GB")
        >>> print(f"Best start time: {start_time}")
        >>> print(f"Carbon intensity: {carbon_intensity:.2f} gCO2eq/kWh")
    """
    
    # Validate inputs
    if duration_minutes < 1:
        raise ValueError("Duration must be at least 1 minute")
    
    max_window_minutes = max_window_hours * 60
    if max_window_minutes < 1 or max_window_minutes > 2820:
        raise ValueError("Window must be between 1 and 2820 minutes (47 hours)")
    
    if duration_minutes > max_window_minutes:
        raise ValueError(
            f"Job duration ({duration_minutes} minutes) exceeds specified window "
            f"({max_window_minutes} minutes)"
        )
    
    # Note: region parameter is kept for API compatibility but currently ignored
    # as we're mocking UK data
    if region != "GB":
        print(f"Warning: Only GB region is currently supported. Using GB data.")
    
    # Generate mock forecast data
    forecast = _generate_mock_forecast()
    
    # Get current time
    current_time = datetime.now(timezone.utc)
    
    # Create windowed forecast to find optimal start time
    # This uses the CATS WindowedForecast class which:
    # 1. Divides the forecast into overlapping windows of the job duration
    # 2. Calculates the average carbon intensity for each window
    # 3. Allows us to find the window with minimum carbon intensity
    windowed_forecast = WindowedForecast(
        data=forecast,
        duration=duration_minutes,
        start=current_time,
        max_window_minutes=max_window_minutes
    )
    
    # Find the window with the minimum average carbon intensity
    # The WindowedForecast class makes each window comparable based on
    # the average carbon intensity value
    best_window = min(windowed_forecast)
    
    # Return the start time and average carbon intensity
    return best_window.start, best_window.value


def print_schedule_info(duration_minutes: int, region: str = "GB", max_window_hours: int = 24):
    """
    Print formatted information about the optimal job schedule.
    
    This is a convenience function that calls get_best_start_time() and
    displays the results in a human-readable format.
    
    Args:
        duration_minutes: Expected duration of the job in minutes
        region: Geographic region (default: "GB")
        max_window_hours: Maximum hours to look ahead (default: 24)
    """
    try:
        start_time, carbon_intensity = get_best_start_time(
            duration_minutes, region, max_window_hours
        )
        
        # Convert to local timezone for display
        local_start = start_time.astimezone()
        
        # Calculate time until job should start
        now = datetime.now(timezone.utc)
        delay = start_time - now
        
        print("\n" + "="*60)
        print("OPTIMAL JOB SCHEDULE")
        print("="*60)
        print(f"Job duration:        {duration_minutes} minutes")
        print(f"Search window:       {max_window_hours} hours")
        print(f"Region:              {region}")
        print("-"*60)
        print(f"Optimal start time:  {local_start.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Carbon intensity:    {carbon_intensity:.2f} gCO2eq/kWh")
        
        if delay.total_seconds() > 60:
            hours = int(delay.total_seconds() // 3600)
            minutes = int((delay.total_seconds() % 3600) // 60)
            print(f"Delay recommended:   {hours}h {minutes}m")
        else:
            print(f"Delay recommended:   Start now (or ASAP)")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example usage
    print("Example 1: 60-minute job")
    print_schedule_info(duration_minutes=60, region="GB", max_window_hours=24)
    
    print("\nExample 2: 120-minute job with shorter search window")
    print_schedule_info(duration_minutes=120, region="GB", max_window_hours=12)
    
    print("\nExample 3: Using the function directly")
    start_time, carbon_intensity = get_best_start_time(duration_minutes=30, region="GB")
    print(f"Best time to start a 30-minute job: {start_time.strftime('%H:%M')}")
    print(f"Expected carbon intensity: {carbon_intensity:.2f} gCO2eq/kWh")
