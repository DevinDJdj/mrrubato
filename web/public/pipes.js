

var pipe_ids = {};

var pipe_channels = {};
var pipe_transcripts = {};
var my_pipe_id = "0";
var active_tab = "0";
//msg, time, direction (out/in)

function findNow(mytime = -1, pipe_name = IPC_NAME){

    //reverse time search
    for (pi=pipe_transcripts[pipe_name].length-1; pi>-1; pi--){
        if (mytime > pipe_transcripts[pipe_name][pi].time){
            break;
        }
    }
    return pi+1;
}

function pipeRecord(datastr, pipe_name = IPC_NAME, mytime = -1, incoming=true){
    if (mytime == -1){
        mytime = Date.now(); //milliseconds since Jan 1 1970
    }
    myNow = findNow(mytime, pipe_name);
    //what is the use-case of non-current time?  

    mymsg = {"time": mytime, "data": datastr, "incoming": incoming};
    pipe_transcripts[pipe_name].splice(myNow, 0, mymsg);
    return mymsg;
}


function pipeGet(pipe_name = IPC_NAME){
    if (typeof(pipe_channels[pipe_name]) ==='undefined'){
        pipe_channel[pipe_name] = {};
        pipe_channel[pipe_name]['ch'] = new BroadcastChannel(pipe_name);
        pipe_channel[pipe_name]['msgcnt'] = 0;
        
    }
    if (typeof(pipe_transcripts[pipe_name]) === 'undefined'){
        pipe_transcripts[pipe_name] = [];
    }

    return pipe_channel[pipe_name]['ch'];
}

function randPipe(){
    let result = "";
    for (let pi = 0; pi < 5; pi++) {
      result += Math.floor(Math.random() * 10);
    }
    return result;    
}

function pipeListen(pipe_name = IPC_NAME){
    ch = pipeGet(pipe_name);
    ch.addEventListener ('message', (event) => {
        console.log(event.data);
        if (event.data.startsWith("pong")){
            //pick random identifier not in the pong list.  
            tokens = event.data.split(" ");

            pid = tokens[1];
            pipe_ids[pipe_name + "_" + pid] = pipeGet(pipe_name + "_" + pid);
            if (my_pipe_id == pid){
                //pick a new pipe ID
                my_pipe_id = randPipe();
                pipeListen(pipe_name + "_" + randPipe()); //directly to you this page.  
                //do we need this?  
                //how do we 
            }


        }
        else if (event.data.startsWith("ping")){
            //if this is not our private channel, then send pong.  
            pipeSend("pong " + my_pipe_id, pipe_name);
        }
        else if (event.data.startsWith("tab activated")){
            tokens = event.data.split(" ");

            pid = tokens[2];
            active_tab = pid;
            //use this to build LLM context or other stuff.  
            //send directly to active tab.  If no response, then set active tab to self.  
            if (pid == my_pipe_id){
                console.log("active tab is self");
            }
        }
        pipeRecord(event.data, pipe_name);
        //what do we do with this data?  
        //for now 
    });
    window.addEventListener('focus', function() {
        // Code to execute when the tab becomes active
        console.log('Tab activated');
        pipeSend("tab activated " + my_pipe_id, pipe_name);
      });    
      if (pipe_name == IPC_NAME){
        //dont want to send this to private channel for self.  
          pipeSend("ping", pipe_name);
      }
    
}

function pipeSend(datastr, pipe_name = IPC_NAME){

    ch = pipeGet(pipe_name);
    ch.postMessage(datastr);
    pipeRecord(datastr, pipe_name, -1, false);
    
}
