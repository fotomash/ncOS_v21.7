class SimpleOrchestrator:
    def __init__(self):
        self.sessions = {}

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

    def shutdown(self):
        self.sessions.clear()

def create_orchestrator(config_path: str | None = None):
    return SimpleOrchestrator()
