# Quando usar

Antes de enviar qualquer matéria ao WordPress. Rode `python skills/materia_validador/skill.py materias/<arquivo>.md`.

# Como ler o laudo

- `erros`: bloqueiam o envio. Corrija o texto e rode de novo.
- `avisos`: não bloqueiam, mas pedem leitura (ex.: palavras em maiúscula no título que podem não ser nomes próprios).
- `numeros_conferidos`: quantos números do texto foram checados contra as fontes.

# Números

Todo número do texto (exceto anos e inteiros até 10) precisa existir em alguma fonte listada em `fontes`.
Se o número for uma conta feita pela redação (ex.: diferença entre dois valores), declare em
`numeros_derivados` com a conta, para o editor conferir:

```yaml
numeros_derivados:
  "70,6": "1 - 1.620/5.520, calculado pela redação"
```

# Limites

O validador não julga qualidade, ângulo nem interpretação. Ele garante forma e números; o resto é edição humana.
