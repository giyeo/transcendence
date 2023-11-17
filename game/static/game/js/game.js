//paddleAx / Bx são declarados no backend e no front, devem ser mudados juntos, (podemos criar alguma lógica para pegar esses valores no handshake ou HTTP GET)
//player = 'A' deve ser um valor que é setado pelo backend e apenas usado por nós (after handshake)
//o sendInputRateMs é um valor que está sendo setado no client, e diz o número de requests que ele faz para o backend em ms, se 16 = 16 por ms
//enviamos o Ay e By, são os valores inicias da posição do paddle

//basicamente todos os valores abaixo podem ser acordados no handshake, para nenhum jogador ter vantagem em cima do outro.
let ready = false;
let sendInputRateMs = 12; //16 = 60fps
let player = 'a'
let match = "none";
let leftShift = 200;
let paddleAx = leftShift + 35;
let paddleBx = leftShift + 745;
let startCountDown = false;
//É declarado no front-end mesmo, podemos fazer uma lógica para pegar do backend no handshake.
let paddleAy = 20 + 300 - 50;
let paddleBy = 20 + 300 - 50;
let paddleSizeA = 100;
let paddleSizeB = 100;
var gameSocket;
//Apenas seguram valores e setam inicialmente
let scored = false;
let scoreA = 0;
let scoreB = 0;
var oldBall = {
	x: 0,
	y: 0,
};
var ball = {
	x: 0,
	y: 0,
};

function setBallmiddle() {
	ball.x = 400 - 10 + leftShift;
	ball.y = 300 + 10;
}

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

var received = 0;
setInterval(function() {
	console.log("received: ", received, "/s");
	received = 0;
}, 1000);

async function onMessageWebSocket(e) {
	let data = JSON.parse(e.data)
	if (data.type === 'close') {
		//another player has disconnect you won
		gameSocket.close();
	}
	if (data.type === 'handshake') {
		player = data.player;
		match = data.match;
	}
	if (data.type === 'gameState') {
		received++;
		handleGameState(data.data);
	}
	if (data.type === 'countDown') {
		loadingScreen.style.display = 'none';
		startCountDown = true;
	}
}

async function handleGameState(data) {
	if (player === 'b')
		paddleAy = data.aY;
	if (player === 'a')
		paddleBy = data.bY;
	scoreA = data.scoreA;
	scoreB = data.scoreB;
	if(data.sound != "none")
		playAudio(data.sound);
	if(scoreA > 3 || scoreB > 3) {
		scoreA = 0;
		scoreB = 0;
		gameSocket.close();
	}
	paddleSizeA = data.paddleSize;
	paddleSizeB = data.paddleSize;
	oldBall.x = ball.x;
	oldBall.y = ball.y;
	ball.x = data.ballX + leftShift;
	ball.y = data.ballY;
}

async function onCloseWebSocket() {
	let element = document.getElementById('countDown');
	element.setAttribute('style', 'display: block; left: 0px; top: 280px');
	element.innerHTML = `Game Over!`;
	await sleep(1000);
	element.setAttribute('style', 'display: block; left: 360px; top: 280px');
	container.innerHTML = '';
	ballPositionHistory = [];
	gameSocket = null;
	scored = false;
	setBallmiddle();
	console.log('WebSocket closed');
}

async function countDown() {
	while(startCountDown == false) {
		await sleep(100);
	}
	startCountDown = false;
	let element = document.getElementById('countDown');
	let count = 3;
	while(count > 0) {
		element.innerHTML = `${count}`;
		await sleep(1000);
		count--;
	}
	element.innerHTML = `GO!`;
	element.setAttribute('style', 'left: 290px; top: 280px');
	await sleep(1000);
	element.setAttribute('style', 'display: none');
}

class sendWebSocket {
	static async sendPaddlePosition() {
		if (gameSocket && gameSocket.readyState === WebSocket.OPEN) {
			if(player === 'a') {
				gameSocket.send(JSON.stringify({
					aY: paddleAy,
					match: match,
					player: player
				}));
			}
			if(player === 'b') {
				gameSocket.send(JSON.stringify({
					bY: paddleBy,
					match: match,
					player: player
				}));
			}
		}
	}
}

async function smoothMoveBall() {
	// drawGame(ball.x, ball.y);
	// addPosition(ball.x, ball.y);
	// await sleep(12);
	const diffX = ball.x - oldBall.x;
	const diffY = ball.y - oldBall.y;
	var steps = 2; // 2, 3, 4, 6, 12
	for (let i = 1; i <= steps; i++) {
	  const t = i / steps;
	  const currentX = oldBall.x + diffX * t;
	  const currentY = oldBall.y + diffY * t;
	  drawGame(currentX, currentY);
	  if (i === steps) {
		addPosition(ball.x, ball.y);
	  }
	  await sleep(12 / steps);
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
		await smoothMoveBall();
	}
}

function fabs(x) {
	if(x < 0)
		return -x;
	return x;
}

function startWebSockets() {
	let url = `ws://${window.location.host}/ws/socket-server/`;
	gameSocket = new WebSocket(url);
}

