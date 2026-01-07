//genbook, gencomments, gencode, genhelp
import * as vscode from 'vscode';
import { posix, basename } from 'path';
import * as tokenizer from './tokenizer'; // Import the Token interface
import * as  Worker from './worker'; // Import the Worker class
import * as fs from 'fs';
import * as Book from './book';
import ollama from 'ollama';


export async function genbook(prompt: string) : Promise<string> {
    //generate next book entries for this topic.  
    //Use other topics as samples..
    return "";
}

export async function gencomments(prompt: string) : Promise<string> {
    //utilize samples from less commented and more commented code from existing codebase..
    //essentially purge comments from code and then add back..
    //then use existing code as last token, expecting commented code output.  
    return "";
}

export async function gencode(prompt: string) : Promise<string> {
    //utilize latest git changes as context for generating code.
    //for now try to get last N commit diffs for topic and use as context.
    return "";
}

export async function genhelp(prompt: string) : Promise<string> {
    //generate explanation for this topic and any commands which are mentioned..
    return "";
}


