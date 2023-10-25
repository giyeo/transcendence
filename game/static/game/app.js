//paddleAx / Bx são declarados no backend e no front, devem ser mudados juntos, (podemos criar alguma lógica para pegar esses valores no handshake ou HTTP GET)
//player = 'A' deve ser um valor que é setado pelo backend e apenas usado por nós (after handshake)
//o framerate é um valor que está sendo setado no client, e diz o número de requests que ele faz para o backend em ms, se 16 = 16 por ms
//enviamos o Ay e By, são os valores inicias da posição do paddle

//basicamente todos os valores abaixo podem ser acordados no handshake, para nenhum jogador ter vantagem em cima do outro.
let ready = false;
let framerate = 12; //16 = 60fps
let player = 'A'
let leftShift = 400;
let paddleAx = leftShift + 35;
let paddleBx = leftShift + 745;

//É declarado no front-end mesmo, podemos fazer uma lógica para pegar do backend no handshake.
let paddleAy = 20 + 300 - 50;
let paddleBy = 20 + 300 - 50;

//Apenas seguram valores e setam inicialmente
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
	if(Math.abs(newX-oldX) < 300 ) {
		while(i < DLSS) {
			ball.x += ((newX - oldX) / DLSS );
			ball.y += ((newY - oldY) / DLSS );
			await sleep(framerate / DLSS );
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
//____________________________SOCKET_BEGIN____________________________

let url = `ws://${window.location.host}/ws/socket-server/`

const startButton = document.getElementById('start-button');
let gameSocket;

startButton.addEventListener('click', () => {
    if (!gameSocket) {
		startGame();
    }
});

function startGame() {
	const overlay = document.getElementById('overlay');
	gameSocket = new WebSocket(url);
	// Show the overlay while waiting for the WebSocket to open
	if (gameSocket.readyState !== WebSocket.OPEN) {
		overlay.style.display = 'block';
	}

	gameSocket.onopen = function(e) {
		overlay.style.display = 'none';
		console.log('WebSocket connected');
		countDown();
	}
	
	gameSocket.onmessage = function(e){
		let data = JSON.parse(e.data)
		if(player === 'B')
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
		if(scoreA > 10 || scoreB > 10) {
				scoreA = 0;
				scoreB = 0;
		}
		updateElementPosition();
		addPosition(ball.x, ball.y);
	}
	
	const game = () => {
		if (gameSocket.readyState === WebSocket.OPEN) {
			gameSocket.send(JSON.stringify({
				aY: paddleAy,
				bY: paddleBy,
			}))
		}
	};
	
	//__________________________GAMELOOP_BEGIN____________________________
	async function countDown() {
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
		gameloop();
	}

	async function gameloop() {
		ready = true;
		while(1) {
			game()
			await sleep(framerate);
		}
	}
}

//____________________________INPUT_BEGIN____________________________
let keyDownInterval = null;
let isKeyDown = false; // Flag to track key press
function startContinuousMove(direction) {
	if (!isKeyDown) {
		isKeyDown = true;
		keyDownInterval = setInterval(() => {
			if (direction === 'up' && paddleAy >= 30) {
				paddleAy -= 10; // Move rectangle 1 upward
				// paddleBy -= 10;
			} else if (direction === 'down' && paddleAy < 520) {
				paddleAy += 10; // Move rectangle 2 downward
				// paddleBy += 10;
			}
		}, 16); // Adjust the interval as needed for desired speed
	}
}

function stopContinuousMove() {
	clearInterval(keyDownInterval);
	isKeyDown = false; // Reset the flag
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

function handleKeyUp(event) {
	if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
		stopContinuousMove();
	}
}
// Attach keydown and keyup event listeners to the document
document.addEventListener('keydown', handleKeyDown);
document.addEventListener('keyup', handleKeyUp);

//____________________________UPDATE_CSS_BEGIN____________________________
document.addEventListener('DOMContentLoaded', function() {
	initialUpdateElementPosition();
});

function clientUpdateElementPosition() {
	if(player == 'A') {
		let element = document.getElementById('paddleA');
		element.style.top = `${paddleAy}px`;
		element.style.left = `${paddleAx}px`;
	}
	else {
		element = document.getElementById('paddleB');
		element.style.top = `${paddleBy}px`;
		element.style.left = `${paddleBx}px`;
	}
}

function initialUpdateElementPosition() {
	let element = document.getElementById('paddleA');
	element.style.top = `${paddleAy}px`;
	element.style.left = `${paddleAx}px`;
	element = document.getElementById('paddleB');
	element.style.top = `${paddleBy}px`;
	element.style.left = `${paddleBx}px`;
	element = document.getElementById('ball');
	element.style.top = `${ball.y}px`;
	element.style.left = `${ball.x}px`;
	element = document.getElementById('horizontalWallLeft');
	element.style.top = `${0}px`;
	element.style.left = `${leftShift}px`;
	element = document.getElementById('horizontalWallMid');
	element.style.top = `${310}px`;
	element.style.left = `${leftShift}px`;
	element.style.backgroundColor = "rgba(200,200,200,0.2)";
	element = document.getElementById('horizontalWallRight');
	element.style.top = `${620}px`;
	element.style.left = `${leftShift}px`;
	element = document.getElementById('verticalWall');
	element.style.top = `${20}px`;
	element.style.left = `${leftShift + 390}px`;
	element = document.getElementById('scoreA');
	element.style.top = `${60}px`;
	element.style.left = `${leftShift + 250}px`;
	element = document.getElementById('scoreB');
	element.style.top = `${60}px`;
	element.style.left = `${leftShift + 460}px`;
	element = document.getElementById('countDown');
	element.style.top = `${280}px`;
	element.style.left = `${leftShift + 360}px`;
}

function updateElementPosition() {
	let element = document.getElementById('paddleA');
	element.style.top = `${paddleAy}px`;
	element = document.getElementById('paddleB');
	element.style.top = `${paddleBy}px`;
	element = document.getElementById('ball');
	element.style.top = `${ball.y}px`;
	element.style.left = `${ball.x}px`;
	element = document.getElementById('scoreA');
	element.innerHTML = `${scoreA}`;
	element = document.getElementById('scoreB');
	element.innerHTML = `${scoreB}`;
}
