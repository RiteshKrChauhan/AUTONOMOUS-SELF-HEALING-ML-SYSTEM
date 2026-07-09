import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


class SystemVisualizer:
    def __init__(self, output_dir="plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_monitoring_dashboard(self, logs, save=True):
        """Create comprehensive monitoring dashboard"""
        cycles = [log['index'] for log in logs if log['event'] == 'cycle']
        errors = [log['error'] for log in logs if log['event'] == 'cycle']
        rolling_avgs = [log.get('rolling_avg') for log in logs if log['event'] == 'cycle']
        drift_flags = [log.get('combined_drift', False) for log in logs if log['event'] == 'cycle']
        
        retrain_cycles = [log['index'] for log in logs if log['event'] == 'retrain_candidate']
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # Plot 1: Error over time
        axes[0].plot(cycles, errors, label='Error', color='blue', alpha=0.6)
        axes[0].plot(cycles, rolling_avgs, label='Rolling Avg', color='orange', linewidth=2)
        for rc in retrain_cycles:
            axes[0].axvline(x=rc, color='red', linestyle='--', alpha=0.7)
        axes[0].set_ylabel('Prediction Error')
        axes[0].set_title('Error Monitoring Over Time')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Drift detection
        drift_points = [cycles[i] for i, d in enumerate(drift_flags) if d]
        drift_errors = [errors[i] for i, d in enumerate(drift_flags) if d]
        axes[1].scatter(cycles, errors, c=['red' if d else 'green' for d in drift_flags], 
                       alpha=0.5, s=30)
        axes[1].set_ylabel('Error')
        axes[1].set_title('Drift Detection Points (Red = Drift)')
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Retrain events
        retrain_y = [1] * len(retrain_cycles)
        axes[2].scatter(retrain_cycles, retrain_y, color='red', s=100, marker='X', 
                       label='Retrain Events')
        axes[2].set_xlabel('Cycle Index')
        axes[2].set_ylabel('Retrain')
        axes[2].set_title('Retrain Timeline')
        axes[2].set_ylim(0, 2)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            output_path = self.output_dir / "monitoring_dashboard.png"
            plt.savefig(output_path, dpi=150)
            print(f"Dashboard saved to {output_path}")
            plt.close()
        
        return fig

    def plot_drift_score_timeline(self, logs, save=True):
        """Plot drift scores over time"""
        cycles = [log['index'] for log in logs if log['event'] == 'cycle']
        drift_scores = [log.get('data_drift_score', 0) for log in logs if log['event'] == 'cycle']
        
        plt.figure(figsize=(12, 5))
        plt.plot(cycles, drift_scores, color='purple', linewidth=2)
        plt.fill_between(cycles, drift_scores, alpha=0.3, color='purple')
        plt.xlabel('Cycle Index')
        plt.ylabel('Drift Score')
        plt.title('Data Drift Score Over Time')
        plt.grid(True, alpha=0.3)
        
        if save:
            output_path = self.output_dir / "drift_scores.png"
            plt.savefig(output_path, dpi=150)
            print(f"Drift scores saved to {output_path}")
            plt.close()

    def plot_retrain_analysis(self, logs, save=True):
        """Analyze retrain effectiveness"""
        retrain_events = [log for log in logs if log['event'] == 'retrain_candidate']
        
        if not retrain_events:
            print("No retrain events to visualize")
            return
        
        retrain_indices = [e['index'] for e in retrain_events]
        buffer_sizes = [e.get('buffer_size', 0) for e in retrain_events]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Retrain frequency
        axes[0].bar(range(len(retrain_indices)), retrain_indices, color='coral')
        axes[0].set_xlabel('Retrain Event #')
        axes[0].set_ylabel('Cycle Index')
        axes[0].set_title('Retrain Event Timeline')
        axes[0].grid(True, alpha=0.3)
        
        # Buffer sizes
        axes[1].bar(range(len(buffer_sizes)), buffer_sizes, color='teal')
        axes[1].set_xlabel('Retrain Event #')
        axes[1].set_ylabel('Buffer Size')
        axes[1].set_title('Retrain Buffer Sizes')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            output_path = self.output_dir / "retrain_analysis.png"
            plt.savefig(output_path, dpi=150)
            print(f"Retrain analysis saved to {output_path}")
            plt.close()
