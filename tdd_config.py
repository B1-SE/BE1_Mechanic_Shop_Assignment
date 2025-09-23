"""
Test-Driven Development configuration and utilities
"""

import subprocess
from pathlib import Path


class TDDRunner:
    """Test-Driven Development automation runner"""
    
    def __init__(self, project_root=None):
        self.project_root = project_root or Path.cwd()
        self.test_dir = self.project_root / "tests"
        self.coverage_threshold = 95
    
    def run_red_phase(self, test_file=None):
        """RED: Run failing tests"""
        print("🔴 RED Phase: Running tests (expecting failures)")
        
        cmd = ["python", "-m", "pytest"]
        if test_file:
            cmd.append(str(test_file))
        else:
            cmd.append("tests/")
        
        cmd.extend(["-v", "--tb=short", "--no-header"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("⚠️  All tests are passing! No RED phase needed.")
            return True
        else:
            print(f"✅ RED phase complete: {result.stderr.count('FAILED')} failing tests")
            return False
    
    def run_green_phase(self, test_file=None):
        """GREEN: Run tests after implementation"""
        print("🟢 GREEN Phase: Running tests (expecting success)")
        
        cmd = ["python", "-m", "pytest"]
        if test_file:
            cmd.append(str(test_file))
        else:
            cmd.append("tests/")
        
        cmd.extend(["-v", "--tb=short"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GREEN phase complete: All tests passing!")
            return True
        else:
            print(f"❌ GREEN phase failed: {result.stderr.count('FAILED')} failing tests")
            print("Implementation needs more work.")
            return False
    
    def run_refactor_phase(self):
        """BLUE/REFACTOR: Run tests with coverage and quality checks"""
        print("🔵 REFACTOR Phase: Running quality checks")
        
        # Run tests with coverage
        coverage_cmd = [
            "python", "-m", "pytest", "tests/",
            "--cov=app",
            f"--cov-fail-under={self.coverage_threshold}",
            "--cov-report=term-missing",
            "-v"
        ]
        
        coverage_result = subprocess.run(coverage_cmd, capture_output=True, text=True)
        
        if coverage_result.returncode != 0:
            print(f"❌ Coverage below {self.coverage_threshold}%")
            return False
        
        # Run linting
        lint_result = self.run_linting()
        
        if coverage_result.returncode == 0 and lint_result:
            print("✅ REFACTOR phase complete: All quality checks passed!")
            return True
        else:
            print("❌ REFACTOR phase failed: Quality checks need attention")
            return False
    
    def run_linting(self):
        """Run code quality checks"""
        checks = [
            (["flake8", "app/", "tests/", "--max-line-length=88"], "Flake8"),
            (["black", "--check", "app/", "tests/"], "Black formatting"),
            (["isort", "--check-only", "app/", "tests/"], "Import sorting")
        ]
        
        all_passed = True
        for cmd, name in checks:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: Passed")
            else:
                print(f"❌ {name}: Failed")
                all_passed = False
        
        return all_passed
    
    def watch_mode(self):
        """Watch for file changes and run TDD cycle"""
        print("👀 TDD Watch Mode: Monitoring file changes...")
        print("Press Ctrl+C to stop")
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class TDDEventHandler(FileSystemEventHandler):
                def __init__(self, tdd_runner):
                    self.tdd_runner = tdd_runner
                
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith('.py'):
                        print(f"\n📝 File changed: {event.src_path}")
                        self.tdd_runner.run_tdd_cycle()
            
            event_handler = TDDEventHandler(self)
            observer = Observer()
            observer.schedule(event_handler, str(self.project_root), recursive=True)
            observer.start()
            observer.join()
            
        except ImportError:
            print("❌ Watchdog not installed. Install with: pip install watchdog")
        except KeyboardInterrupt:
            print("\n👋 TDD Watch Mode stopped")
    
    def run_tdd_cycle(self, test_file=None):
        """Run complete RED-GREEN-REFACTOR cycle"""
        print("\n" + "="*50)
        print("🔄 Starting TDD Cycle")
        print("="*50)
        
        # RED Phase
        red_result = self.run_red_phase(test_file)
        
        if red_result:
            print("\n⏩ Skipping to REFACTOR phase (no failing tests)")
            return self.run_refactor_phase()
        
        # Wait for implementation
        input("\n⏸️  Implement the feature to make tests pass, then press Enter...")
        
        # GREEN Phase
        green_result = self.run_green_phase(test_file)
        
        if not green_result:
            print("\n🔄 Return to implementation phase")
            return False
        
        # REFACTOR Phase
        return self.run_refactor_phase()


def main():
    """CLI for TDD runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test-Driven Development Runner")
    parser.add_argument("--phase", choices=["red", "green", "refactor", "cycle"], 
                       default="cycle", help="TDD phase to run")
    parser.add_argument("--test-file", help="Specific test file to run")
    parser.add_argument("--watch", action="store_true", help="Watch mode")
    
    args = parser.parse_args()
    
    tdd = TDDRunner()
    
    if args.watch:
        tdd.watch_mode()
    elif args.phase == "red":
        tdd.run_red_phase(args.test_file)
    elif args.phase == "green":
        tdd.run_green_phase(args.test_file)
    elif args.phase == "refactor":
        tdd.run_refactor_phase()
    elif args.phase == "cycle":
        tdd.run_tdd_cycle(args.test_file)


if __name__ == "__main__":
    main()