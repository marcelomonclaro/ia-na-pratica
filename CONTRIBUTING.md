# Como contribuir

Este repositório reúne fluxos testados num site jornalístico. Contribuições que os tornem mais úteis para outras redações, assessorias e empresas são bem-vindas.

## O que ajuda mais

- **Relatos de uso:** você adaptou um fluxo? Abra uma issue contando onde, o que funcionou e o que não funcionou. Números de teste (como os de detecção de adulterações) valem ouro.
- **Correções:** erros de código, testes que falham no seu sistema, documentação confusa.
- **Adaptações:** regras do validador para outros manuais de redação, envio para outros sistemas além do WordPress, outros idiomas.
- **Novos testes:** casos que o validador deixa passar e deveria pegar.

## Como enviar

1. Abra uma issue antes de mudanças grandes, para combinar o caminho.
2. Faça um fork e trabalhe num ramo próprio.
3. Rode os testes antes de enviar:
   ```bash
   cd redacao
   pip install -r requirements.txt
   for d in skills/*/ tools/; do (cd "$d" && python -m pytest -q); done
   ```
4. Abra o pull request explicando o que muda e por quê. Os testes rodam automaticamente.

## Regras do projeto

- **Revisão humana antes de publicar** é parte do desenho. Contribuições que permitam a um agente publicar sozinho não serão aceitas.
- **Nada de credenciais** em código, exemplos ou issues. Use variáveis de ambiente.
- **Fontes com licença aberta:** só inclua texto de estudos cuja licença permita redistribuição (CC BY, CC BY-SA, CC0), com a atribuição em `redacao/fontes/README.md`.
- **Matérias de exemplo** devem ser suas ou ter autorização do autor.
- Textos e mensagens em português; código e nomes podem seguir o padrão existente.

## Segurança

Achou uma falha que permita furar a trava ou expor credenciais? Escreva para contato@marcelofleury.com em vez de abrir uma issue pública.

## Conduta

Discussões objetivas e respeitosas. Críticas ao código e às ideias, nunca às pessoas.
