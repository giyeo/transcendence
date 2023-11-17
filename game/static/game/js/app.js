var userData;
var randomUserData;

API_URL = "http://127.0.0.1:8000"

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
			await getUserData(intraCode, intraAccessToken);
		else
			await getRandomUserData();
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
	otpText = document.getElementById('2fa-activation-input');
	qrcodeImage = document.getElementById('2fa-button-qrcode');
	inputActivationOTP = document.getElementById('input-activation-OTP')
	a = await verifyOTP(otpText.value, accessToken)
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
	let intraCode = getIntraCode();
	let intraAccessToken = getIntraAccessToken();
	let accessToken = getAccessToken();
	console.log("intraCode: " + intraCode)
	console.log("intraAccessToken: " + intraAccessToken)
	var selectedLanguage = localStorage.getItem("selectedLanguage") || "en";
	document.getElementById("languageSelectMenu").value = selectedLanguage;
	document.getElementById("languageSelectLogin").value = selectedLanguage;

	window.location.hash = 'login'
	removeQueryParam('code')

	if (intraCode || intraAccessToken) {
		console.log("intraCode or intraAccessToken defined, going to menu")
		goToMenu(intraCode, intraAccessToken);
	}

	findMatch = document.getElementById('find-match');
	findMatch.addEventListener('click', () => {
		runGame();
	});

	button2fa = document.getElementById('2fa-button');
	button2fa.addEventListener('click', () => {
		getQRCode(getAccessToken())
	});

	sendOTPHandler = document.getElementById('sendOTP');
	sendOTPHandler.addEventListener('click', () => {
		sendOTP(accessToken);
	});

	loginGuest = document.getElementById('login-guest');
	loginGuest.addEventListener('click', () => {
		goToMenu();
	});

	loginOTP = document.getElementById('send-login-OTP');
	otpText = document.getElementById('2fa-login-input');
	loginOTP.addEventListener('click', () => {
		verifyLoginOTP(otpText.value);
	});

	loginIntra = document.getElementById('login-intra');
	loginIntra.addEventListener('click', () => {
		let intraAccessToken = getIntraAccessToken();
		if (intraAccessToken) {
			console.log("Already logged in");
			window.location.reload();
		} else {
			console.log("Not logged in. Redirecting...");
			INTRA_API_URL_AUTH = "https://api.intra.42.fr/oauth/authorize"
			INTRA_CLIENT_ID = "u-s4t2ud-d7f64afc7fb7dc2840609df8b5328f172dd434549cf932c6606762ecb4016c2d"
			INTRA_REDIRECT_URI = "http://127.0.0.1:8000/game"
			INTRA_RESPONSE_TYPE = "code"
			window.location.href = INTRA_API_URL_AUTH + "?client_id=" + INTRA_CLIENT_ID + "&redirect_uri=" + INTRA_REDIRECT_URI + "&response_type=" + INTRA_RESPONSE_TYPE;
		}
	});

	languageSelectLogin = document.getElementById('languageSelectLogin');
	languageSelectLogin.addEventListener('change', () => {
		selectedLanguage = languageSelectLogin.value;
		if (["en", "pt", "fr"].includes(selectedLanguage)) {
			localStorage.setItem("selectedLanguage", selectedLanguage);
			updateLanguage(selectedLanguage);
		}
	})

	languageSelectMenu = document.getElementById('languageSelectMenu');
	languageSelectMenu.addEventListener('change', () => {
		selectedLanguage = languageSelectMenu.value;
		if (["en", "pt", "fr"].includes(selectedLanguage)) {
			localStorage.setItem("selectedLanguage", selectedLanguage);
			updateLanguage(selectedLanguage);
			sendLanguage(accessToken, selectedLanguage);
		}
	})

	updateLanguage(selectedLanguage);

	logoutButton = document.getElementById('logout');
	logoutButton.addEventListener('click', () => {
		localStorage.removeItem("intra_access_token");
		localStorage.removeItem("intra_access_token_expires_at");
		localStorage.removeItem("access_token");
		localStorage.removeItem("access_token_expires_at");
		window.location.reload();
	});
}

document.addEventListener('DOMContentLoaded', setupSinglePageApplication);