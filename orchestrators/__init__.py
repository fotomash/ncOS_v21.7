class SimpleOrchestrator:
    def __init__(self):
        self.sessions = {}
        import importlib.util
        from pathlib import Path
        scorer_path = Path(__file__).resolve().parents[1] / "NCOS_Phoenix_Ultimate_v21.7" / "core" / "engines" / "predictive_scorer.py"
        spec = importlib.util.spec_from_file_location("predictive_scorer", scorer_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        PredictiveScorer = module.PredictiveScorer
        self.scorer = PredictiveScorer({
            "grade_thresholds": {"A": 0.9, "B": 0.75, "C": 0.65},
            "factor_weights": {
                "htf_bias": 0.2,
                "idm_detected": 0.1,
                "sweep_validated": 0.15,
                "choch_confirmed": 0.15,
                "poi_validated": 0.2,
                "tick_density": 0.1,
                "spread_status": 0.1,
            },
        })

    def create_session(self, config):
        self.sessions[config.session_id] = config
        return config.session_id

    async def process_data(self, session_id, fmt, file_path):
        return {
            "stages": {
                "ingestion": True,
                "strategies": True,
                "signal": True,
                "visualization": True,
            }
        }

    def score(self, features, context=None):
        return self.scorer.score(features, context)

    def shutdown(self):
        self.sessions.clear()

def create_orchestrator(config_path: str | None = None):
    return SimpleOrchestrator()
