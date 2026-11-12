

export class state {
    static selectionhistory: any[] = [];
    static selectionmap: Record<string, any> = {};
    static cmdhistory: any[] = [];
    static transcripthistory: any[] = [];
    static currentfunctions: any[] = ["Hello"];
    static currenttopic: string = "";
    static currentbook: string = "";
    static filter: any[] = [];
    static tabs: any[] = [];
    static webtabs: any[] = [];
    static last_sent: number = 0;
    static last_received: number = 0;
    static last_edited: number = 0;
}

export function getFunctions(): any[] {
    return state.currentfunctions;
}

export function setFunctions(funcs: any[]): void {
    state.currentfunctions.length = 0;
    state.currentfunctions.push(...funcs);
    console.log('Current functions set to:', state.currentfunctions);
}



// 2. Async function to send the HTTP request
export async function sendDataToFlask(mystate: typeof state): Promise<typeof state | null> {
  const url = 'http://127.0.0.1:8003/state/update/';
  let last_sent = Date.now();
  mystate.last_sent = last_sent;
  const payload = mystate;
  console.log('Sending data to Flask with payload:', payload);
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload), // Serialize payload to a JSON string with last_updated timestamp
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Parse and return the strongly-typed JSON response
    const data: typeof state = await response.json();
    console.log('Data received from Flask:', data);
    data.last_received = Date.now();
    data.last_edited = 0; //dont update..
    return data;
  } catch (error) {
    console.error('Failed to send request to Flask:', error);
    return null;
  }
}
