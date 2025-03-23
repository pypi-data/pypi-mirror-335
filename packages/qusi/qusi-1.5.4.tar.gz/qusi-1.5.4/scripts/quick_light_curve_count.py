from pathlib import Path

base_path = Path('data/tess_light_curves')
injectee_paths_generator = base_path.glob('**/*.fits')
count = 0
for _ in injectee_paths_generator:
    count += 1
    if count % 1000 == 0:
        print(count)

