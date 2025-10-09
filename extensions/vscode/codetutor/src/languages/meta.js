
export default class LANG {
    config = {};
    keybot = 48;
    keyoffset = 0;
    name = "meta";
    funcdict = {};

    constructor(){
        console.log("meta language constructor");
    }

    init(config){
        //optional init function
        console.log("meta language init");
        this.config = config || {};
        this.load();
    }

    load(){
        let obj = {
            "2":{
            },
            "3":{
                "Set Topic": [0, 4, 5],
                "Add Topic": [0, 6, 7],
            },

        }
        if (this.name in this.config['languages']){
            //merge existing config with defaults
            obj = Object.assign({}, obj, this.config['languages'][this.name]);
            this.config['languages'][this.name] = obj;
        }
        this.funcdict["Set Topic"] = this.set_topic;
    }

    set_topic(sequence, words){
        console.log("meta set_topic", sequence, words);
        if (sequence.length > 0){
            //set topic to 
            numtopics = sequence[0]-this.keybot-this.keyoffset;
            //select this number of topics and share those topics.  
        }
    }

    act(cmd, sequence, words){
        console.log("meta act", cmd, sequence, words);
        if (cmd in this.funcdict){
            func = this.funcdict[cmd];
            if (sequence.length ===1 && sequence[0] === this.keybot+this.keyoffset){
                func([], words); //no parameters
            }
            else if (sequence.length > 1 && JSON.stringify(sequence.slice(-2)) === JSON.stringify([this.keybot+this.keyoffset, this.keybot+this.keyoffset])){
                func(sequence.slice(0, -2), words);
            }
            else{
                return 1; //more keys needed
            }

        }
        else{
            console.log("meta unknown command", cmd);
        }
    }

    word(sequence, words=[]){
        cmd = "";
        sl = sequence.length;
        if (sl in this.config['languages'][this.name]){
            for (const [key, value] of Object.entries(this.config['languages'][this.name][sl])) {
                if (JSON.stringify(value) === JSON.stringify(sequence.slice(-sl))){
                    cmd = key;
                    break;
                }
            }
        }
        return cmd;

    }
}