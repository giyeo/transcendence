//paddleAx / Bx são declarados no backend e no front, devem ser mudados juntos, (podemos criar alguma lógica para pegar esses valores no handshake ou HTTP GET)
//player = 'A' deve ser um valor que é setado pelo backend e apenas usado por nós (after handshake)
//o framerate é um valor que está sendo setado no client, e diz o número de requests que ele faz para o backend em ms, se 16 = 16 por ms
//enviamos o Ay e By, são os valores inicias da posição do paddle

//basicamente todos os valores abaixo podem ser acordados no handshake, para nenhum jogador ter vantagem em cima do outro.
let ready = false;
let framerate = 12; //16 = 60fps
let player = 'a'
let match = "none";
let leftShift = 400;
let paddleAx = leftShift + 35;
let paddleBx = leftShift + 745;

//É declarado no front-end mesmo, podemos fazer uma lógica para pegar do backend no handshake.
let paddleAy = 20 + 300 - 50;
let paddleBy = 20 + 300 - 50;

//Apenas seguram valores e setam inicialmente
let scored = false;
let scoreA = 0;
let scoreB = 0;
var ball = {
	x: 0,
	y: 0,
	radians: 0,
	velocity: 0
};

//____________________________UTILS_BEGIN____________________________
function playAudio(name) {
	const audio = document.getElementById(name);
	if(name == "score")
		scored = true;
	audio.volume = 0.1;
	audio.play();
  }

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

//________________________INTERPOLATION_BEGIN____________________________
//adding frames N between old and new positions
async function goToPosition(newX, newY) {
	var oldX = ball.x;
	var oldY = ball.y;
	var DLSS = 4;
	var i = 0
	if (Math.abs(newX - oldX) < 300 ) {
		while(i < DLSS) {
			ball.x += ((newX - oldX) / DLSS);
			ball.y += ((newY - oldY) / DLSS);
			await sleep(framerate / DLSS);
			i++;
		}
	}
	ball.x = newX;
	ball.y = newY;
}

//____________________________TAIL_BEGIN____________________________
var ballPositionHistory = [];
const container = document.getElementById('tail');

function addPosition(x, y) {
	// Add the new position to the list
	ballPositionHistory.push({ x, y });

	// If the list exceeds the maximum length, remove the oldest element and its corresponding child element
	if (ballPositionHistory.length > 25) {
		const removedItem = ballPositionHistory.shift();
		const removedChild = container.querySelector(`[data-x="${removedItem.x}"][data-y="${removedItem.y}"]`);
		container.removeChild(removedChild);
	}

	// Create a new <div> element for the new position
	const ballElement = document.createElement('div');
	ballElement.className = 'ball';
	ballElement.style.top = `${y}px`;
	ballElement.style.left = `${x}px`;
	ballElement.style.opacity = '0.1';

	// Set custom attributes to identify this element
	ballElement.setAttribute('data-x', x);
	ballElement.setAttribute('data-y', y);

	// Append the new <div> element to the container
	container.appendChild(ballElement);
}

const loadingScreen = document.getElementById('loadingScreen');

function onOpenWebSocket(e) {
	console.log('WebSocket connected');
}

function onMessageWebSocket(e) {
	let data = JSON.parse(e.data)

	if (data.player) {
		player = data.player;
		match = data.match;
		return ;
	}
	loadingScreen.style.display = 'none';
	if (player === 'b')
		paddleAy = data.data.aY; //dont receive myself, only if i'm player B
	else
		paddleBy = data.data.bY;
	//ball.x = data.data.ballX;
	//ball.y = data.data.ballY;
	goToPosition(data.data.ballX, data.data.ballY)
	ball.radians = data.data.ballRad;
	ball.velocity = data.data.ballVelocity;
	scoreA = data.data.scoreA;
	scoreB = data.data.scoreB;
	if(data.data.sound != "none")
		playAudio(data.data.sound);
	if(scoreA > 111 || scoreB > 111) {
			scoreA = 0;
			scoreB = 0;
			gameSocket.close();
	}
	drawGame();
	addPosition(ball.x, ball.y);
}

async function onCloseWebSocket() {
	let element = document.getElementById('countDown');
	element.setAttribute('style', 'display: block; left: 320px; top: 280px');
	element.innerHTML = `Game Over!`;
	await sleep(1000);
	document.getElementById("menu").style.display = "block";
	document.getElementById("game").style.display = "none";
	element.setAttribute('style', 'display: block; left: 760px; top: 280px');
	container.innerHTML = '';
	ballPositionHistory = [];
	gameSocket = null;
	scored = false;
	console.log('WebSocket closed');
}

async function countDown() {
	sendWebSocket.sendPaddlePosition();
	let element = document.getElementById('countDown');
	let count = 3;
	while(count > 0) {
		element.innerHTML = `${count}`;
		await sleep(1000);
		count--;
	}
	element.innerHTML = `GO!`;
	element.setAttribute('style', 'left: 690px; top: 280px');
	await sleep(1000);
	element.setAttribute('style', 'display: none');
}

