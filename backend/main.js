socket = io.connect('http://127.0.0.1:4000');

function register(email, pwd, first_name, last_name, licence_plate){
	socket.emit('register', email, pwd, first_name, last_name, licence_plate);
}

function log_in(email, pwd){
	socket.emit('authentificate', email, pwd);
}

function get_parkings(){
	socket.emit('get_parkings');
}

function reserve_parking(parking_id, _type){
	socket.emit('reserve_parking', parking_id, _type);
}

socket.on('signed_up', function(data){
	console.log(data);
});

socket.on('logged_on', function(data){
	console.log(data);
});

socket.on('all_parkings', function(data){
	console.log(data);
})

socket.on('update_parking', function(data){
	console.log(data);
});

