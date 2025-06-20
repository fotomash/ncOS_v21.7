"""
ncOScore Enhanced Core Orchestrator v1.1
Integrated SMC Analysis, Vector Operations, and Liquidity Analysis
Production-ready with all missing components
"""

import asyncio
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd

# Import our new engines
from smc_analysis_engine import ncOScoreSMCEngine
from enhanced_vector_engine import ncOScoreVectorEngine, BrownVectorStoreIntegration
from vector_store import VectorStore
from liquidity_analysis_engine import ncOScoreLiquidityEngine

class MountPoint(Enum):
    """Unified mount point definitions"""
    CUSTOM_GPT = "/mnt/data"
    WORKSPACE = "workspace://"
    MEMORY = "memory://"
    SESSION = "session://"

    @classmethod
    def resolve(cls, path: str) -> Path:
        """Resolve path with proper mount point"""
        if path.startswith("/mnt/data"):
            return Path(path)
        elif path.startswith("workspace://"):
            return Path("./workspace") / path[12:]
        elif path.startswith("memory://"):
            return Path("./memory") / path[9:]
        elif path.startswith("session://"):
            return Path("./session") / path[10:]
        return Path(path)

@dataclass
class SessionState:
    """Enhanced session state with trading capabilities"""
    session_id: str = field(default_factory=lambda: f"ncos_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    start_time: datetime = field(default_factory=datetime.now)
    mount_points: Dict[str, str] = field(default_factory=dict)
    active_agents: List[str] = field(default_factory=list)
    processed_files: List[str] = field(default_factory=list)
    memory_usage_mb: float = 0.0
    interaction_count: int = 0
    system_health: str = "green"

    # Trading-specific state
    active_analyses: Dict[str, Any] = field(default_factory=dict)
    market_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    trading_signals: List[Dict] = field(default_factory=list)
    confluence_scores: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.mount_points = {
            "custom_gpt": "/mnt/data",
            "workspace": "./workspace", 
            "memory": "./memory",
            "session": "./session"
        }

class ncOScoreEnhancedOrchestrator:
    """Enhanced orchestrator with full SMC and vector capabilities"""

    def __init__(self, config_path: Optional[str] = None):
        self.session_state = SessionState()
        self.agents = {}
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        mem_cfg = self.config.get("memory", {})
        self.memory_manager = EnhancedMemoryManager(
            ttl_seconds=mem_cfg.get("context_ttl_seconds", 3600),
            default_window=mem_cfg.get("context_window", 5),
        )

        # Initialize enhanced engines
        self.smc_engine = None
        self.vector_engine = None
        self.liquidity_engine = None
        self.brown_vector_store = None
        self.drift_agent = None


    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load enhanced configuration"""
        default_config = {
            "version": "ncOScore-1.1-Enhanced",
            "features": {
                "csv_enrichment": True,
                "dynamic_menus": True,
                "vector_memory": True,
                "agent_orchestration": True,
                "smc_analysis": True,
                "liquidity_analysis": True,
                "brown_vector_store": True,
                "multi_timeframe_confluence": True
            },
            "memory": {
                "backend": "in_memory",
                "max_size_mb": 1024,  # Increased for trading data
                "compression": True,
                "gc_enabled": True,
                "context_ttl_seconds": 3600,
                "context_window": 5
            },
            "trading": {
                "supported_timeframes": ["M5", "M15", "H1", "H4", "D1"],
                "default_timeframe": "H1",
                "confluence_threshold": 0.6,
                "signal_strength_threshold": 0.7
            },
            "drift_detection": {
                "drift_threshold": 1.0,
                "history_size": 20
            }
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging"""
        logger = logging.getLogger("ncOScore-Enhanced")
        logger.setLevel(logging.INFO)
        return logger

    async def initialize(self):
        """Initialize all enhanced components"""
        self.logger.info(f"🚀 Initializing ncOScore Enhanced session: {self.session_state.session_id}")

        # Initialize core components
        await self._load_enhanced_agents()
        await self._initialize_trading_engines()
        await self._validate_boot()

        self.logger.info("✅ ncOScore Enhanced initialization complete")

    async def _load_enhanced_agents(self):
        """Load enhanced agents including trading engines"""
        enhanced_agents = {
            "csv_processor": "CSV processing and enrichment",
            "menu_controller": "Dynamic menu generation",
            "memory_manager": "Memory and vector management", 
            "file_handler": "File upload and processing",
            "validator": "System validation and health",
            "smc_analyzer": "Smart Money Concepts analysis",
            "vector_processor": "Vector operations and similarity search",
            "liquidity_analyzer": "Liquidity analysis and sweep detection",
            "confluence_calculator": "Multi-timeframe confluence scoring",
            "drift_detector": "Embedding drift detection"
        }

        for agent_id, description in enhanced_agents.items():
            self.agents[agent_id] = {
                "id": agent_id,
                "description": description,
                "status": "active",
                "loaded_at": datetime.now()
            }
            self.session_state.active_agents.append(agent_id)

    async def _initialize_trading_engines(self):
        """Initialize trading analysis engines"""
        try:
            # Initialize SMC Engine
            self.smc_engine = ncOScoreSMCEngine(self.session_state)
            self.logger.info("✅ SMC Analysis Engine initialized")

            # Initialize Vector Store and Engine
            store_path = MountPoint.resolve(self.session_state.mount_points["session"]) / "vector_store.json"
            self.vector_store = VectorStore(store_path)
            self.vector_engine = ncOScoreVectorEngine(
                dimensions=1536,

            self.logger.info("✅ Vector Engine initialized")
            self._vector_store_task = asyncio.create_task(self._autosave_vector_store())

            # Initialize Brown Vector Store
            self.brown_vector_store = BrownVectorStoreIntegration(self.vector_engine)
            self.logger.info("✅ Brown Vector Store initialized")

            # Initialize Drift Detection Agent
            drift_cfg = self.config.get("drift_detection", {})
            self.drift_agent = DriftDetectionAgent(self, drift_cfg)
            self.logger.info("✅ Drift Detection Agent initialized")

            # Initialize Liquidity Engine
            self.liquidity_engine = ncOScoreLiquidityEngine(self.session_state)
            self.logger.info("✅ Liquidity Analysis Engine initialized")

        except Exception as e:
            self.logger.error(f"❌ Error initializing trading engines: {e}")
            raise

    async def _validate_boot(self):
        """Enhanced boot validation"""
        validations = {
            "agents_loaded": len(self.agents) > 0,
            "session_valid": self.session_state.session_id is not None,
            "config_loaded": self.config is not None,
            "mount_points_ready": len(self.session_state.mount_points) > 0,
            "smc_engine_ready": self.smc_engine is not None,
            "vector_engine_ready": self.vector_engine is not None,
            "liquidity_engine_ready": self.liquidity_engine is not None,
            "brown_store_ready": self.brown_vector_store is not None,
            "drift_agent_ready": self.drift_agent is not None
        }

        failed = [k for k, v in validations.items() if not v]
        if failed:
            raise RuntimeError(f"Enhanced boot validation failed: {failed}")

    async def process_file(self, file_path: str, file_type: str = None) -> Dict:
        """Enhanced file processing with trading analysis"""
        self.session_state.interaction_count += 1

        # Auto-detect file type if not provided
        if not file_type:
            file_type = self._detect_file_type(file_path)

        # Route to appropriate processor
        if file_type == "csv":
            return await self._process_trading_csv(file_path)
        elif file_type in ["zip", "tar", "gz"]:
            return await self._process_archive(file_path)
        else:
            return await self._process_generic(file_path)

    async def _process_trading_csv(self, file_path: str) -> Dict:
        """Process CSV with full trading analysis"""
        self.logger.info(f"Processing trading CSV: {file_path}")
        try:
            # Load CSV data
            try:
                df = pd.read_csv(file_path)
            except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
                msg = f"CSV parsing error for {file_path}: {e}"
                self.logger.error(msg)
                return {"status": "error", "error": msg}

            # Validate required columns
            required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
            missing_columns = [c for c in required_columns if c not in df.columns]
            if missing_columns:
                msg = f"Missing required columns: {missing_columns}"
                self.logger.error(msg)
                raise ValueError(msg)

            # Store in session state
            file_key = Path(file_path).stem
            self.session_state.market_data[file_key] = df

            # Run comprehensive analysis
            analysis_results = {}

            # SMC Analysis
            if self.smc_engine:
                smc_result = await self.smc_engine.analyze_market_structure(df)
                analysis_results["smc_analysis"] = smc_result

            # Vector Analysis
            if self.vector_engine:
                vector_result = await self.vector_engine.embed_market_data(df, f"market_data_{file_key}")
                analysis_results["vector_analysis"] = vector_result

                # Forward embedding to drift detector
                if self.drift_agent and vector_result.get("embedding") is not None:
                    await self.drift_agent.handle_trigger(
                        "embedding.generated",
                        {
                            "embedding": vector_result["embedding"],
                            "key": f"market_data_{file_key}",
                        },
                        {},
                    )

                # Pattern matching
                pattern_result = await self.vector_engine.pattern_matching(df, "market_structure")
                analysis_results["pattern_matching"] = pattern_result

            # Liquidity Analysis
            if self.liquidity_engine:
                liquidity_result = await self.liquidity_engine.analyze_liquidity(df)
                analysis_results["liquidity_analysis"] = liquidity_result

            # Calculate overall confluence score
            confluence_score = self._calculate_overall_confluence(analysis_results)
            self.session_state.confluence_scores[file_key] = confluence_score

            # Generate trading signals
            signals = self._generate_enhanced_signals(analysis_results, confluence_score)
            self.session_state.trading_signals.extend(signals)

            # Store analysis in session
            self.session_state.active_analyses[file_key] = analysis_results

            self.logger.info(f"Finished processing trading CSV: {file_path}")

            return {
                "status": "success",
                "type": "trading_csv",
                "file": file_path,
                "processor": "enhanced_trading_processor",
                "data_shape": df.shape,
                "analysis_results": analysis_results,
                "confluence_score": confluence_score,
                "signals_generated": len(signals),
                "features": [
                    "smc_analysis", "vector_embeddings", "liquidity_analysis", 
                    "pattern_matching", "confluence_scoring", "signal_generation"
                ],
                "next_actions": [
                    "view_smc_analysis", "check_liquidity_zones", "review_signals",
                    "multi_timeframe_analysis", "export_analysis", "create_dashboard"
                ]
            }

        except Exception as e:
            self.logger.error(f"Error processing trading CSV {file_path}: {e}")
            return {"status": "error", "error": str(e)}

    def _calculate_overall_confluence(self, analysis_results: Dict) -> float:
        """Calculate overall confluence score from all analyses"""
        scores = []

        # SMC confluence
        if "smc_analysis" in analysis_results:
            smc_score = analysis_results["smc_analysis"].get("confluence_score", 0.0)
            scores.append(smc_score * 0.4)  # 40% weight

        # Liquidity confluence
        if "liquidity_analysis" in analysis_results:
            liq_score = analysis_results["liquidity_analysis"].get("sweep_probability", 0.0)
            scores.append(liq_score * 0.3)  # 30% weight

        # Pattern matching confidence
        if "pattern_matching" in analysis_results:
            pattern_data = analysis_results["pattern_matching"]
            if pattern_data.get("status") == "success" and pattern_data.get("similar_patterns"):
                avg_similarity = sum(p["similarity"] for p in pattern_data["similar_patterns"]) / len(pattern_data["similar_patterns"])
                scores.append(avg_similarity * 0.3)  # 30% weight

        return sum(scores) if scores else 0.0

    def _generate_enhanced_signals(self, analysis_results: Dict, confluence_score: float) -> List[Dict]:
        """Generate enhanced trading signals"""
        signals = []

        if confluence_score > self.config["trading"]["confluence_threshold"]:
            # High confluence signal
            signal = {
                "type": "High_Confluence_Setup",
                "confluence_score": confluence_score,
                "strength": "High" if confluence_score > 0.8 else "Medium",
                "timestamp": datetime.now().isoformat(),
                "components": []
            }

            # Add SMC signals
            if "smc_analysis" in analysis_results:
                smc_signals = analysis_results["smc_analysis"].get("signals", [])
                signal["components"].extend(smc_signals)

            # Add liquidity signals
            if "liquidity_analysis" in analysis_results:
                liq_zones = analysis_results["liquidity_analysis"].get("high_probability_zones", [])
                for zone in liq_zones:
                    if zone["probability"] > 0.6:
                        signal["components"].append({
                            "type": "Liquidity_Zone",
                            "price": zone["price"],
                            "probability": zone["probability"]
                        })

            signals.append(signal)

        return signals

    def generate_enhanced_menu(self, context: Dict = None) -> Dict:
        """Generate enhanced menu with trading capabilities"""
        base_menu = {
            "title": "🎛️ ncOScore Enhanced Trading System",
            "session": self.session_state.session_id,
            "version": "v1.1-Enhanced",
            "categories": {}
        }

        # Trading Analysis Category
        if self._has_market_data():
            base_menu["categories"]["trading_analysis"] = {
                "icon": "📈",
                "title": "Trading Analysis",
                "options": {
                    "1": {
                        "label": "SMC Structure Analysis",
                        "action": "run_smc_analysis",
                        "description": "Analyze BOS, CHoCH, FVG, and POI patterns"
                    },
                    "2": {
                        "label": "Liquidity Analysis",
                        "action": "run_liquidity_analysis", 
                        "description": "Detect liquidity pools and sweep probabilities"
                    },
                    "3": {
                        "label": "Multi-Timeframe Confluence",
                        "action": "calculate_confluence",
                        "description": "Calculate confluence across timeframes"
                    },
                    "4": {
                        "label": "Generate Trading Signals",
                        "action": "generate_signals",
                        "description": "Create high-probability trading setups"
                    }
                }
            }

        # Vector Operations Category
        base_menu["categories"]["vector_operations"] = {
            "icon": "🔮",
            "title": "Vector Operations",
            "options": {
                "5": {
                    "label": "Pattern Matching",
                    "action": "pattern_matching",
                    "description": "Find similar historical patterns"
                },
                "6": {
                    "label": "Similarity Search",
                    "action": "similarity_search",
                    "description": "Search vector store for correlations"
                },
                "7": {
                    "label": "Brown Vector Store",
                    "action": "brown_vector_ops",
                    "description": "Advanced vector store operations"
                }
            }
        }

        # System Management Category
        base_menu["categories"]["system_management"] = {
            "icon": "⚙️",
            "title": "System Management",
            "options": {
                "8": {
                    "label": "Trading Dashboard",
                    "action": "show_dashboard",
                    "description": "View comprehensive trading dashboard"
                },
                "9": {
                    "label": "System Status",
                    "action": "system_status",
                    "description": "Check system health and performance"
                },
                "0": {
                    "label": "Help & Documentation",
                    "action": "show_help",
                    "description": "Show available commands and help"
                }
            }
        }

        # Add current status
        base_menu["status"] = {
            "market_data_files": len(self.session_state.market_data),
            "active_analyses": len(self.session_state.active_analyses),
            "trading_signals": len(self.session_state.trading_signals),
            "confluence_scores": self.session_state.confluence_scores,
            "system_health": self.session_state.system_health
        }

        return base_menu

    def _has_market_data(self) -> bool:
        """Check if market data is available"""
        return len(self.session_state.market_data) > 0

    def get_enhanced_system_status(self) -> Dict:
        """Get enhanced system status with trading metrics"""
        base_status = {
            "session_id": self.session_state.session_id,
            "uptime": str(datetime.now() - self.session_state.start_time),
            "memory_usage_mb": self.session_state.memory_usage_mb,
            "active_agents": len(self.session_state.active_agents),
            "processed_files": len(self.session_state.processed_files),
            "system_health": self.session_state.system_health
        }

        # Trading-specific status
        trading_status = {
            "market_data_files": len(self.session_state.market_data),
            "active_analyses": len(self.session_state.active_analyses),
            "trading_signals": len(self.session_state.trading_signals),
            "confluence_scores": self.session_state.confluence_scores
        }

        # Engine status
        engine_status = {
            "smc_engine": "active" if self.smc_engine else "inactive",
            "vector_engine": "active" if self.vector_engine else "inactive",
            "liquidity_engine": "active" if self.liquidity_engine else "inactive",
            "brown_vector_store": "active" if self.brown_vector_store else "inactive"
        }

        if self.vector_engine:
            engine_status["vector_store_stats"] = self.vector_engine.get_vector_store_stats()

        return {
            "system": base_status,
            "trading": trading_status,
            "engines": engine_status
        }

    async def _autosave_vector_store(self, interval: int = 300) -> None:
        """Periodically save the vector store to disk."""
        while True:
            await asyncio.sleep(interval)
            if self.vector_store:
                try:
                    self.vector_store.save()
                    self.logger.info("💾 Vector store autosaved")
                except Exception as e:  # pragma: no cover - safeguard
                    self.logger.error(f"Vector store autosave failed: {e}")

    # Additional helper methods for file detection
    def _detect_file_type(self, file_path: str) -> str:
        """Auto-detect file type"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return "csv"
        elif suffix in [".zip", ".tar", ".gz"]:
            return "archive"
        elif suffix in [".json", ".yaml", ".yml"]:
            return "config"
        else:
            return "generic"

    async def _process_archive(self, file_path: str) -> Dict:
        """Process archive files"""
        return {
            "status": "success", 
            "type": "archive",
            "file": file_path,
            "processor": "archive_handler",
            "features": ["extraction", "content_analysis", "batch_processing"],
            "next_actions": ["extract", "analyze_contents", "process_batch"]
        }

    async def _process_generic(self, file_path: str) -> Dict:
        """Process generic files"""
        return {
            "status": "success",
            "type": "generic",
            "file": file_path,
            "processor": "generic_handler",
            "features": ["content_analysis", "metadata_extraction"],
            "next_actions": ["analyze", "convert", "process"]
        }

    # ------------------------------------------------------------------
    async def store_memory(self, namespace: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Expose memory storage for agents."""
        entry = self.memory_manager.store_memory(namespace, data, metadata)
        return {
            "namespace": namespace,
            "timestamp": entry.timestamp.isoformat(),
            "metadata": entry.metadata,
        }

    async def get_memory(self, namespace: str, window_size: Optional[int] = None) -> List[Any]:
        """Retrieve a context window for ``namespace``."""
        entries = self.memory_manager.get_context_window(namespace, window_size)
        return [e.data for e in entries]
