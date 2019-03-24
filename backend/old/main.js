socket = io.connect('http://127.0.0.1:4000');

function get_parkings(){
	socket.emit('get_parkings');
}

function reserve_parking(parking_id, _type){
	socket.emit('reserve_parking', parking_id, _type);
}

socket.on('all_parkings', function(data){
	console.log(data);
})

socket.on('update_parking', function(data){
	console.log(data)
});

socket.on('hello', function(){
	console.log('Hello world');
});
