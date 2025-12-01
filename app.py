import runpy
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Main execution to run all components
if __name__ == "__main__":
    runpy.run_path(os.path.join(os.path.dirname(__file__), "src", "dash_gen.py"))