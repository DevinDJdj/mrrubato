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

export function tokenize(str: string) {
    const out: Token[] = []
    let currentPosition = 0
  
    while (currentPosition < str.length) {
      // Process token, increment currentPosition
      
      currentPosition++;
    }
  
    return out
}

