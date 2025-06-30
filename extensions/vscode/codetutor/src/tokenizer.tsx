import * as vscode from 'vscode';
import * as Book from './book';

export interface Token {
    type: number;
    line: number;
    column: number;    
    topic: string;
    data: string;
    date: number; //date in YYYYMMDD format.
}

function newToken(line: number, column: number, topic: string, date: number): Token {
    return {
        type: -1, //default type
        line: line,
        column: column,
        topic: topic,
        data: "",
        date: date
    };
}

export function execute(lines: Array<Array<Token>>, topic: string = "NONE"): string {
    //now we have a list of tokens.  We need to group them by line.
    let rettext = "";
    for (let i = 0; i < lines.length; i++) {
        //for now just based on the initial token.  
        // Other logic in the fnmap itself.  
        let j=0;
        if (lines[i][j].type === -1) {
            //this is an identifier or just text, we need to add it to the line.
            rettext += lines[i][j].data + " ";
        }
        else {
            //this is a function.  
            if (Book.defmap[lines[i][j].data.length] !== undefined && Book.defmap[lines[i][j].data.length][lines[i][j].data] !== undefined) {
                //this is a function, we need to add it to the line.
                if (Book.fnmap[lines[i][j].data] !== undefined) {
                    //this should remove any data in the line which is 
                    // used in the function and no longer needed.  
                    rettext += (Book.fnmap[lines[i][j].data])(lines[i], j);
                }

            }
        }

    }
    return rettext;

}
export function tokenize(str: string, topic: string = "NONE") {
    let out: Token[] = []
    let currentPosition = 0
    let currenttopic = topic;
    let currentline = 0;
    let currentcolumn = 0;
    let currentdate = parseInt(Book.formatDate());
    let instr = false;
    let currenttoken: Token = newToken(currentline, currentcolumn, currenttopic, currentdate);
    let lines = [];
    //should be able to read multiple lines.  
    while (currentPosition < str.length) {
      // Process token, increment currentPosition
        let pos = Book.defstring.indexOf(str[currentPosition]);
        if (pos >= 0) {
            //for now type is just position in defstring
            if (instr){
                //handle as needed.  
                if (currenttoken !==null && currenttoken.data.trim().length > 0) {
                    out.push(currenttoken);
                    currenttoken = newToken(currentline, currentcolumn, currenttopic, currentdate);
                }
            }
            else{
                currenttoken.type = pos;
                currenttoken.data = str[currentPosition];
                out.push(currenttoken);
                currenttoken = null;
                instr = false;
            }
        }
        else if (str[currentPosition] === '\n') {
            if (currenttoken !==null && currenttoken.data.trim().length > 0) {
                out.push(currenttoken);
                lines.push(out);
                out = [];

            }
            currenttoken = null;
            currentcolumn = -1;
            currentline++;
            instr = false;
        }
        else{
            currenttoken.data += str[currentPosition];
            instr = true;
        }

        currentcolumn++;
        if (currenttoken === null) {
            currenttoken = newToken(currentline, currentcolumn, currenttopic, currentdate);
        }
      currentPosition++;

    }

    if (instr) {
        out.push(currenttoken);
    }
    if (out.length > 0) {
        lines.push(out);
    }
    for (let i = 0; i < lines.length; i++) {
        let deflookup = "";
        let fnsequence = "";
        let fns = [];
        let params = [];
        for (let j = 0; j < lines[i].length; j++) {
            switch (lines[i][j].type) {
                case -1: //identifier
                    //check previous token.  
                    params.push(lines[i][j]);
                    break;
                default: //code
                    fnsequence = lines[i][j].data;
                    //check if this is a function.  

                    if (Book.defmap[fnsequence.length+1] !== undefined) {
                        //lookahead.
                        //is this a function.
                        let k=j-1;
                        let potentialfn = fnsequence;
                        if (k> -1 && lines[i][k].type !== -1) {
                            //still function sequence.  
                            potentialfn = lines[i][k].data + potentialfn;
                            if (Book.defmap[potentialfn.length] !== undefined && Book.defmap[potentialfn.length][potentialfn] !== undefined) {
                                //this is a function.
                                fnsequence = potentialfn;
                                lines[i][j].data = potentialfn;
                                //remove the previous token.  
                                lines[i].splice(k, 1);
                                j--;
                                k = -1;
                                break;
                            }
                            k--;
                            
                        }
                    }
                    if (Book.defmap[fnsequence.length] !== undefined && Book.defmap[fnsequence.length][fnsequence] !== undefined) {
                        //this is a function.

                    }
                    break;
            }
            
        }
    }
    return lines;

}

