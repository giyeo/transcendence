const translations = {
	"login-guest": {
		"en": "Play as guest",
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
	"2FAButtonToggle": {
		"en": "Toggle 2FA",
		"pt": "Alternar 2FA",
		"fr": "Basculer la 2FA",
	},
	"2FAButtonSendOTP": {
		"en": "Send OTP",
		"pt": "Enviar OTP",
		"fr": "Envoyer OTP",
	},
	"send-login-OTP": {
		"en": "Send OTP",
		"pt": "Enviar OTP",
		"fr": "Envoyer OTP",
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
		"pt": "Carregando...",
		"fr": "Chargement...",
	},
	"logoutButton": {
		"en": "Logout",
		"pt": "Sair",
		"fr": "Déconnexion",
	},
	"settingsButton": {
		"en": "Settings",
		"pt": "Configurações",
		"fr": "Paramètres",
	},
};

export function updateLanguage(selectedLanguage) {
	console.log("Selected Language:", selectedLanguage)
	var elementsToUpdate = document.querySelectorAll('.translation');
	elementsToUpdate.forEach(function(element) {
		element.innerHTML = translations[element.id][selectedLanguage];
	});
}

export default updateLanguage