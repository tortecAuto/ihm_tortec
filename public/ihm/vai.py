import json

def update_y_values(json_file_path):
    # Abrir o arquivo JSON e carregar os dados com codificação UTF-8
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Percorrer todos os elementos no array de 'element'
    for element in data[0]['element']:
        # Verificar se a chave 'y' existe no dicionário
        if 'y' in element:
            # Incrementar o valor de 'y' por 60
            element['y'] += 60

    # Salvar os dados modificados de volta no arquivo JSON, usando codificação UTF-8
    with open(json_file_path, 'w', encoding='utf-8') as file:
        # Usar 'ensure_ascii=False' para evitar que caracteres especiais sejam escapados
        json.dump(data, file, indent=4, ensure_ascii=False)
# Caminho do arquivo JSON
json_file_path = 'prog.json'

# Chamar a função para atualizar os valores de 'y'
update_y_values(json_file_path)