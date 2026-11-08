<?php
/**
 * Plugin Name: Trava de publicação da automação
 * Description: O usuário da automação cria rascunhos e sobe fotos, mas não publica, não agenda e não altera conteúdo já publicado.
 * Version: 0.1.0
 *
 * Instalação: copiar para wp-content/mu-plugins/ (plugins "must-use" carregam sempre e não podem ser desativados pelo painel).
 * Configuração: defina o login da conta da automação no wp-config.php, antes da linha "That's all, stop editing":
 *   define( 'TRAVA_USUARIO_AUTOMACAO', 'login-da-conta' );
 * Sem essa linha, a trava vale para a conta de login "automacao".
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! defined( 'TRAVA_USUARIO_AUTOMACAO' ) ) {
	define( 'TRAVA_USUARIO_AUTOMACAO', 'automacao' );
}

function trava_e_automacao( $user_id = 0 ) {
	$user = $user_id ? get_userdata( $user_id ) : wp_get_current_user();
	return $user && $user->exists() && TRAVA_USUARIO_AUTOMACAO === $user->user_login;
}

/* 1. Remove as capacidades de publicar e de mexer no que já está publicado. */
add_filter(
	'user_has_cap',
	function ( $allcaps, $caps, $args, $user ) {
		if ( $user && TRAVA_USUARIO_AUTOMACAO === $user->user_login ) {
			foreach ( array( 'publish_posts', 'publish_pages', 'edit_published_posts', 'edit_published_pages', 'delete_published_posts', 'delete_published_pages', 'edit_others_posts', 'edit_others_pages', 'delete_others_posts', 'delete_others_pages' ) as $cap ) {
				$allcaps[ $cap ] = false;
			}
		}
		return $allcaps;
	},
	10,
	4
);

/* 2. Segunda barreira: qualquer status diferente de rascunho vira rascunho. */
add_filter(
	'wp_insert_post_data',
	function ( $data ) {
		if ( trava_e_automacao() && in_array( $data['post_status'], array( 'publish', 'future', 'private', 'pending' ), true ) ) {
			$data['post_status'] = 'draft';
		}
		return $data;
	},
	99
);
