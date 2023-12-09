var userData;
var randomUserData;
var matchType = "simpleMatch";
var gameMode = "defaultGameMode";
var matchSuggestedName = "";

import {updateLanguage} from './language.js';
import {startGame, gameSocket} from './game.js';
import * as REST from './rest.js';
import * as UTIL from './util.js'

function mountMenu() {
	let img = "";
	let login = "";
	if(randomUserData) {
		img = randomUserData.picture.large
		login = randomUserData.login.username
	}
	if(userData) {
		img = userData.image.versions.medium
		login = userData.login
		var gameModeElement = document.getElementById('gameModeElement');
		gameModeElement.style.display = "block";
	}
	document.getElementById("image").src = img;
	if (localStorage.getItem("aliasName")) {
		document.getElementById("loginName").innerText = login + " - " + localStorage.getItem("aliasName");
	} else {
		document.getElementById("loginName").innerText = login;
	}

}

async function goToMenu(intraCode, intraAccessToken) {
	window.location.hash = 'loading'
	try {
		if(intraCode || intraAccessToken) {
			await REST.getUserData(intraCode, intraAccessToken);
			if (userData) {
				if (!UTIL.getAccessToken()) {
					window.location.hash = 'login_otp'
				} else {
					mountMenu();
					window.location.hash = 'menu'
				}
			}
		} else {
			await REST.getRandomUserData();
			if (randomUserData) {
				mountMenu();
				window.location.hash = 'menu'
			} else {
				window.location.hash = 'login'
			}

		}
	} catch (error) {
		window.location.hash = 'login'
	}
}

async function sendOTP(accessToken) {
	let otpText = document.getElementById('2FAInputOTP');
	let qrcodeImage = document.getElementById('2FAImageQRCode');
	let status2FAElement = document.getElementById('2FAStatus');
	let verified = await REST.verifyOTP(otpText.value, accessToken)
	if (verified) {
		otpText.value = ""
		verified.twofa_enabled ? status2FAElement.innerHTML = "ACTIVATED" : status2FAElement.innerHTML = "DEACTIVATED";
		qrcodeImage.src = "";
		return true;
	} else {
		return false;
	}
}

async function runGame() {
	window.location.hash = 'game'
	if (!gameSocket) {
		await startGame();
	}
	window.location.hash = 'menu'
}

function logout() {
	randomUserData = null;
	userData = null;
	localStorage.removeItem("intra_access_token");
	localStorage.removeItem("access_token");
	localStorage.removeItem("access_token_expires_at");
	localStorage.removeItem("aliasName");
	localStorage.removeItem("selectedLanguage");
	window.location.reload();
}

