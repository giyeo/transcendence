//paddleAx / Bx são declarados no backend e no front, devem ser mudados juntos, (podemos criar alguma lógica para pegar esses valores no handshake ou HTTP GET)
//player = 'A' deve ser um valor que é setado pelo backend e apenas usado por nós (after handshake)
//o sendInputRateMs é um valor que está sendo setado no client, e diz o número de requests que ele faz para o backend em ms, se 16 = 16 por ms
//enviamos o Ay e By, são os valores inicias da posição do paddle

//basicamente todos os valores abaixo podem ser acordados no handshake, para nenhum jogador ter vantagem em cima do outro.
let multiplierWidth = 1;
let multiplierHeight = 1;
let ready = false;
let sendInputRateMs = 12; //16 = 60fps
let player = 'a'
let matchName = "";
let leftShift;
let startCountDown = false;
//É declarado no front-end mesmo, podemos fazer uma lógica para pegar do backend no handshake.
let paddleAy;
let paddleBy;
let paddleSizeA;
let paddleSizeB;
var gameSocket;
var currentWinner;
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

import { matchType, matchSuggestedName, updateMatchType, userData, runGame, randomUserData } from './app.js';
import { getAccessToken } from './util.js';

function setBallmiddle() {
	ball.x = (400 - 10 + leftShift) * multiplierWidth;
	ball.y = (300 + 10) * multiplierHeight;
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
	ballElement.style.width = `${20 * multiplierWidth}px`;
	ballElement.style.height = `${20 * multiplierHeight}px`;
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
	//console.log("received: ", received, "/s");
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
		matchName = data.match;
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
		paddleAy = data.aY * multiplierHeight;
	if (player === 'a')
		paddleBy = data.bY * multiplierHeight;
	//console.log("RECEIBED", paddleAy, paddleBy);
	scoreA = data.scoreA;
	scoreB = data.scoreB;
	if(data.sound != "none")
		playAudio(data.sound);
	if(scoreA > 3 || scoreB > 3) {
		if(scoreA > scoreB)
			currentWinner = 'a';
		else
			currentWinner = 'b';
		scoreA = 0;
		scoreB = 0;
		gameSocket.close();
	} else {
		paddleSizeA = data.paddleSize * multiplierHeight;
		paddleSizeB = data.paddleSize * multiplierHeight;
		oldBall.x = ball.x;
		oldBall.y = ball.y;
		ball.x = (data.ballX * multiplierWidth) + leftShift;
		ball.y = data.ballY * multiplierHeight;
	}
}

async function onCloseWebSocket() {
	let element = document.getElementById('countDown');
	console.log("CLOSE matchType: ", matchType);
	if (matchType === 'simpleMatch') {
		element.innerHTML = `Game Over!\nWinner is ${currentWinner}`;
		console.log("currentWinner simple: ", currentWinner);
	}
	else if (matchType === 'tournamentMatch') {
		element.innerHTML = `Game Over!\nWinner of the first round is ${currentWinner}`;
		console.log("currentWinner first round: ", currentWinner);
	}
	else if (matchType === 'tournamentMatchFinal') {
		element.innerHTML = `Game Over!\nWinner of the tournament is ${currentWinner}`;
		console.log("currentWinner tournament: ", currentWinner);
	}
	element.setAttribute('style', 'display: block;');
	await sleep(120000);
	container.innerHTML = '';
	ballPositionHistory = [];
	gameSocket = null;
	scored = false;
	scoreA = 0;
	scoreB = 0;
	setBallmiddle();
	console.log('WebSocket closed');
	element.innerHTML = "";
	if (currentWinner == player) {	
		if (matchType === 'tournamentMatch') {
			updateMatchType("tournamentMatchFinal");
			await sleep(1000);
			runGame();
		}
	}
}

async function countDown() {
	let countDownElement = document.getElementById('countDown');
	let count = 3;
	while(startCountDown == false) {
		await sleep(100);
	}
	startCountDown = false;
	while(count > 0) {
		countDownElement.innerHTML = `${count}`;
		await sleep(1000);
		count--;
	}
	countDownElement.innerHTML = "GO!";
	await sleep(1000);
	countDownElement.setAttribute('style', 'display: none');
	countDownElement.innerHTML = "";
}

