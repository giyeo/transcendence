async function getUserData(intraCode, intraAccessToken) {
	try {
		const data = await request("GET", API_URL + "/game/data" + "?code=" + intraCode + "&intra_access_token=" + intraAccessToken, {});
		console.log(data);
		if (data.intra_access_token) {
			localStorage.setItem("intra_access_token", data.intra_access_token);
			localStorage.setItem("intra_access_token_expires_at", data.intra_access_token_expires_at);
		}
		if (data.access_token) {
			localStorage.setItem("access_token", data.access_token);
			localStorage.setItem("access_token_expires_at", data.access_token_expires_at);
		}
		userData = data;
	} catch (error) {
		console.error('Error:', error);
	}
};

async function getRandomUserData() {
	try {
		const data = await request("GET", "https://randomuser.me/api/", {});
		console.log(data);
		randomUserData = data.results[0]
	} catch (error) {
		console.error('Error:', error);
	}
}

async function getQRCode(accessToken) {
	try {
		const data = await request("GET", API_URL + '/game/qrcode', {'Authorization': 'Bearer ' + accessToken}, "blob");
		console.log(data);
		qrcodeImage = document.getElementById('2fa-button-qrcode');
		qrcodeImage.src = URL.createObjectURL(data);
		qrcodeImage.style.display = "block";
	} catch (error) {
		console.error('Error:', error);
	}
}

async function verifyOTP(otp, accessToken) {
	try {
		await request("GET", API_URL + '/game/verifyOTP?&otp=' + otp, {'Authorization': 'Bearer ' + accessToken});
		return 200;
	} catch (error) {
		console.error('Error:', error);
		return 500;
	}
}

async function sendLanguage(accessToken, selectedLanguage) {
	try {
		const data = await request("PATCH", API_URL + '/game/updateLanguage' + '?lang=' + selectedLanguage, {'Authorization': 'Bearer ' + accessToken});
	} catch (error) {
		console.error('Error:', error);
	}
}

async function verifyLoginOTP(otp) {
	try {
		const data = await request("GET", API_URL + '/game/verifyLoginOTP?&otp=' + otp + '&userId=' + userData.user_id, {});
		if (data.access_token) {
			localStorage.setItem("access_token", data.access_token)
			localStorage.setItem("access_token_expires_at", data.access_token_expires_at)
			mountMenu();
			window.location.hash = 'menu'
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

	return new Promise((resolve, reject) => {
		fetch(url, { method: method, headers: headers })
			.then(response => {
				if(response.ok){
					if(blob)
						resolve(response.blob())
					else //tem que ter esse else pq é async
						resolve(response.json());
				}
			})
			.catch(error => {
				console.error('There was a problem with the fetch operation:', error);
				reject(error);
			});
	});
}