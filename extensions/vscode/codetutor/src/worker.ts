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


//for now just map topic to worker.  
export var workers: {[key: string] : Worker | undefined} = {};


//add a worker for specific topic.  
//for now just use last entry in book for this topic.  
async function addWorker(topic: string, type: string = "git") : Promise<boolean> {
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
        if ((Book.topicarray[topic] !== undefined)){
            length = Book.topicarray[topic].length;
        }
        if (length === 0) return false; //no work to do.



        let newworker: Worker = {
            bookentry: Book.topicarray[topic][length - 1],
            weight: 1,
            workflow: wf,
            type: type,
            efficiency: 0
        };
        workers[topic] = newworker;
    }
    else{
        workers[topic].weight += 1; //increase weight of worker.
        workers[topic].workflow = wf; //reset workflow.
    }
    return true;

}
