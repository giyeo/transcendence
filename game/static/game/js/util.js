export function removeQueryParam(key) {
	// Get the current URL
	var url = new URL(window.location.href);
	// Get the URLSearchParams object from the URL
	var params = new URLSearchParams(url.search);
	// Remove the specified query parameter
	params.delete(key);
	// Update the URL with the modified query parameters
	url.search = params.toString();
	// Replace the current entry in the browser's history with the updated URL
	window.history.replaceState({}, document.title, url.href);
}

export function getIntraCode() {
	let urlParams = new URLSearchParams(window.location.search);
	if (urlParams.has('code')) {
		return urlParams.get('code');
	}
	return "";
}

export function getIntraAccessToken() {
	let intraAccessToken = localStorage.getItem("intra_access_token")
	if (intraAccessToken) {
		return intraAccessToken;
	} else {
		return "";
	}
}

export function getAccessToken() {
	let accessToken = localStorage.getItem("access_token")
	if (accessToken) {
		return accessToken;
	} else {
		return "";
	}
}