# Redação automatizada com travas

O modelo de linguagem escreve e escolhe as evidências; programas fixos e testados fazem o resto; uma pessoa publica.

| Pacote | O que faz | Trava |
| --- | --- | --- |
| `skills/estudo_extrator` | PDF de estudo → texto e metadados (corta as referências) e `achar.py` para localizar trechos; `ficha.py` lista as frases com números | Não resume nem interpreta |
| `skills/materia_validador` | Confere a matéria contra o manual de redação (título, lide, intertítulos, expressões vetadas, SEO, legenda e texto alternativo da foto, status) e exige, para cada número do texto, um trecho literal da fonte que o contenha | Número sem evidência = erro |
| `skills/wp_rascunho` | Markdown → blocos do editor do WordPress + JSON para a API REST | Matéria reprovada não sai |
| `tools/enviar_rascunho.py` | Envia ao WordPress pela API REST com a conta da automação | Confere que o site gravou rascunho; não duplica matéria que já tem `wp_id` |
| `tools/verificar_trava.py` | Tenta publicar ao criar, publicar o rascunho e abrir um post publicado para edição | Reprova se algum passo passar |
| [`../wordpress/trava-automacao.php`](../wordpress/README.md) | Plugin obrigatório no servidor: a conta da automação não publica | Trava no próprio site |

Cada pacote tem `manifest.yaml` (contrato), `skill.py` (código), `instructions.md` e `test_skill.py` (testes offline).

## O fluxo

1. **Extração:** `python skills/estudo_extrator/skill.py fontes/pdf/estudo.pdf` e `python skills/estudo_extrator/ficha.py fontes/estudo.txt` para listar as frases com números.
2. **Redação:** a IA escreve a matéria em Markdown com cabeçalho YAML, no formato de `materias/01-marcas-busca-generativa.md`. Para cada número, ela registra em `evidencias` o trecho literal da fonte.
3. **Validação:** `python skills/materia_validador/skill.py materias/arquivo.md`. Com erro, a matéria volta para a IA ou para o editor.
4. **Rascunho:** `python tools/enviar_rascunho.py materias/arquivo.md --simular` mostra o que seria enviado; sem `--simular`, cria o rascunho.
5. **Publicação:** o editor revisa no WordPress e decide. Correções frequentes viram regras novas em `skills/materia_validador/manifest.yaml`.

## Ligar ao seu WordPress

1. Crie no WordPress uma conta só para a automação (papel Autor basta para posts; Editor, se for criar páginas).
2. Instale a trava em `wp-content/mu-plugins/` e defina o login dessa conta no `wp-config.php` (ver [`../wordpress/README.md`](../wordpress/README.md)).
3. Em Usuários > (conta da automação) > Senhas de aplicativo, gere uma senha.
4. Defina as variáveis de ambiente `WP_URL`, `WP_USER` e `WP_APP_PASSWORD`. Nunca grave a senha em arquivo.
5. Rode `python tools/verificar_trava.py`. Ele cria um rascunho de teste, que o editor apaga com a própria conta.

No GitHub, o workflow [`.github/workflows/redacao.yml`](../.github/workflows/redacao.yml) roda os testes em cada pull request. Os jobs de envio e de verificação da trava só rodam à mão (Actions > Run workflow) e leem as credenciais de um ambiente chamado `wordpress` (Settings > Environments), que pode exigir aprovação antes de cada execução.

## Adaptar ao seu manual

As regras estão em `skills/materia_validador/manifest.yaml`: tamanho do título e do lide, número de intertítulos, expressões vetadas, campos obrigatórios. As do exemplo seguem o manual do marcelofleury.com. O campo `mf_format` em `skills/wp_rascunho/skill.py` é um metadado do tema daquele site; se o seu não o registrar, o envio tenta de novo sem ele.

## Testes

```bash
pip install -r requirements.txt
for d in skills/*/ tools/; do (cd "$d" && python -m pytest -q); done
```

Esperado: 27 passam e 1 é pulado (o do extrator procura PDFs em `fontes/pdf/`, que ficam fora do Git).

## Resultado do teste de sensibilidade

Cada um dos 40 números das 3 matérias do primeiro teste foi trocado por um valor vizinho:

- regra antiga ("o número existe em algum lugar do estudo"): 25 de 80 adulterações detectadas (31%);
- regra nova (trecho literal por número), troca só no texto: 33 de 40 (82%);
- regra nova, troca no texto e na ficha: 38 de 40 (95%).

As falhas restantes são números vizinhos que aparecem no mesmo trecho, como "sete de oito".
