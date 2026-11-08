---
wp_id: 958
tipo: pagina
titulo: "Redação com IA e checagem automática: como funciona no marcelofleury.com"
slug: redacao-com-ia-checagem-automatica
seo:
  palavra_chave: redação com IA
  metadesc: "Como o marcelofleury.com usa redação com IA e checagem automática de números contra a fonte, e como o método pode ser aplicado a outras equipes."
foto:
  url: "https://images.unsplash.com/photo-1763568258314-24ef37bb52e2?w=1600&q=80&fm=jpg"
  legenda: "Notebook com código na tela. Foto: Daniil Komov/Unsplash"
  alt: "Tela de notebook exibindo linhas de código, com um pequeno bicho de pelúcia ao lado"
fontes: [../fontes/teste-2026-11-07.md]
numeros_derivados:
  "3,21": "exemplo ilustrativo; valor real da matéria sobre buscadores (2611.07614)"
  "3,22": "exemplo ilustrativo de adulteração usado no teste"
evidencias:
  - {numero: "3", trecho: "Matérias produzidas: 3, a partir de 3 estudos publicados no arXiv"}
  - {numero: "40", trecho: "Números checados nas três matérias: 40 números com evidência declarada."}
  - {numero: "31", trecho: "25 de 80 adulterações detectadas (31%)"}
  - {numero: "25", trecho: "25 de 80 adulterações detectadas (31%)"}
  - {numero: "80", trecho: "25 de 80 adulterações detectadas (31%)"}
  - {numero: "82", trecho: "33 de 40 adulterações detectadas (82%)"}
  - {numero: "95", trecho: "38 de 40 adulterações detectadas (95%)"}
  - {numero: "2", trecho: "Erros encontrados só na releitura humana: 2"}
---
O marcelofleury.com passou a produzir matérias a partir de estudos científicos com um fluxo em que a inteligência artificial escreve, programas fixos conferem o texto e uma pessoa decide o que é publicado. No primeiro teste, em novembro de 2026, o processo gerou 3 matérias sobre estudos em inglês, todas entregues como rascunho no padrão do site.

O método segue a proposta de um [estudo sobre agentes de IA](/agentes-ia-ferramentas-prontas-skillware-estudo/) publicado no mesmo mês: o modelo de linguagem decide o que fazer, e a execução fica com programas testados, que fazem sempre a mesma coisa.

## Como funciona

1. **Extração.** Um programa converte o PDF do estudo em texto e lista as frases que contêm números, com a frase original ao lado.
2. **Redação.** A IA escreve a matéria seguindo o manual de redação do site e indica, para cada número citado, o trecho literal do estudo que o sustenta.
3. **Validação.** Um segundo programa, sem uso de IA, confere o título, o tamanho do primeiro parágrafo, o número de intertítulos, as expressões vetadas pelo manual, a legenda da foto, os campos de SEO e a presença de um parágrafo sobre os limites do estudo. Também verifica se cada trecho citado existe na fonte e contém o número usado no texto. Matéria com erro não segue adiante.
4. **Rascunho.** Um terceiro programa monta o post no WordPress com foto, legenda, categorias e tags. Ele só cria rascunhos, e uma trava instalada no próprio site impede a conta da automação de publicar.
5. **Publicação.** O editor revisa o rascunho no painel e decide se publica.

## O que o teste mostrou

A primeira versão da checagem de números apenas verificava se o número aparecia em algum ponto do estudo. Para medir a eficácia, cada número das três matérias foi trocado por um valor vizinho, como 3,21 por 3,22. Essa regra detectou 25 de 80 adulterações, ou 31%: um estudo longo contém quase qualquer número em algum lugar.

Com a exigência de um trecho literal para cada número, a detecção subiu para 82% quando o erro estava só no texto e para 95% quando texto e ficha de evidências foram alterados juntos. Os casos que escaparam são números vizinhos que aparecem na mesma frase do estudo, como "sete de oito".

A releitura humana continuou necessária. Ela encontrou 2 erros que nenhuma regra automática pegaria: uma concordância verbal e um verbo que descrevia o processo de forma imprecisa.

## Como aplicar em outras equipes

O mesmo método pode ser adaptado a redações, assessorias de imprensa, órgãos públicos e empresas que publicam dados. O trabalho tem quatro partes:

- **Manual em regras.** Leitura do manual de estilo da equipe e separação do que um programa pode conferir do que depende de leitura humana.
- **Validador próprio.** Programa com as regras da equipe, incluindo a checagem de números contra as fontes, como balanços, pesquisas e relatórios.
- **Ligação com o site.** Envio ao sistema de publicação da equipe apenas como rascunho, com uma conta separada e senhas guardadas fora do código.
- **Treinamento.** Orientação para revisar, corrigir e publicar, e para transformar correções frequentes em novas regras.

Os limites são claros. O resultado vem de um teste com 3 matérias e 40 números conferidos, e será atualizado com o uso diário. O validador confere forma e números, mas não avalia o ângulo da matéria, a interpretação nem a gramática, que continuam com o editor.
