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
			var data = await request("GET", API_URL + '/game/qrcode', {'Authorization': 'Bearer ' + accessToken}, "blob");
		} catch (error) {
			console.error('Error:', error);
		}
		imageQRCode2FA.src = URL.createObjectURL(data);
		ImageInputAndButton2FA.style.display = "block";
	}
}

export async function verifyOTP(otp, accessToken) {
	try {
		await request("GET", API_URL + '/game/verifyOTP?&otp=' + otp, {'Authorization': 'Bearer ' + accessToken});
		return 200;
	} catch (error) {
		console.error('Error:', error);
		return 500;
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
		}
	} catch (error) {
		console.error('Error:', error);
	}
}


async function request(method, url, headers, blob) {
	console.log(method, url);

	if(url === "")
		throw new Error("missing URL");

	if (typeof headers === 'undefined')
		headers = {};

	var availableMethods = ["GET", "POST", "PUT", "PATCH", "DELETE"];
	if(availableMethods.indexOf(method) === -1) {
		throw new Error("Method not available");
	}

	console.log("fucking url", url)

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
					console.log("FUCKING URL2", url)
					console.log("Error:", response.status);
				}
			})
			.catch(error => {
				console.log("FUCKING URL2", url)
				console.error('There was a problem with the fetch operation:', error);
				reject(error);
			});
	});
}