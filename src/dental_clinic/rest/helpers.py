def formatDateDigibee(data: str) -> type[str]:
    data = data[0:10]
    data = data.replace("-", "")
    return data

def formatCNPJDigibee(cnpj: str) -> type[str]:
    cnpj.replace("-", "")
    cnpj.replace(".", "")
    cnpj.replace("/", "")
    
    if len(cnpj) == 14:
        return cnpj
    
    cnpj = [int(d) for d in cnpj if d.isdigit()]
    if len(cnpj) != 12:
        raise ValueError("O CNPJ deve conter 14 dígitos")
    
    soma = 0
    peso = 5
    for i in range(0, 12):
        soma += cnpj[i] * peso
        peso -= 1
        if peso == 1:
            peso = 9
    
    resto = soma % 11
    if resto < 2:
        digito_1 = 0
    else:
        digito_1 = 11 - resto
    
    cnpj.append(digito_1)
    
    soma = 0
    peso = 6
    for i in range(0, 13):
        soma += cnpj[i] * peso
        peso -= 1
        if peso == 1:
            peso = 9
    
    resto = soma % 11
    if resto < 2:
        digito_2 = 0
    else:
        digito_2 = 11 - resto
    
    cnpj.append(digito_2)
    
    return ''.join(map(str, cnpj[14:]))