class sendWebSocket {
	static async sendPaddlePosition() {
		//console.log(paddleAy, paddleBy, multiplierHeight);
		let sAy = paddleAy / multiplierHeight;
		let sBy = paddleBy / multiplierHeight;
		//console.log(sBy, sAy)
		if (gameSocket && gameSocket.readyState === WebSocket.OPEN) {
			if(player === 'a') {
				gameSocket.send(JSON.stringify({
					aY: sAy,
					match: matchName,
					player: player
				}));
			}
			if(player === 'b') {
				gameSocket.send(JSON.stringify({
					bY: sBy,
					match: matchName,
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
	document.addEventListener('resize', (e) => { e.preventDefault(); });
}

const API_URL = "http://127.0.0.1:8000"

async function enterQueue() {
	loadingScreen.style.display = 'block';
	return new Promise((resolve, reject) => {
		fetch(API_URL + `/game/enterQueue?matchType=${matchType}&gamemode=${"default"}&matchSuggestedName=${matchSuggestedName}`, {headers: {'Authorization': 'Bearer ' + getAccessToken()}})
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

async function enterQueueRandom() {
	loadingScreen.style.display = 'block';
	return new Promise((resolve, reject) => {
		fetch(API_URL + `/game/enterQueueRandom?username=${randomUserData.login.username}`)
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

export async function startGame() {
	calculateLargest4x3Size();
	if (userData) {
		await enterQueue();
		console.log("User as 42")
	} else if (randomUserData) {
		await enterQueueRandom();
		console.log("User as random")
	}
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
				if(player == 'a' && paddleAy >= 30.0 * multiplierHeight)
					paddleAy -= 10.0 * multiplierHeight; // Move rectangle 1 upward
				if(player == 'b' && paddleBy >= 30.0 * multiplierHeight)
					paddleBy -= 10.0 * multiplierHeight;
			} else if (direction === 'down') {
				if(player == 'a' && paddleAy < 520.0 * multiplierHeight)
					paddleAy += 10.0 * multiplierHeight; // Move rectangle 2 downward
				if(player == 'b' && paddleBy < 520.0 * multiplierHeight)
					paddleBy += 10.0 * multiplierHeight;
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
	leftShift = window.innerWidth / 2 - (400 * multiplierWidth);
	setBallmiddle();
	var elementPositions = [
		{
			top: paddleAy,
			left: leftShift + (35 * multiplierWidth),
			width: (20 * multiplierWidth),
			height: paddleSizeA,
			element: document.getElementById('paddleA')
			
		},
		{
			top: paddleBy,
			left: leftShift + (745 * multiplierWidth),
			width: (20 * multiplierWidth),
			height: paddleSizeB,
			element: document.getElementById('paddleB')
		},
		{
			top: ball.y,
			left: ball.x,
			height: 20 * multiplierHeight,
			width: 20 * multiplierWidth,
			element: document.getElementById('ball')
		},
		{
			top: 0,
			left: leftShift,
			width: 800 * multiplierWidth,
			height: 20 * multiplierHeight,
			element: document.getElementById('horizontalWallLeft')
		},
		{
			top: 620 * multiplierHeight,
			left: leftShift,
			width: 800 * multiplierWidth,
			height: 20 * multiplierHeight,
			element: document.getElementById('horizontalWallRight')
		},
		{
			top: 20 * multiplierHeight,
			left: leftShift + (390 * multiplierWidth),
			width: 20 * multiplierWidth,
			height: 600 * multiplierHeight,
			borderleft: 20 * multiplierWidth,
			element: document.getElementById('verticalWall')
		},
		{
			top: 60 * multiplierHeight,
			left: leftShift + (250 * multiplierWidth),
			fontsize: 100 * multiplierWidth,
			element: document.getElementById('scoreA')
		},
		{
			top: 60 * multiplierHeight,
			left: leftShift + (460 * multiplierWidth),
			fontsize: 100 * multiplierWidth,
			element: document.getElementById('scoreB')
		},
		{
			top: 280 * multiplierHeight,
			left: leftShift + 360 * multiplierWidth,
			element: document.getElementById('countDown')
		},
	]
	for (let elementPosition of elementPositions) {
		if (elementPosition.element.id == 'scoreA' || elementPosition.element.id == 'scoreB') {
			elementPosition.element.style.fontSize = `${elementPosition.fontsize}px`;
		}
		if (elementPosition.element.id == 'verticalWall') {
			elementPosition.element.style.borderLeft = `${elementPosition.borderleft}px dashed #f2f2f2`;
		}
		elementPosition.element.style.top = `${elementPosition.top}px`;
		elementPosition.element.style.left = `${elementPosition.left}px`;
		if (elementPosition.element.id !== 'countDown') {
			elementPosition.element.style.height = `${elementPosition.height}px`;
			elementPosition.element.style.width = `${elementPosition.width}px`;
		}
	}
}

function calculateLargest4x3Size() {
	const targetAspectRatio = 4 / 3;
	const windowWidth = window.innerWidth - 120;
	const windowHeight = window.innerHeight - 120;
	console.log("WINDOWD WIDTH AND HEIGHT: ", windowWidth, windowHeight)
  
	let width = windowWidth;
	let height = windowHeight;
  
	if (width / height > targetAspectRatio) {
	  width = height * targetAspectRatio;
	} else {
	  height = width / targetAspectRatio;
	}
  
	width = Math.floor(width);
	height = Math.floor(height);

	multiplierWidth = width / 800;
	console.log("multiplierWidth: ", multiplierWidth)
	multiplierHeight = height / 600;
	console.log("multiplierHeight: ", multiplierHeight)

	console.log(`Largest 4:3 compatible size: ${width} x ${height}`);
	leftShift = 200 * multiplierWidth;
	paddleSizeA = 100 * multiplierHeight;
	paddleSizeB = 100 * multiplierHeight;
	paddleAy = (20.0 + 300.0 - 50.0) * multiplierHeight;
	paddleBy = (20.0 + 300.0 - 50.0) * multiplierHeight;
}

function movePaddleClient() {
	if(player == 'a')
		document.getElementById('paddleA').style.top = `${paddleAy}px`;
	if(player == 'b')
		document.getElementById('paddleB').style.top = `${paddleBy}px`;
}

async function drawGame(ballX, ballY) {
	var elementPositions = [
		{
			top: ballY,
			left: ballX,
			width: 20 * multiplierWidth,
			height: 20 * multiplierHeight,
			element: document.getElementById('ball'),
			player: 'none'
		},
		{
			top: paddleAy,
			left: leftShift + (35 * multiplierWidth),
			height: paddleSizeA,
			element: document.getElementById('paddleA'),
			player: 'a'
		},
		{
			top: paddleBy,
			left: leftShift + (745 * multiplierWidth),
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