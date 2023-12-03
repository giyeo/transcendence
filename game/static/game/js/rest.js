import { userData, updateUserData, updateRandomUserData, logout } from './app.js'

console.log("API_URL: " + API_URL)

export async function getUserData(intraCode, intraAccessToken) {
	try {
		console.log("This is data before the request: " + data)
		console.log("URL NOW:", API_URL + "/game/data" + "?code=" + intraCode + "&intra_access_token=" + intraAccessToken)
		var data = await request("GET", API_URL + "/game/data" + "?code=" + intraCode + "&intra_access_token=" + intraAccessToken, {});
		console.log("This is data after the request: " + data)
		if (data.intra_access_token) {
			localStorage.setItem("intra_access_token", data.intra_access_token);
		}
		if (data.access_token) {
			localStorage.setItem("access_token", data.access_token);
		}
		delete data.intra_access_token;
		delete data.access_token;
		updateUserData(data);
	} catch (error) {
		console.error('Error:', error);
	}
};

export async function getRandomUserData() {
	try {
		var data = await request("GET", "https://randomuser.me/api/", {});
		console.log(data);
		updateRandomUserData(data.results[0]);
	} catch (error) {
		console.error('Error:', error);
	}
}

export async function getQRCode(accessToken) {
	let imageQRCode2FA = document.getElementById('2FAImageQRCode');
	let ImageInputAndButton2FA = document.getElementById('2FAImageInputAndButton');
	if (ImageInputAndButton2FA.style.display === "block") {
		ImageInputAndButton2FA.style.display = "none";
		imageQRCode2FA.src = "";
		return;
	} else {
		try {
			var status2fa = await request("GET", API_URL + '/game/2FAStatus', {'Authorization': 'Bearer ' + accessToken});
			let status2FAElement = document.getElementById('2FAStatus');
			status2FAElement.innerHTML = status2fa.twofa_enabled ? "ACTIVATED" : "DEACTIVATED";
		} catch (error) {
			console.error('Error:', error);
		}
		try {
			var data = await request("GET", API_URL + '/game/qrcode', {'Authorization': 'Bearer ' + accessToken}, "blob");
			imageQRCode2FA.src = URL.createObjectURL(data);
			ImageInputAndButton2FA.style.display = "block";
		} catch (error) {
			console.error('Error:', error);
		}
	}
}

export async function verifyOTP(otp, accessToken) {
	console.log("VERIFYING OTP");
	try {
		var data = await request("GET", API_URL + '/game/verifyOTP?&otp=' + otp, {'Authorization': 'Bearer ' + accessToken});
		console.log("OTP VERIFIED");
		return data;
	} catch (error) {
		console.log("OTP NOT VERIFIED");
		return false;
	}
}

export async function sendLanguage(accessToken, selectedLanguage) {
	try {
		var data = await request("PATCH", API_URL + '/game/updateLanguage' + '?lang=' + selectedLanguage, {'Authorization': 'Bearer ' + accessToken});
	} catch (error) {
		console.error('Error:', error);
	}
}

export async function verifyLoginOTP(otp) {
	try {
		var data = await request("GET", API_URL + '/game/verifyLoginOTP?&otp=' + otp + '&userId=' + userData.user_id, {});
		if (data.access_token) {
			localStorage.setItem("access_token", data.access_token)
			localStorage.setItem("access_token_expires_at", data.access_token_expires_at)
			return data.access_token;
		} else {
			return "";
		}
	} catch (error) {
		console.log("THIS ERROR:", error);
		console.error('Error:', error);
	}
}


async function request(method, url, headers, blob) {
	console.log("DOING REQUEST", method, url);

	if(url === "")
		throw new Error("missing URL");

	if (typeof headers === 'undefined')
		headers = {};

	var availableMethods = ["GET", "POST", "PUT", "PATCH", "DELETE"];
	if(availableMethods.indexOf(method) === -1) {
		throw new Error("Method not available");
	}

	return new Promise((resolve, reject) => {
		fetch(url, { method: method, headers: headers })
			.then(response => {
				if (response.status === 401) {
					logout();
				} else if (response.ok) {
					if(blob) {
						resolve(response.blob())
					}
					else {
						resolve(response.json());
					}
				} else {
					console.log("Error:", response.status);
				}
				reject(response.status);
			})
			.catch(error => {
				console.error('There was a problem with the fetch operation:', error);
				reject(error);
			});
	});
}