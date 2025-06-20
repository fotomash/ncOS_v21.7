
import os
import json
import gzip
import logging
import time
from threading import Thread, Event
import shutil

# --- Setup basic logging ---
# This allows you to see what the snapshot manager is doing in the system logs.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SnapshotConfig:
    """A centralized class to handle configuration for the snapshot system."""
    def __init__(self, config_data):
        # Interval in seconds between automatic snapshots.
        self.snapshot_interval = config_data.get('snapshot_interval_seconds', 180)
        # Master switch to enable or disable snapshotting.
        self.persist_memory = config_data.get('persist_memory', True)
        # Whether to compress snapshots with gzip to save space.
        self.compress_snapshots = config_data.get('compress_snapshots', True)
        # Path template for saving snapshots. {timestamp} is replaced with the current time.
        self.snapshot_path_template = config_data.get('snapshot_path_template', './snapshots/ncos_snapshot_{timestamp}.json')
        # The maximum number of snapshots to keep. Older ones are deleted.
        self.max_snapshots = config_data.get('max_snapshots', 10)

        # Ensure the directory for snapshots exists.
        self.snapshot_dir = os.path.dirname(self.snapshot_path_template)
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)
            logging.info(f"Created snapshot directory: {self.snapshot_dir}")

class MemoryBridge:
    """
    A bridge to interact with the system's memory.
    This class should be adapted to hook into the actual memory management APIs of ncOS.
    """
    def get_current_memory_state(self):
        """Retrieves the current memory state of the OS."""
        logging.info("Fetching current memory state.")
        # In a real implementation, this would call an ncOS API.
        # For this example, we'll use the data from bootstrap_memory_snapshot.json as a mock.
        try:
            with open('bootstrap_memory_snapshot.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("bootstrap_memory_snapshot.json not found for mocking. Returning empty state.")
            return {"error": "memory_source_not_found", "details": "The mock data file is missing."}
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from memory snapshot file.")
            return {"error": "invalid_memory_format", "details": "The mock data file is corrupted."}

    def restore_memory_state(self, state):
        """Restores the system's memory to a given state."""
        logging.info("Restoring memory state.")
        # In a real implementation, this would be a call to an ncOS API to load the memory state.
        # For now, we just log that the action would be performed.
        logging.info("System memory state has been restored (simulation).")
        # logging.debug(f"Restored state details: {state}")
        return True

class MemorySnapshotManager:
    """Manages the creation, restoration, and maintenance of memory snapshots."""
    def __init__(self, config, memory_bridge):
        self.config = config
        self.memory_bridge = memory_bridge
        self._stop_event = Event()
        self._thread = Thread(target=self._snapshot_scheduler, daemon=True)

    def _snapshot_scheduler(self):
        """Periodically creates snapshots based on the configured interval."""
        logging.info("Snapshot scheduler started.")
        while not self._stop_event.is_set():
            self.create_snapshot()
            self._cleanup_old_snapshots()
            # Wait for the specified interval or until the stop event is set.
            self._stop_event.wait(self.config.snapshot_interval)
        logging.info("Snapshot scheduler stopped.")

    def start(self):
        """Starts the automatic snapshotting process in a background thread."""
        if not self.config.persist_memory:
            logging.warning("Memory persistence is disabled. Snapshot manager will not start.")
            return
        if self._thread.is_alive():
            logging.warning("Snapshot manager is already running.")
            return
        logging.info("Starting automatic memory snapshot manager.")
        self._thread.start()

    def stop(self):
        """Stops the automatic snapshotting process gracefully."""
        if not self._thread.is_alive():
            logging.info("Snapshot manager is not running.")
            return
        logging.info("Stopping automatic memory snapshot manager.")
        self._stop_event.set()
        self._thread.join() # Wait for the thread to finish its current cycle.

    def create_snapshot(self):
        """Creates a single memory snapshot, handling compression and storage."""
        try:
            state = self.memory_bridge.get_current_memory_state()
            if "error" in state:
                logging.error(f"Could not create snapshot due to memory bridge error: {state['details']}")
                return None

            timestamp = int(time.time())
            file_path = self.config.snapshot_path_template.format(timestamp=timestamp)

            logging.info(f"Creating snapshot: {file_path}")

            if self.config.compress_snapshots:
                file_path += '.gz'
                with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
            else:
                with open(file_path, 'w') as f:
                    json.dump(state, f, indent=2)

            logging.info(f"Successfully created snapshot: {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"An unexpected error occurred while creating snapshot: {e}", exc_info=True)
            return None

    def find_latest_snapshot(self):
        """Finds the path of the most recent valid snapshot file."""
        try:
            files = [os.path.join(self.config.snapshot_dir, f) for f in os.listdir(self.config.snapshot_dir)]
            if not files:
                return None
            # Find the most recently modified file in the directory.
            latest_file = max(files, key=os.path.getmtime)
            return latest_file
        except FileNotFoundError:
            logging.warning("Snapshot directory not found. No snapshots to restore from.")
            return None

    def restore_from_latest_snapshot(self):
        """Restores the system memory from the most recent snapshot."""
        latest_snapshot = self.find_latest_snapshot()
        if not latest_snapshot:
            logging.warning("No snapshot found to restore from.")
            return False

        logging.info(f"Attempting to restore from snapshot: {latest_snapshot}")
        try:
            if latest_snapshot.endswith('.gz'):
                with gzip.open(latest_snapshot, 'rt', encoding='utf-8') as f:
                    state = json.load(f)
            else:
                with open(latest_snapshot, 'r') as f:
                    state = json.load(f)

            return self.memory_bridge.restore_memory_state(state)
        except Exception as e:
            logging.error(f"Failed to restore from snapshot {latest_snapshot}: {e}", exc_info=True)
            return False

    def _cleanup_old_snapshots(self):
        """Removes the oldest snapshots to stay within the max_snapshots limit."""
        try:
            files = sorted(
                [os.path.join(self.config.snapshot_dir, f) for f in os.listdir(self.config.snapshot_dir)],
                key=os.path.getmtime
            )

            if len(files) > self.config.max_snapshots:
                num_to_delete = len(files) - self.config.max_snapshots
                files_to_delete = files[:num_to_delete]
                logging.info(f"Cleaning up {len(files_to_delete)} old snapshots.")
                for f in files_to_delete:
                    try:
                        os.remove(f)
                        logging.info(f"Removed old snapshot: {f}")
                    except OSError as e:
                        logging.error(f"Error removing snapshot file {f}: {e}")
        except FileNotFoundError:
            # This is not an error; the directory might not have been created yet.
            pass
        except Exception as e:
            logging.error(f"An error occurred during snapshot cleanup: {e}", exc_info=True)

# --- Example Usage ---
# This block demonstrates how you would integrate and use the snapshot manager in your application.
# You would typically place this logic in your main application's startup and shutdown sequence.
def main_application_simulation():
    # 1. Define the configuration for the snapshot system.
    # This could be loaded from a YAML or JSON config file in your ncOS project.
    config_data = {
        "snapshot_interval_seconds": 10,  # For demonstration, snapshot every 10 seconds
        "persist_memory": True,
        "compress_snapshots": True,
        "snapshot_path_template": "./ncos_snapshots/snapshot_{timestamp}.json",
        "max_snapshots": 5 # Keep the last 5 snapshots
    }

    # 2. Initialize the core components.
    snapshot_config = SnapshotConfig(config_data)
    memory_bridge = MemoryBridge()
    snapshot_manager = MemorySnapshotManager(snapshot_config, memory_bridge)

    # 3. On system boot, attempt to restore from the latest snapshot.
    print("--- [ncOS System Boot] ---")
    restored = snapshot_manager.restore_from_latest_snapshot()
    if restored:
        print("System state restored successfully from the latest snapshot.")
    else:
        print("Could not restore from a snapshot. Starting with a clean state.")
    print("--------------------------")

    # 4. Start the automatic snapshotting service in the background.
    snapshot_manager.start()

    # 5. Your main application logic runs here.
    # The snapshot manager will work in the background.
    print("Snapshot service is running in the background.")
    print("The main application is now running. Press Ctrl+C to shut down.")
    try:
        # This loop simulates your application being alive.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 6. On system shutdown, stop the service gracefully.
        print("\n--- [ncOS System Shutdown] ---")
        snapshot_manager.stop()
        print("Snapshot service stopped gracefully.")
        print("----------------------------")

if __name__ == '__main__':
    # To prevent timeouts in automated environments, we won't run the infinite loop here.
    # The 'main_application_simulation' function shows how you should use the classes.
    print("Refactored snapshot system script generated.")
    print("The 'main_application_simulation' function demonstrates usage.")
    # You can uncomment the line below to run the simulation locally.
    # main_application_simulation()

