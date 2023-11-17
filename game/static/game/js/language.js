const translations = {
	"login-guest": {
		"en": "Play as Guest",
		"pt": "Jogar como convidado",
		"fr": "Jouer en tant qu'invité",
	},
	"login-intra": {
		"en": "Play as 42",
		"pt": "Jogar como 42",
		"fr": "Jouer en tant que 42",
	},
	"find-match": {
		"en": "Find Match",
		"pt": "Encontrar partida",
		"fr": "Trouver une partie",
	},
	"2fa-button": {
		"en": "Toggle 2FA",
		"pt": "Alternar 2FA",
		"fr": "Basculer la 2FA",
	},
	"sendOTP": {
		"en": "Enter",
		"pt": "Entrar",
		"fr": "Entrer",
	},
	"send-login-OTP": {
		"en": "Enter",
		"pt": "Entrar",
		"fr": "Entrer",
	},
	"wait-other-players": {
		"en": "Waiting for other players...",
		"pt": "Aguardando outros jogadores...",
		"fr": "En attente d'autres joueurs...",
	},
	"game-over": {
		"en": "Game Over",
		"pt": "Fim de jogo",
		"fr": "Fin du jeu",
	},
	"loading": {
		"en": "Loading...",
		"pt": "Esperando...",
		"fr": "Chargement...",
	},
	"logout": {
		"en": "Logout",
		"pt": "Sair",
		"fr": "Se déconnecter",
	},
};

function updateLanguage(selectedLanguage) {
	console.log("Selected Language:", selectedLanguage)
	var elementsToUpdate = document.querySelectorAll('.translation');
	elementsToUpdate.forEach(function(element) {
		element.innerHTML = translations[element.id][selectedLanguage];
	});
}