import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env import create_app
app = create_app()

def main():
    app.run(host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
