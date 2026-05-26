import os, glob
files = glob.glob('frontend/**/*.py', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('use_container_width=True', 'width="stretch"')
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print("Done")
