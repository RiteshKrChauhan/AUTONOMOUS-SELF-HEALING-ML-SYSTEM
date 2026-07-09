import json
from datetime import datetime
from pathlib import Path


class GovernanceLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cycle_log_path = self.log_dir / f"cycles_{timestamp}.jsonl"
        self.decision_log_path = self.log_dir / f"decisions_{timestamp}.jsonl"
        self.retrain_log_path = self.log_dir / f"retrains_{timestamp}.jsonl"

    def log_cycle(self, cycle_data):
        """Log each prediction cycle"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "cycle",
            **cycle_data
        }
        self._append_jsonl(self.cycle_log_path, entry)

    def log_decision(self, decision_data):
        """Log decision engine outputs"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "decision",
            **decision_data
        }
        self._append_jsonl(self.decision_log_path, entry)

    def log_retrain(self, retrain_data):
        """Audit trail for retrain events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "retrain",
            **retrain_data
        }
        self._append_jsonl(self.retrain_log_path, entry)

    def _append_jsonl(self, path, data):
        """Append JSON line to file"""
        with open(path, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def get_retrain_history(self):
        """Retrieve all retrain events for audit"""
        if not self.retrain_log_path.exists():
            return []
        
        history = []
        with open(self.retrain_log_path, 'r') as f:
            for line in f:
                history.append(json.loads(line))
        return history
