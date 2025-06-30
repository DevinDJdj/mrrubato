import * as vscode from 'vscode';
import * as Book from './book';
import ollama from 'ollama';


interface Workflow {
    prompts: string[];  //prompts used for the workflow.
    //this can include use substitution of responses 
    // from previous steps.  
    responses: string[]; //responses from the model.
    step: number; //current step in the workflow.

}

interface Worker {
    bookentry: Book.BookTopic;
    weight: number; //time weight of worker.  
    workflow: Workflow; //workflow used for the worker.
    efficiency: number; //efficiency of the worker.
    type: string; //type of worker.  git, todo, etc.
    //what is percentage of useful output?  
}


export var currentTopicIndex: number = 0; //current topic being worked on.
//this is used to track the current topic being worked on by the worker.
//for now just map topic to worker.  
export var workers: {[key: string] : Worker | undefined} = {};

export var worktopics: string[] = []; //list of topics being worked on.

export async function incrementWorker() : Promise< Worker > {
    let topic = worktopics[currentTopicIndex];
    if(workers[topic] !== undefined){
        //reset workflow.
        workers[topic].workflow.step++;
        if (workers[topic].workflow.step > workers[topic].workflow.prompts.length) {
            //reset the step.
            workers[topic].workflow.step = 0;
            //return next worker.  
            currentTopicIndex++;
            if (currentTopicIndex >= worktopics.length) {
                currentTopicIndex = 0; //reset to first topic.
            }
            return workers[worktopics[currentTopicIndex]];
        }
        else{
            //return current worker.  
            return workers[topic];
        }
    }

}

export async function removeWorker(topic: string) : Promise<boolean> {
    if(workers[topic] !== undefined){
        delete workers[topic];
        //remove from worktopics.
        const index = worktopics.indexOf(topic);
        if (index > -1) {
            worktopics.splice(index, 1);
        }
        return true;
    }
    return false;
}
//add a worker for specific topic.  
//for now just use last entry in book for this topic.  
export async function addWorker(topic: string, type: string = "git") : Promise<boolean> {
    let wf: Workflow = {
        prompts: ["The next GIT Commits for this file would look like this:"],
        responses: [],
        step: 0
    };
    if (type !== "git"){
        wf.prompts = ["The next TODO items for this file would look like this:"];
    }

    if(workers[topic] === undefined){
        //create a new worker.  

        let length = 0;
        //0 is the most recent.  
        if ((Book.topicarray[topic] !== undefined)){
            length = Book.topicarray[topic].length;
        }
        if (length === 0) return false; //no work to do.



        let newworker: Worker = {
            bookentry: Book.topicarray[topic][0],
            weight: 1,
            workflow: wf,
            type: type,
            efficiency: 0
        };
        workers[topic] = newworker;
        worktopics.push(topic); //add to worktopics.
//        currentWorkTopic = topic; //set current work topic.
    }
    else{
        workers[topic].weight += 1; //increase weight of worker.
        workers[topic].workflow = wf; //reset workflow.
    }
    return true;

}


export function initWorkers(context: vscode.ExtensionContext) {
    //start a worker for each %%+ in book.  
    for (const [key, val] of Object.entries(Book.arrays["%%"])) {    
        //really should use same functions.  
//        let tokens = Book.getTokens(text);
//        Book.executeTokens(tokens);        
        if (key.trim() === "+"){
            addWorker(val[val.length-1].topic, "git");
        }
    }
 }