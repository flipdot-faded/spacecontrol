var exec = require('child_process').exec;
var fs = require('fs');
var request = require('request');

var OLD_STATE_FILE = __dirname+'/laststate';
var SHUTDOWN_FILE = __dirname+'/shutdowndone';
var DOOR_OPEN = 0;
var DOOR_CLOSED = 1;
var SECONDS_UNTIL_SHUTDOWN = 60 * 1; // 5 mins

readDoorStatus(function(doorStatus) {  
  // ensure the laststate file exists
  if(!fs.existsSync(OLD_STATE_FILE)){
    var content = doorStatus == DOOR_OPEN ? DOOR_OPEN : unixNow();
    fs.writeFileSync(OLD_STATE_FILE, content);
  }

  var oldStatus = fs.readFileSync(OLD_STATE_FILE, 'utf8');
debugger;  
  // if its open, save it was open the last time
  if(doorStatus == DOOR_OPEN) {
    if(fs.existsSync(SHUTDOWN_FILE)){
      fs.unlinkSync(SHUTDOWN_FILE);
    }
    fs.writeFileSync(OLD_STATE_FILE, DOOR_OPEN);

    // ensure the hackerDS system in powered on
    request.post('http://hutschienenpi:8080/CanBus/regulus/SetPort?port=0&state=1');   

    console.log('door is still open');
    return;
  }

  // if the shutdown file was created stop here
  if(fs.existsSync(SHUTDOWN_FILE)){
    return;
  }
  
  // if the door was open the last time,
  // but is not open now, it has closed:
  // dump the current time stamp to start counting
  if(oldStatus == DOOR_OPEN && doorStatus == DOOR_CLOSED) { 
    fs.writeFileSync(OLD_STATE_FILE, unixNow());
    return;
  }

  // check if the 30 mins have passed
  var timeDiff = unixNow() - oldStatus;
  console.log(timeDiff);
  
  if(timeDiff >= SECONDS_UNTIL_SHUTDOWN){
    console.log('SHUTDOWN');
    shutdownMachines(function(){
      // create the shutdown file to mark we have shut down
      fs.writeFileSync(SHUTDOWN_FILE, unixNow());
    });
  }
});

function shutdownMachines(callback) {
  var machines = [
    {name:'pi-display',u:'pi'},
    {name:'pi-gui',u:'pi'}
  ]
  
  machines.forEach(function(m){
    var command = 'ssh '+m.u+'@'+m.name+' sudo shutdown -h 0';
    exec(command);
  });

  // shut down the energy
  setTimeout(function(){
    request.post('http://hutschienenpi:8080/CanBus/regulus/SetPort?port=0&state=0');
  }, 1000 * 60 * 2);
  
  if(callback) callback();
}

function readDoorStatus(callback){
  exec('/usr/local/bin/gpio -g read 4', function(err, out){
   if(callback) callback(out);
  });
}

function unixNow(){
  return Math.round( new Date().getTime()/1000);
}
