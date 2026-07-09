"""
System Verification Script
Run this to check if all components are working correctly
"""

import sys
from pathlib import Path

def check_imports():
    """Verify all dependencies are installed"""
    print("🔍 Checking imports...")
    
    required_modules = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('sklearn', 'scikit-learn'),
        ('river', 'river'),
        ('mlflow', 'mlflow'),
        ('matplotlib', 'matplotlib'),
        ('scipy', 'scipy'),
    ]
    
    missing = []
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed\n")
    return True


def check_project_structure():
    """Verify all required files exist"""
    print("🔍 Checking project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'dataset/raw/train_FD001.txt',
        'ml/train.py',
        'ml/predict.py',
        'ml/performance_gate.py',
        'ml/shadow_evaluator.py',
        'ml/confidence_predictor.py',
        'drift/adwin_detector.py',
        'drift/data_drift.py',
        'drift/error_monitor.py',
        'drift/anomaly_detector.py',
        'decision/engine.py',
        'decision/adaptive_cooldown.py',
        'governance/governance_logger.py',
        'visualization/plotter.py',
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ Missing files: {len(missing)}")
        return False
    
    print("✅ All required files present\n")
    return True


def check_data():
    """Verify dataset is available"""
    print("🔍 Checking dataset...")
    
    data_file = Path('dataset/raw/train_FD001.txt')
    if not data_file.exists():
        print("  ❌ Dataset not found")
        return False
    
    # Check file size
    size_mb = data_file.stat().st_size / (1024 * 1024)
    print(f"  ✅ Dataset found ({size_mb:.2f} MB)")
    
    # Try loading
    try:
        from dataset.processed.preprocess_module import load_data
        df = load_data(str(data_file))
        print(f"  ✅ Dataset loaded ({len(df)} rows)")
    except Exception as e:
        print(f"  ❌ Error loading dataset: {e}")
        return False
    
    print("✅ Dataset ready\n")
    return True


def test_components():
    """Test individual components"""
    print("🔍 Testing components...")
    
    tests = []
    
    # Test 1: Performance Gate
    try:
        from ml.performance_gate import ModelPerformanceGate
        gate = ModelPerformanceGate()
        print("  ✅ Performance Gate")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Performance Gate: {e}")
        tests.append(False)
    
    # Test 2: Adaptive Cooldown
    try:
        from decision.adaptive_cooldown import AdaptiveCooldown
        cooldown = AdaptiveCooldown()
        should_retrain, required, elapsed = cooldown.should_retrain(50, 0.7)
        print("  ✅ Adaptive Cooldown")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Adaptive Cooldown: {e}")
        tests.append(False)
    
    # Test 3: Shadow Evaluator
    try:
        from ml.shadow_evaluator import ShadowModelEvaluator
        evaluator = ShadowModelEvaluator()
        print("  ✅ Shadow Evaluator")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Shadow Evaluator: {e}")
        tests.append(False)
    
    # Test 4: Anomaly Detector
    try:
        from drift.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector()
        print("  ✅ Anomaly Detector")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Anomaly Detector: {e}")
        tests.append(False)
    
    # Test 5: Confidence Predictor
    try:
        from ml.confidence_predictor import ConfidencePredictor
        predictor = ConfidencePredictor()
        print("  ✅ Confidence Predictor")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Confidence Predictor: {e}")
        tests.append(False)
    
    # Test 6: Enhanced Decision Engine
    try:
        from decision.engine import DecisionEngine
        engine = DecisionEngine()
        action = engine.decide(True, 30.0, True, 0.8)
        assert action in ["STABLE", "WATCH", "MONITOR", "ALERT", "RETRAIN", "RETRAIN_URGENT"]
        print("  ✅ Enhanced Decision Engine")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Enhanced Decision Engine: {e}")
        tests.append(False)
    
    # Test 7: Governance Logger
    try:
        from governance.governance_logger import GovernanceLogger
        logger = GovernanceLogger(log_dir="logs_test")
        print("  ✅ Governance Logger")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Governance Logger: {e}")
        tests.append(False)
    
    # Test 8: Visualizer
    try:
        from visualization.plotter import SystemVisualizer
        viz = SystemVisualizer()
        print("  ✅ Visualizer")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ Visualizer: {e}")
        tests.append(False)
    
    if all(tests):
        print("✅ All components working\n")
        return True
    else:
        print(f"❌ {sum(not t for t in tests)} component(s) failed\n")
        return False


def main():
    print("="*60)
    print("🚀 AUTONOMOUS ML SYSTEM - VERIFICATION")
    print("="*60)
    print()
    
    checks = [
        ("Dependencies", check_imports),
        ("Project Structure", check_project_structure),
        ("Dataset", check_data),
        ("Components", test_components),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed: {e}\n")
            results.append((name, False))
    
    print("="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*60)
    
    if all(r for _, r in results):
        print("\n🎉 ALL CHECKS PASSED!")
        print("\nYou're ready to run the system:")
        print("  python main.py")
        print("\nTo view MLflow logs:")
        print("  mlflow ui")
        return 0
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the system.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
