import base64
import os

md_path = r'c:\Users\Facundo\Documents\Programación Visual\regelabo\docs\presentation_data.md'
img_path = r'c:\Users\Facundo\Documents\Programación Visual\regelabo\docs\verhulst_model.png'

with open(img_path, 'rb') as f:
    img_data = f.read()
    base64_data = base64.b64encode(img_data).decode('utf-8')

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the image reference with base64
new_content = content.replace('![Modelo de Verhulst](verhulst_model.png)', f'![Modelo de Verhulst](data:image/png;base64,{base64_data})')

temp_md = r'c:\Users\Facundo\Documents\Programación Visual\regelabo\docs\temp_presentation.md'
with open(temp_md, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Created {temp_md} with embedded image.")
