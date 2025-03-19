pattern = [
    # size
    {'Size': 'Size'},
    {'Length': 'Size'},
    {'Height': 'Size'},
    {'Width': 'Size'},
    {'Style': 'Style'},
    {'Themes': 'Style'},
    {'Theme': 'Style'},
    {'Season': 'Style'},
    {'Event': 'Style'},
    {'Pattern': 'Style'},
    {'Occasion': 'Style'},
    {'Flavour': 'Flavour'},
    # material
    {'Upholstery': 'Material'},
    {'Materials': 'Material'},
    {'Material': 'Material'},
    {'Tool Surface Compatibility': 'Material'},
    {'Texture': 'Material'},
    {'Fabric': 'Material'},
    {'Finish': 'Material'},
    {'Glass': 'Material'},
    # feature
    {'Features': 'Feature'},
    {'Feature': 'Feature'},
    {'Connectivity': 'Feature'},
    {'Connection': 'Feature'},
    {'Cellular': 'Feature'},
    {'Network': 'Feature'},
    {'Functions': 'Feature'},
    {'Function': 'Feature'},
    {'Ingredient': 'Feature'},
    {'Benefits': 'Feature'},
    {'Diet': 'Feature'},
    # sku]
    {'Colour': 'SKU'},
    {'Tone': 'SKU'},
    {'Interface': 'SKU'},
    {'Power': 'SKU'},
    {'Water': 'SKU'},
    {'Shape': 'SKU'},
    {'Number': 'SKU'},
    {'Scent': 'SKU'},
    {'Form': 'SKU'},
    {'Formulation': 'SKU'},
    {'Design': 'SKU'},
    # others
    {'Region': 'Region'},
    {'Language': 'Region'},
    {'Type': 'Type'},
    {'Display': 'Type'},
    {'Brand': 'Brand'},
    {'Teams': 'Brand'},
    {'Manufacturer': 'Brand'},
    {'Assistant': 'Brand'},
    # people
    {'Gender': 'People'},
    {'Age': 'People'},
    {'Baby': 'People'},
    {'Religion': 'People'},
    {'Life': 'People'},
]

label_list = set([list(i.values())[0] for i in pattern])
label_list = ['O'] + [f'B-{i}' for i in label_list] + [f'I-{i}' for i in label_list]

label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for i, label in enumerate(label_list)}

