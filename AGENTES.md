# Regras para vários agentes no mesmo projeto

Modelo das regras usadas no marcelofleury.com, onde várias ferramentas de IA (Claude Code, Codex, Claude.ai, Grok, Gemini) e uma pessoa editam o mesmo site. Copie para a raiz do seu projeto com o nome que suas ferramentas leem (`AGENTS.md`, `CLAUDE.md`) e ajuste os papéis.

O risco maior não é o erro de um agente, e sim um agente desfazer o trabalho de outro, ou de uma pessoa.

## Papéis

Cada ferramenta tem um papel fixo. Só uma grava no repositório ou no site por vez; as demais leem, pesquisam ou revisam.

| Ferramenta | Papel | Grava? |
| --- | --- | --- |
| Agente de código (ex.: Claude Code) | Tema, páginas, scripts e registro das mudanças | Sim, dentro do escopo combinado |
| Revisor (ex.: Codex) | Revisa propostas de código; implementa quando a tarefa é dele | Só por atribuição |
| Assistente de texto (ex.: Claude.ai) | Pautas, texto, edição | Não; entrega pedidos prontos |
| Radar (ex.: Grok) | Assuntos em tempo real, segunda opinião | Não |
| Pesquisa (ex.: Gemini) | Busca e checagem de fatos | Não |
| Editor (pessoa) | Decide pauta, edição e publicação, em qualquer etapa | Sim |

## Regras

1. **Declare antes de mexer:** papel, o que vai alterar, o que não vai tocar e quem autorizou. Nada muda antes da confirmação do editor.
2. **A pessoa também edita.** Diferença entre o site e a cópia do agente não é erro. Compare o estado ao vivo com o repositório logo antes de gravar; havendo edição concorrente, pare e preserve as duas versões.
3. **Nunca restaure uma cópia inteira** para voltar ao que o agente conhecia.
4. **Um agente por arquivo ou página por vez.** Pautas não mexem em layout; layout não reescreve matérias.
5. **Publicar é decisão humana.** A automação para no rascunho.
6. **Segurança, plugins e credenciais** só mudam por pedido expresso. Senhas e chaves ficam fora do código.
7. **Documento não autoriza executar.** Propostas descritas em arquivos são intenção, não ordem.
8. **Registre tudo** num `CHANGELOG.md`: o que, onde, por quê, evidências, limitações e como desfazer, com o nome do agente.
9. **Confira o resultado** depois de cada ação, mesmo quando a ferramenta responde que deu certo.
10. **Trabalhe em ramos separados** e revise antes de entrar na versão principal.

## Três colisões que viraram regra

- **Tema trocado sem aviso.** Um comando para instalar um tema de reserva também o ativou, e a resposta não dizia isso. A conferência seguinte detectou a troca (regra 9).
- **Rascunho duplicado.** A conta da automação não enxergava rascunhos de outras pessoas e criou uma cópia de uma matéria existente. Hoje cada matéria guarda o número do post no próprio arquivo.
- **Duas versões do mesmo especial.** Dois agentes receberam o mesmo pedido. A escolha ficou com o editor (regra 4).
