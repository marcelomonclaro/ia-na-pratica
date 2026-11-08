# Trava da automação no WordPress

`trava-automacao.php` impede a conta usada pela automação de publicar, agendar, apagar ou alterar conteúdo publicado e conteúdo de outras pessoas. Ela continua podendo criar rascunhos e subir imagens.

São duas barreiras:

1. tira dessa conta as capacidades de publicar e de mexer no que é publicado ou de outras pessoas;
2. qualquer status diferente de rascunho enviado por ela (publicado, agendado, privado, pendente) vira rascunho.

## Instalar

1. Copie `trava-automacao.php` para `wp-content/mu-plugins/` no servidor (crie a pasta se não existir). Plugins "must-use" carregam sempre e não aparecem para desativar no painel.
2. No `wp-config.php`, antes da linha `/* That's all, stop editing! */`, informe o login da conta da automação:
   ```php
   define( 'TRAVA_USUARIO_AUTOMACAO', 'login-da-conta' );
   ```
   Sem essa linha, a trava vale para a conta de login `automacao`.
3. Rode `python redacao/tools/verificar_trava.py` com as credenciais da conta da automação nas variáveis de ambiente. O teste reprova se conseguir publicar ou editar conteúdo publicado.

## Limites

- A trava é uma camada a mais. Ela não substitui senha forte, verificação em duas etapas para administradores e o menor papel possível para a conta da automação.
- O papel Editor, necessário para criar páginas, dá outras capacidades (HTML sem filtro, categorias, comentários) que a trava não tira.
- Como a busca por endereço não enxerga rascunhos de outras pessoas, o envio guarda o `wp_id` no arquivo da matéria para não duplicar.