class sendWebSocket {
	static sendPaddlePosition() {
		if (gameSocket && gameSocket.readyState === WebSocket.OPEN) {
			if(player === 'a') {
				gameSocket.send(JSON.stringify({
					type: "paddlePosition",
					aY: paddleAy,
					match: match
				}));
				console.log("a");
			}
			if(player === 'b') {
				gameSocket.send(JSON.stringify({
					type: "paddlePosition",
					bY: paddleBy,
					match: match
				}));
				console.log("b");
			}
		}
	}
}

async function gameLoop() {
	ready = true;
	while(1) {
		if(!gameSocket)
			return ;
		if (gameSocket.readyState !== WebSocket.OPEN) {
			await sleep(100);
			continue;
		}
		if(scored == true) {
			scored = false;
			removeEventListener('keydown', handleKeyDown);
			await sleep(1000);
			ready = true;
		}
		sendWebSocket.sendPaddlePosition();
		await sleep(framerate);
	}
}

let gameSocket;

function startWebSockets() {
	let url = `ws://${window.location.host}/ws/socket-server/`
	gameSocket = new WebSocket(url);
	console.log("gameSocket: ", gameSocket);
	// Show the loadingScreen while waiting for the WebSocket to open
	if (gameSocket.readyState !== WebSocket.OPEN) {
		loadingScreen.style.display = 'block';
	}
}

function startEventListeners() {
	gameSocket.addEventListener('open', onOpenWebSocket);
	gameSocket.addEventListener('message', onMessageWebSocket);
	gameSocket.addEventListener('close', onCloseWebSocket);
	document.addEventListener('keydown', handleKeyDown);
	document.addEventListener('keyup', handleKeyUp);
}

async function startGame() {
	startWebSockets();
	startEventListeners();
	setupGame();
	await countDown();
	gameLoop();
}

//____________________________INPUT_BEGIN____________________________
let keyDownInterval = null;
let isKeyDown = false; // Flag to track key press
// Attach keydown and keyup event listeners to the document


function stopContinuousMove() {
	clearInterval(keyDownInterval);
	isKeyDown = false; // Reset the flag
}

function handleKeyUp(event) {
	if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
		stopContinuousMove();
	}
}

function startContinuousMove(direction) {
	if (!isKeyDown) {
		isKeyDown = true;
		keyDownInterval = setInterval(() => {
			if (direction === 'up' && paddleAy >= 30) {
				if(player == 'a')
					paddleAy -= 10; // Move rectangle 1 upward
				else
					paddleBy -= 10;
			} else if (direction === 'down' && paddleAy < 520) {
				if(player == 'a')
					paddleAy += 10; // Move rectangle 2 downward
				else
					paddleBy += 10;
			}
		}, 16); // Adjust the interval as needed for desired speed
	}
}

// Handle keydown and keyup events
function handleKeyDown(event) {
	if(ready == false)
		return;
	if (event.key === 'ArrowUp') {
		startContinuousMove('up');
	} else if (event.key === 'ArrowDown') {
		startContinuousMove('down');
	}
}

function setupGame() {
	let elementPositions = [
		{
			top: paddleAy,
			left: paddleAx,
			element: document.getElementById('paddleA')
		},
		{
			top: paddleBy,
			left: paddleBx,
			element: document.getElementById('paddleB')
		},
		{
			top: ball.y,
			left: ball.x,
			element: document.getElementById('ball')
		},
		{
			top: 0,
			left: leftShift,
			element: document.getElementById('horizontalWallLeft')
		},
		{
			top: 310,
			left: leftShift,
			element: document.getElementById('horizontalWallMid')
		},
		{
			top: 620,
			left: leftShift,
			element: document.getElementById('horizontalWallRight')
		},
		{
			top: 20,
			left: leftShift + 390,
			element: document.getElementById('verticalWall')
		},
		{
			top: 60,
			left: leftShift + 250,
			element: document.getElementById('scoreA')
		},
		{
			top: 60,
			left: leftShift + 460,
			element: document.getElementById('scoreB')
		},
		{
			top: 280,
			left: leftShift + 360,
			element: document.getElementById('countDown')
		}
	]
	for (let elementPosition of elementPositions) {
		elementPosition.element.style.top = `${elementPosition.top}px`;
		elementPosition.element.style.left = `${elementPosition.left}px`;
	}
}

function drawGame() {
	elementPositions = [
		{
			top: paddleAy,
			left: paddleAx,
			element: document.getElementById('paddleA')
		},
		{
			top: paddleBy,
			left: paddleBx,
			element: document.getElementById('paddleB')
		},
		{
			top: ball.y,
			left: ball.x,
			element: document.getElementById('ball')
		},
	]
	for (let elementPosition of elementPositions) {
		elementPosition.element.style.top = `${elementPosition.top}px`;
		elementPosition.element.style.left = `${elementPosition.left}px`;
	}
	let element = document.getElementById('scoreA');
	element.innerHTML = `${scoreA}`;
	element = document.getElementById('scoreB');
	element.innerHTML = `${scoreB}`;
}
