var i2c     = require('i2c');
var address = 0x18;

// https://www.npmjs.com/package/i2c
// npm install i2c

var wire = new i2c(address, {device: '/dev/i2c-0'}); // point to your i2c address, debug provides REPL interface


wire.scan(function(err, data) {
	  console.log( data )      ;
	 })                        ;
wire.setAddress(32)                ;
// Put it in reading mode
wire.writeByte( 0x00, function(err) {    });
wire.readByte(function(err, res) { console.log( " result is single byte", res ) })

// wire.read( 1,function(err, res) { 
// result is single byte 
//  console.log( res )       ;
//	 })                        ;

// wire.writeByte(	byte, function(err) {    });
//  
//wire.writeByte(byte, function(err) {});
// 
//wire.writeBytes(command, [byte0, byte1], function(err) {});
// 
//wire.readByte(function(err, res) { // result is single byte })
// 
//wire.readBytes(command, length, function(err, res) {
//  // result contains a buffer of bytes
// });
//  
//wire.on('data', function(data) {
//// result for continuous stream contains data buffer, address, length, timestamp
//});
// 
//wire.stream(command, length, delay); // continuous stream, delay in ms
// 
//  
//// plain read/write
// 
//wire.write([byte0, byte1], function(err) {});
// 
//wire.read(length, function(err, res) {
//// result contains a buffer of bytes
//});
// 
