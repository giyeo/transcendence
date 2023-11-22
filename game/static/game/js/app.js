var userData;
var randomUserData;
var matchType = "simpleMatch";
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
	}
	document.getElementById("image").src = img;
	document.getElementById("loginName").innerText = login;
}

async function goToMenu(intraCode, intraAccessToken) {
	window.location.hash = 'loading'
	try {
		if(intraCode || intraAccessToken) {
			await REST.getUserData(intraCode, intraAccessToken);
			if (userData) {
				if (!UTIL.getAccessToken()) {
					window.location.hash = 'login_otp'
				}
				else {
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
		console.error('Error getting user data:', error);
		window.location.hash = 'login'
	}
}

async function sendOTP(accessToken) {
	let otpText = document.getElementById('2FAInputOTP');
	let qrcodeImage = document.getElementById('2FAImageQRCode');
	//let inputActivationOTP = document.getElementById('input-activation-OTP')
	let a = await REST.verifyOTP(otpText.value, accessToken)
	console.log(a)
	if(a === 200) {
		otpText.value = ""
		qrcodeImage.style.display = "none"
		//inputActivationOTP.style.display = "none"
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
	window.location.reload();
}
  
function setupSinglePageApplication() {
	window.location.hash = 'login';
	let intraCode = UTIL.getIntraCode();
	let intraAccessToken = UTIL.getIntraAccessToken();
	let accessToken = UTIL.getAccessToken();
	console.log("intraCode: " + intraCode)
	console.log("intraAccessToken: " + intraAccessToken)
	var selectedLanguage = localStorage.getItem("selectedLanguage") || "en";
	var matchSuggestedNameElement = document.getElementById('matchSuggestedName');
	document.getElementById("languageSelectMenu").value = selectedLanguage;
	document.getElementById("languageSelectLogin").value = selectedLanguage;
	UTIL.removeQueryParam('code');

	if (intraCode || intraAccessToken) {
		console.log("intraCode or intraAccessToken defined, going to menu")
		goToMenu(intraCode, intraAccessToken);
	}

	document.getElementById('find-match').addEventListener('click', () => {
		matchSuggestedName = matchSuggestedNameElement.value;
		runGame();
		matchSuggestedNameElement.value = "";
	});

	var buttonToggle2FA = document.getElementById('2FAButtonToggle')
	buttonToggle2FA.addEventListener('click', () => {
		REST.getQRCode(UTIL.getAccessToken())
	});

	var buttonSendOTP = document.getElementById('2FAButtonSendOTP')
	buttonSendOTP.addEventListener('click', () => {
		sendOTP(accessToken);
	});

	var matchTypeElement = document.getElementById('matchTypeElement');

	document.getElementById('login-guest').addEventListener('click', () => {
		goToMenu();
		matchTypeElement.style.display = "none";
		buttonToggle2FA.removeEventListener("click", () => {});
		buttonToggle2FA.style.display = "none";
		buttonSendOTP.removeEventListener("click", () => {});

	});

	document.getElementById('send-login-OTP').addEventListener('click', () => {
		REST.verifyLoginOTP(document.getElementById('2fa-login-input').value);
		if(UTIL.getAccessToken()) {
			mountMenu();
			window.location.hash = 'menu';
		}
	});

	document.getElementById('login-intra').addEventListener('click', () => {
		let intraAccessToken = UTIL.getIntraAccessToken();
		if (intraAccessToken) {
			console.log("Already logged in");
			window.location.reload();
		} else {
			console.log("Not logged in. Redirecting...");
			let INTRA_API_URL_AUTH = "https://api.intra.42.fr/oauth/authorize"
			let INTRA_CLIENT_ID = "u-s4t2ud-d7f64afc7fb7dc2840609df8b5328f172dd434549cf932c6606762ecb4016c2d"
			let INTRA_REDIRECT_URI = "http://127.0.0.1:8000/game"
			let INTRA_RESPONSE_TYPE = "code"
			window.location.href = INTRA_API_URL_AUTH + "?client_id=" + INTRA_CLIENT_ID + "&redirect_uri=" + INTRA_REDIRECT_URI + "&response_type=" + INTRA_RESPONSE_TYPE;
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
			REST.sendLanguage(accessToken, selectedLanguage);
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
		console.log("CHANGING MATCH TYPE: ", matchTypeElement.value);
		if (matchTypeElement.value === "simpleMatch") {
			console.log("Simple");
			matchType = "simpleMatch";
			selectTournamentNameElement.style.display = "none";
		}
		else if (matchTypeElement.value === "tournamentMatch") {
			console.log("Tournament");
			matchType = "tournamentMatch";
			selectTournamentNameElement.style.display = "block";
		}
		else {
			console.log("Simple anyway");
			matchType = "simpleMatch";
			selectTournamentNameElement.style.display = "none";
		}
		matchSuggestedNameElement.value = "";
	});

	var settingsButtonElement = document.getElementById('settingsButton');
	settingsButtonElement.addEventListener('click', () => {
		let languageElement = document.getElementById('language');
		let _2FAElement = document.getElementById('2FA');
		if (languageElement.style.display === "block" && _2FAElement.style.display === "block") {
			languageElement.style.display = "none";
			_2FAElement.style.display = "none";
			return ;
		}
		languageElement.style.display = "block";
		_2FAElement.style.display = "block";
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

export { userData, updateUserData, randomUserData, matchType, updateMatchType, runGame, logout, matchSuggestedName, updateRandomUserData }