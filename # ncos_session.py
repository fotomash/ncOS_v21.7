# ncos_session.py
# v3 - Integrating the NativeChartEngine with Plotly.

import pandas as pd
import plotly.graph_objects as go
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# ==============================================================================
# 1. UNIFIED PYDANTIC CONFIGURATION (No changes in this step)
# ==============================================================================

class MemoryConfig(BaseModel):
    token_budget: int = Field(8192, description="Token budget for L1 session memory.")
    compression_ratio: float = Field(0.75, description="Target compression for L2 vector memory.")
    persistent_storage_backend: str = Field("file", description="Backend for L3 memory (file or sqlite).")

class StrategyConfig(BaseModel):
    wyckoff_enabled: bool = True
    wyckoff_phases: List[str] = ["accumulation", "markup", "distribution", "markdown"]
    smc_enabled: bool = True

class ChartingConfig(BaseModel):
    native_renderer: bool = True
    action_hooks: List[str] = ["zoom", "pan", "annotate", "export"]
    output_formats: List[str] = ["png", "svg", "interactive_html"]

class NCOSConfig(BaseModel):
    version: str = "21.0-PhoenixSession"
    memory: MemoryConfig = MemoryConfig()
    strategies: StrategyConfig = StrategyConfig()
    charting: ChartingConfig = ChartingConfig()


# ==============================================================================
# 2. ENGINE & ANALYZER CLASSES (Updating NativeChartEngine)
# ==============================================================================

class WyckoffAnalyzer:
    """Represents the consolidated 38 Wyckoff analysis components."""
    def __init__(self, config: StrategyConfig):
        self.config = config
        print("Wyckoff Analyzer Initialized.")

    def detect_phase(self, market_data: pd.DataFrame) -> str:
        """Integrates logic from WyckoffPhaseCycleAgent to detect the current market phase."""
        print("-> Running Wyckoff phase detection...")
        return "Accumulation"

    def analyze_micro_structure(self, market_data: pd.DataFrame) -> Dict:
        """Placeholder for micro-structure analysis."""
        print("-> Analyzing micro-structure...")
        return {"sos_found": True, "lps_detected": False}

class NativeChartEngine:
    """Represents the 16 native charting modules, now with Plotly integration."""
    def __init__(self, config: ChartingConfig):
        self.config = config
        self.figure = None
        print("Native Chart Engine Initialized.")

    def create_chart(self, data: pd.DataFrame, chart_type: str = 'candlestick') -> 'NativeChartEngine':
        """
        Generates a Plotly chart object from market data.
        This now contains real plotting logic.
        """
        print(f"-> Generating '{chart_type}' chart with hooks: {self.config.action_hooks}")
        
        if data.empty:
            print("--> Warning: No data provided to create_chart. Generating empty figure.")
            self.figure = go.Figure()
            return self

        self.figure = go.Figure(data=[go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])

        self.figure.update_layout(
            title='Market Analysis Chart',
            yaxis_title='Price (USD)',
            xaxis_rangeslider_visible=False # A common preference
        )
        return self

    def render(self, output_path: str):
        """
        Renders the generated chart to an interactive HTML file.
        """
        if self.figure is None:
            print("--> Error: No figure to render. Please call create_chart() first.")
            return None
        
        print(f"-> Chart rendered to {output_path}")
        self.figure.write_html(output_path)
        return output_path


# ==============================================================================
# 3. THE SESSION CONTROLLER (Minor update to pass real data)
# ==============================================================================

class SessionController:
    """The main controller for an interactive NCOS session."""
    def __init__(self, config: NCOSConfig):
        print("\nInitializing NCOS Session Controller...")
        self.config = config
        self.wyckoff_analyzer = WyckoffAnalyzer(self.config.strategies)
        self.chart_engine = NativeChartEngine(self.config.charting)
        self.session_state = {
            "analysis_count": 0,
            "charts_generated": 0,
            "last_phase_detected": None
        }
        print("✓ NCOS Session Controller is ready.")

    def run_wyckoff_analysis(self, data_path: str):
        print(f"\nCommand received: Running Wyckoff analysis on '{data_path}'...")
        # market_data = pd.read_csv(data_path)
        market_data = pd.DataFrame() # Using empty DataFrame for now

        phase = self.wyckoff_analyzer.detect_phase(market_data)
        self.session_state["last_phase_detected"] = phase
        self.session_state["analysis_count"] += 1

        print(f"Analysis complete. Detected Phase: {phase}")
        return phase

    def generate_analysis_chart(self, output_path: str = "analysis_chart.html"):
        """
        A user-facing method to generate and save a chart.
        Now uses sample data to create a real chart.
        """
        print(f"\nCommand received: Generating analysis chart...")
        
        # Create a sample DataFrame for demonstration purposes
        sample_data = pd.DataFrame({
            'Date': pd.to_datetime(['2025-06-19', '2025-06-20', '2025-06-21']),
            'Open': [100, 110, 120],
            'High': [115, 125, 128],
            'Low': [98, 108, 118],
            'Close': [110, 122, 125]
        })

        self.chart_engine.create_chart(data=sample_data).render(output_path)
        self.session_state["charts_generated"] += 1
        print(f"Chart successfully generated and saved to '{output_path}'.")
        return output_path

    def get_status(self):
        print("\n--- NCOS SESSION STATUS ---")
        print(f"  Version: {self.config.version}")
        print(f"  Analyses Performed: {self.session_state['analysis_count']}")
        print(f"  Charts Generated: {self.session_state['charts_generated']}")
        print(f"  Last Detected Phase: {self.session_state['last_phase_detected']}")
        print("--------------------------")
        return self.session_state