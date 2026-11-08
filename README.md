# IA na prática: fluxos de agentes para redações e equipes de comunicação

Ferramentas e regras testadas no [marcelofleury.com](https://marcelofleury.com), publicação do jornalista Marcelo Fleury, para usar IA na produção de conteúdo sem abrir mão da revisão humana. São abertas para quem trabalha com jornalismo, comunicação ou outros setores e quer adaptá-las.

A ideia central: **o modelo de linguagem decide e escreve; programas fixos e testados conferem, montam e travam.** Nenhuma matéria é publicada por um agente. A automação entrega rascunhos, e uma pessoa revisa e publica.

A explicação completa, com números e ressalvas, está na página [IA na prática](https://marcelofleury.com/laboratorio-de-ia/).

## O que tem aqui

| Pasta | O que faz |
| --- | --- |
| [`redacao/`](redacao/README.md) | Transforma um estudo em rascunho de matéria. O extrator lista as frases com números; a IA escreve e aponta, para cada número, o trecho literal da fonte; o validador confere tudo sem IA; o montador gera os blocos do WordPress; o envio cria só rascunhos. |
| [`wordpress/`](wordpress/README.md) | Trava instalada no próprio WordPress: a conta da automação não publica nem altera conteúdo publicado. Inclui um teste que tenta furar a trava. |
| [`skills/garimpo-pautas/`](skills/garimpo-pautas/SKILL.md) | Skill de garimpo de pautas em quatro frentes (radar do momento, pautas pouco cobertas, agenda e estudos novos), com o mesmo prompt para comparar ferramentas de IA. |
| [`AGENTES.md`](AGENTES.md) | Regras para várias ferramentas de IA e pessoas trabalharem no mesmo site sem desfazer o trabalho umas das outras. |

## O que o teste mostrou

No primeiro uso, em novembro de 2026, o fluxo gerou 3 rascunhos de matérias a partir de estudos em inglês. Para medir a checagem, cada um dos 40 números citados foi trocado por um valor vizinho (3,21 por 3,22):

| Regra | Adulterações detectadas |
| --- | --- |
| O número aparece em algum ponto do estudo | 31% |
| Cada número exige um trecho literal (erro só no texto) | 82% |
| Cada número exige um trecho literal (erro no texto e na ficha) | 95% |

A releitura humana ainda encontrou 2 erros que nenhuma regra pegaria. O validador confere forma e números, não ângulo, interpretação ou gramática.

## Começar

Python 3.12 ou superior.

```bash
cd redacao
pip install -r requirements.txt
python skills/materia_validador/skill.py materias/01-marcas-busca-generativa.md
```

O passo a passo para ligar ao seu WordPress está em [`redacao/README.md`](redacao/README.md).

## Ressalvas

- Os fluxos foram testados num único site, com amostras pequenas.
- As regras do validador seguem o manual de redação do marcelofleury.com (título em caixa baixa, lide clássico, sem linha fina). Ajuste `redacao/skills/materia_validador/manifest.yaml` ao manual da sua equipe.
- Ferramentas, modelos e preços mudam rápido. Confira as condições atuais antes de adotar.
- Use uma conta própria para a automação, com o mínimo de permissões, e guarde senhas fora do código.

## Contribuir

Correções, adaptações para outros sistemas e relatos de uso são bem-vindos. Veja [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença

Código sob [MIT](LICENSE). As matérias de exemplo em `redacao/materias/` são © Marcelo Fleury, publicadas no marcelofleury.com e incluídas só para os testes; o estudo em `redacao/fontes/` é dos seus autores, sob CC BY 4.0 (ver [`redacao/fontes/README.md`](redacao/fontes/README.md)).