function setupSinglePageApplication() {
	window.location.hash = 'login';
	let intraCode = UTIL.getIntraCode();
	var selectedLanguage = localStorage.getItem("selectedLanguage") || "en";
	var matchSuggestedNameElement = document.getElementById('matchSuggestedName');
	document.getElementById("languageSelectMenu").value = selectedLanguage;
	document.getElementById("languageSelectLogin").value = selectedLanguage;
	UTIL.removeQueryParam('code');

	if (intraCode || UTIL.getIntraAccessToken()) {
		goToMenu(intraCode, UTIL.getIntraAccessToken());
	}

	document.getElementById('find-match').addEventListener('click', () => {
		matchSuggestedName = matchSuggestedNameElement.value;
		matchTypeElement.value = "simpleMatch";
		runGame();
		matchSuggestedNameElement.value = "";
	});

	var buttonToggle2FA = document.getElementById('2FAButtonToggle')
	buttonToggle2FA.addEventListener('click', () => {
		REST.getQRCode(UTIL.getAccessToken())
	});

	var buttonSendOTP = document.getElementById('2FAButtonSendOTP')
	buttonSendOTP.addEventListener('click', async () => {
		let element2FAMessage = document.getElementById('2FAMessage');
		let verified = await sendOTP(UTIL.getAccessToken());
		if (verified) {
			element2FAMessage.innerText = "OTP verified. 2FA toggled.";
		} else {
			element2FAMessage.innerText = "Invalid OTP";
		}
		setTimeout(() => {element2FAMessage.innerText = "";}, 1500);
	});

	var matchTypeElement = document.getElementById('matchTypeElement');

	// document.getElementById('login-guest').addEventListener('click', () => {
	// 	goToMenu();
	// 	matchTypeElement.style.display = "none";
	// 	buttonToggle2FA.removeEventListener("click", () => {});
	// 	buttonToggle2FA.style.display = "none";
	// 	buttonSendOTP.removeEventListener("click", () => {});

	// });

	document.getElementById('send-login-OTP').addEventListener('click', async () => {
		let accessToken = await REST.verifyLoginOTP(document.getElementById('2fa-login-input').value);
		let otpMessageElement = document.getElementById('otp-login-message');
		if (accessToken) {
			otpMessageElement.innerText = "";
			goToMenu();
		} else {
			otpMessageElement.innerText = "Invalid OTP";
			setTimeout(() => {otpMessageElement.innerText = "";}, 1500);
		}
	});

	document.getElementById('login-intra').addEventListener('click', () => {
		if (UTIL.getIntraAccessToken()) {
			window.location.reload();
		} else {
			window.location.href = INTRA_API_URL_AUTH + "?client_id=" + INTRA_CLIENT_ID + "&redirect_uri=" + INTRA_REDIRECT_URI + "&response_type=" + INTRA_RESPONSE_TYPE;;
		}
	});

	var languageSelectLogin = document.getElementById('languageSelectLogin');
	languageSelectLogin.addEventListener('change', () => {
		selectedLanguage = languageSelectLogin.value;
		if (["en", "pt", "fr"].includes(selectedLanguage)) {
			localStorage.setItem("selectedLanguage", selectedLanguage);
			updateLanguage(selectedLanguage);
		}
	});

	var languageSelectMenu = document.getElementById('languageSelectMenu');
	languageSelectMenu.addEventListener('change', () => {
		selectedLanguage = languageSelectMenu.value;
		if (["en", "pt", "fr"].includes(selectedLanguage)) {
			localStorage.setItem("selectedLanguage", selectedLanguage);
			updateLanguage(selectedLanguage);
			REST.sendLanguage(UTIL.getAccessToken(), selectedLanguage);
		}
	});

	updateLanguage(selectedLanguage);

	var logoutButton = document.getElementById('logoutButton');
	logoutButton.addEventListener('click', () => {
		logout();
	});

	var selectTournamentNameElement = document.getElementById('selectTournamentName');

	matchTypeElement.value = "simpleMatch";
	matchTypeElement.addEventListener('change', () => {
		if (matchTypeElement.value === "simpleMatch") {
			matchType = "simpleMatch";
			selectTournamentNameElement.style.display = "none";
			if (gameModeElement.length === 1) {
				var option = document.createElement("option");
				option.text = "Crazy";
				option.value = "crazyGameMode";
				gameModeElement.add(option);
			}
		}
		else if (matchTypeElement.value === "tournamentMatch") {
			matchType = "tournamentMatch";
			selectTournamentNameElement.style.display = "block";
			if (gameModeElement.value != "defaultGameMode" || gameMode != "defaultGameMode") {
				gameModeElement.value = "defaultGameMode";
				gameMode = "defaultGameMode";
			}
			gameModeElement.remove(1);
		}
		else {
			matchType = "simpleMatch";
			selectTournamentNameElement.style.display = "none";
			if (gameModeElement.length === 1) {
				var option = document.createElement("option");
				option.text = "Crazy";
				option.value = "crazyGameMode";
				gameModeElement.add(option);
			}
		}
		matchSuggestedNameElement.value = "";
	});

	var gameModeElement = document.getElementById('gameModeElement');

	gameModeElement.value = "defaultGameMode";
	if (userData) {
		gameModeElement.style.display = "block";
	} else {
		gameModeElement.style.display = "none";
	}
	gameModeElement.addEventListener('change', () => {
		if (gameModeElement.value === "defaultGameMode") {
			gameMode = "defaultGameMode";
			if (matchTypeElement.length === 1) {
				var option = document.createElement("option");
				option.text = "Tournament Match";
				option.value = "tournamentMatch";
				matchTypeElement.add(option);
			}
		} else if (gameModeElement.value === "crazyGameMode") {
			gameMode = "crazyGameMode";
			if (matchTypeElement.value != "simpleMatch" || matchType != "simpleMatch") {
				matchTypeElement.value = "simpleMatch";
				matchType = "simpleMatch";
				selectTournamentNameElement.style.display = "none";
				selectTournamentNameElement.value = "";
			}
			matchTypeElement.remove(1);
		} else {
			gameModeElement.value = "defaultGameMode";
			if (matchTypeElement.length === 1) {
				var option = document.createElement("option");
				option.text = "Tournament Match";
				option.value = "tournamentMatch";
				matchTypeElement.add(option);
			}
		}
	});

	var settingsButtonElement = document.getElementById('settingsButton');
	settingsButtonElement.addEventListener('click', () => {
		let languageElement = document.getElementById('language');
		let _2FAElement = document.getElementById('_2FA');
		if (languageElement.style.display === "block" && _2FAElement.style.display === "block") {
			languageElement.style.display = "none";
			_2FAElement.style.display = "none";
			return ;
		}
		languageElement.style.display = "block";
		_2FAElement.style.display = "block";
	});

	var aliasNameElement = document.getElementById('aliasName');
	var aliasNameButtonElement = document.getElementById('changeAliasName');
	var aliasNameClearButtonElement = document.getElementById('clearAliasName');
	aliasNameButtonElement.addEventListener('click', () => {
		if (aliasNameElement.value.length > 0) {
			localStorage.setItem("aliasName", aliasNameElement.value);
			if (userData) {
				document.getElementById("loginName").innerText = userData.login + " - " + aliasNameElement.value;
			} else if (randomUserData) {
				document.getElementById("loginName").innerText = randomUserData.login.username + " - " + aliasNameElement.value;
			}
		}
	});

	aliasNameClearButtonElement.addEventListener('click', () => {
		localStorage.removeItem("aliasName");
		if (userData) {
			document.getElementById("loginName").innerText = userData.login;
		} else if (randomUserData) {
			document.getElementById("loginName").innerText = randomUserData.login.username;
		}
	});
}

function updateMatchType(newMatchType) {
	matchType = newMatchType;
}

function updateUserData(newUserData) {
	userData = newUserData;
}

function updateRandomUserData(newRandomUserData) {
	randomUserData = newRandomUserData;
}

document.addEventListener('DOMContentLoaded', setupSinglePageApplication);

export { userData, updateUserData, randomUserData, matchType, gameMode, updateMatchType, runGame, logout, matchSuggestedName, updateRandomUserData }