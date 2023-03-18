import json
from pathlib import Path
materials=json.loads(Path('material.json').read_text(encoding='utf-8'))
