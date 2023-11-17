var userData;
var randomUserData;

import {updateLanguage} from './language.js';
import {startGame, gameSocket} from './game.js';
import * as REST from './rest.js';
import * as UTIL from './util.js'

function mountMenu() {
	let img = "";
	let displayname = "";
	let login = "";
	if(randomUserData) {
		img = randomUserData.picture.large
		displayname = randomUserData.name.first + randomUserData.name.last
		login = randomUserData.login.username
	}
	if(userData) {
		img = userData.image.versions.medium
		displayname = userData.displayname
		login = userData.login
	}
	document.getElementById("image").src = img;
	document.getElementById("displayName").innerText = displayname;
	document.getElementById("loginName").innerText = login;
}

async function goToMenu(intraCode, intraAccessToken) {
	window.location.hash = 'loading'
	try {
		if(intraCode || intraAccessToken)
			userData = await REST.getUserData(intraCode, intraAccessToken);
		else
			await REST.getRandomUserData();
		if (!userData["access_token"]) {
			window.location.hash = 'login_otp'
		}
		else {
			mountMenu();
			window.location.hash = 'menu'
		}
	} catch (error) {
		console.error('Error getting user data:', error);
		window.location.hash = 'login'
	}
}

async function sendOTP(accessToken) {
	let otpText = document.getElementById('2fa-activation-input');
	let qrcodeImage = document.getElementById('2fa-button-qrcode');
	let inputActivationOTP = document.getElementById('input-activation-OTP')
	let a = await REST.verifyOTP(otpText.value, accessToken)
	console.log(a)
	if(a === 200) {
		otpText.value = ""
		qrcodeImage.style.display = "none"
		inputActivationOTP.style.display = "none"
	}
}

async function runGame() {
	window.location.hash = 'game'
	if (!gameSocket) {
		await startGame(userData);
	}
	window.location.hash = 'menu'
}

function setupSinglePageApplication() {
	let intraCode = UTIL.getIntraCode();
	let intraAccessToken = UTIL.getIntraAccessToken();
	let accessToken = UTIL.getAccessToken();
	console.log("intraCode: " + intraCode)
	console.log("intraAccessToken: " + intraAccessToken)
	var selectedLanguage = localStorage.getItem("selectedLanguage") || "en";
	document.getElementById("languageSelectMenu").value = selectedLanguage;
	document.getElementById("languageSelectLogin").value = selectedLanguage;

	window.location.hash = 'login';
	UTIL.removeQueryParam('code');

	if (intraCode || intraAccessToken) {
		console.log("intraCode or intraAccessToken defined, going to menu")
		goToMenu(intraCode, intraAccessToken);
	}

	document.getElementById('find-match').addEventListener('click', () => {
		runGame();
	});

	document.getElementById('2fa-button').addEventListener('click', () => {
		REST.getQRCode(UTIL.getAccessToken())
	});

	document.getElementById('sendOTP').addEventListener('click', () => {
		sendOTP(accessToken);
	});

	document.getElementById('login-guest').addEventListener('click', () => {
		goToMenu();
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
	})

	var languageSelectMenu = document.getElementById('languageSelectMenu');
	languageSelectMenu.addEventListener('change', () => {
		selectedLanguage = languageSelectMenu.value;
		if (["en", "pt", "fr"].includes(selectedLanguage)) {
			localStorage.setItem("selectedLanguage", selectedLanguage);
			updateLanguage(selectedLanguage);
			REST.sendLanguage(accessToken, selectedLanguage);
		}
	})

	updateLanguage(selectedLanguage);

	var logoutButton = document.getElementById('logout');
	logoutButton.addEventListener('click', () => {
		localStorage.removeItem("intra_access_token");
		localStorage.removeItem("intra_access_token_expires_at");
		localStorage.removeItem("access_token");
		localStorage.removeItem("access_token_expires_at");
		window.location.reload();
	});
}

document.addEventListener('DOMContentLoaded', setupSinglePageApplication);

export { userData, randomUserData}