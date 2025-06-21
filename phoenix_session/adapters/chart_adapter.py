# phoenix_session/adapters/chart_adapter.py
class ChartAdapter:
    def __init__(self, phoenix_controller, native_engine=None):
        self.phoenix = phoenix_controller
        self.native_engine = native_engine # The original NCOS chart engine
        self.config = phoenix_controller.config

    def render_chart(self, data, use_legacy=False):
        """
        Render a chart using either Phoenix or native engine.
        """
        if self.config.fast_mode and not use_legacy:
            return self.phoenix.chart(data)
        elif self.native_engine:
            print("Legacy charting not implemented in this adapter.")
            return None
        else:
            raise ValueError("No valid chart engine available.")