function startEventListeners() {
	gameSocket.addEventListener('open', onOpenWebSocket);
	gameSocket.addEventListener('message', onMessageWebSocket);
	gameSocket.addEventListener('close', onCloseWebSocket);
	document.addEventListener('keydown', handleKeyDown);
	document.addEventListener('keyup', handleKeyUp);
	// document.addEventListener('resize', startGame);
}

const API_URL = "http://127.0.0.1:8000"

async function enterQueue(userData) {
	loadingScreen.style.display = 'block';
	return new Promise((resolve, reject) => {
		fetch(API_URL + `/game/enterQueue?matchType=${"1v1"}&gamemode=${"default"}`, {headers: {'Authorization': 'Bearer ' + userData.access_token}})
			.then(response => {
				console.log(response)
				resolve(response)
			})
			.catch(error => {
				console.error('There was a problem with the fetch operation:', error);
				resolve(error);
			});
	})
}

export async function startGame(userData) {
	await enterQueue(userData);
	startWebSockets();
	startEventListeners();
	setupGame();
	await countDown();
	await gameLoop();
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
			if (direction === 'up') {
				if(player == 'a' && paddleAy >= 30)
					paddleAy -= 10; // Move rectangle 1 upward
				if(player == 'b' && paddleBy >= 30)
					paddleBy -= 10;
			} else if (direction === 'down') {
				if(player == 'a' && paddleAy < 520)
					paddleAy += 10; // Move rectangle 2 downward
				if(player == 'b' && paddleBy < 520)
					paddleBy += 10;
			}
			
			movePaddleClient();
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
	leftShift = window.innerWidth / 2 - 400;
	setBallmiddle();
	var elementPositions = [
		{
			top: paddleAy,
			left: leftShift + 35,
			width: 20,
			height: paddleSizeA,
			element: document.getElementById('paddleA')
			
		},
		{
			top: paddleBy,
			left: leftShift + 745,
			width: 20,
			height: paddleSizeB,
			element: document.getElementById('paddleB')
		},
		{
			top: ball.y,
			left: ball.x,
			width: 20,
			height: 20,
			element: document.getElementById('ball')
		},
		{
			top: 0,
			left: leftShift,
			width: 800,
			height: 20,
			element: document.getElementById('horizontalWallLeft')
		},
		{
			top: 310,
			left: leftShift,
			width: 800,
			height: 20,
			element: document.getElementById('horizontalWallMid')
		},
		{
			top: 620,
			left: leftShift,
			width: 800,
			height: 20,
			element: document.getElementById('horizontalWallRight')
		},
		{
			top: 20,
			left: leftShift + 390,
			width: 20,
			height: 600,
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
		if (elementPosition.element !== 'scoreA'
		 && elementPosition.element !== 'scoreB'
		 && elementPosition.element !== 'countDown') {
			elementPosition.element.style.height = `${elementPosition.height}px`;
			elementPosition.element.style.width = `${elementPosition.width}px`;
		}
	}
}

function movePaddleClient() {
	if(player == 'a')
		document.getElementById('paddleA').style.top = `${paddleAy}px`;
	if(player == 'b')
		document.getElementById('paddleB').style.top = `${paddleBy}px`;
}

async function drawGame(ballX, ballY) {
	leftShift = window.innerWidth / 2 - 400;
	var elementPositions = [
		{
			top: ballY,
			left: ballX,
			height: 20,
			element: document.getElementById('ball'),
			player: 'none'
		},
		{
			top: paddleAy,
			left: leftShift + 35,
			height: paddleSizeA,
			element: document.getElementById('paddleA'),
			player: 'a'
		},
		{
			top: paddleBy,
			left: leftShift + 745,
			height: paddleSizeB,
			element: document.getElementById('paddleB'),
			player: 'b'
		}]
	for (let elementPosition of elementPositions) {
		if(elementPosition.player == player) {
			elementPosition.element.style.height = `${elementPosition.height}px`;
			continue;
		}
		elementPosition.element.style.top = `${elementPosition.top}px`;
		elementPosition.element.style.left = `${elementPosition.left}px`;
		elementPosition.element.style.height = `${elementPosition.height}px`;
	}
	let element = document.getElementById('scoreA');
	element.innerHTML = `${scoreA}`;
	element = document.getElementById('scoreB');
	element.innerHTML = `${scoreB}`;
}

class updateElement {
	static async topLeft(element, top, left) {
		document.getElementById(element).style.top = `${top}px`;
		document.getElementById(element).style.left = `${left}px`;
	}
	static async topLeftWidthHeight(element, top, left, width, height) {
		document.getElementById(element).style.top = `${top}px`;
		document.getElementById(element).style.left = `${left}px`;
		document.getElementById(element).style.width = `${width}px`;
		document.getElementById(element).style.height = `${height}px`;
	}
	static async top(element, top) {
		document.getElementById(element).style.top = `${top}px`;
	}
	static async left(element, left) {
		document.getElementById(element).style.left = `${left}px`;
	}
	static async width(element, width) {
		document.getElementById(element).style.width = `${width}px`;
	}
	static async height(element, height) {
		document.getElementById(element).style.height = `${height}px`;
	}
}

export default startGame;
export {gameSocket}