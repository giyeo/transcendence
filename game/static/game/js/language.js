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
	"madeby": {
		"en": "Made by The Boys { Caio, Eduardo, Luigi, Rafael }",
		"pt": "Feito por The Boys { Caio, Eduardo, Luigi, Rafael }",
		"fr": "Réalisé par The Boys { Caio, Eduardo, Luigi, Rafael }",
	},
	"instructions2FA1": {
		"en": "To toggle 2FA, scan the QR code below with your 2FA app and enter the OTP code.",
		"pt": "Para alternar 2FA, escaneie o código QR abaixo com seu aplicativo 2FA e insira o código OTP.",
		"fr": "Pour basculer la 2FA, scannez le code QR ci-dessous avec votre application 2FA et entrez le code OTP.",
	},
	"changeAliasName": {
		"en": "Change Alias Name",
		"pt": "Alterar nome de alias",
		"fr": "Changer le nom d'alias",
	},
	"clearAliasName": {
		"en": "Clear Alias Name",
		"pt": "Limpar nome de alias",
		"fr": "Effacer le nom d'alias",
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