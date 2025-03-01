import * as webllm from "https://esm.run/@mlc-ai/web-llm";
var stopllm = false;
export default stopllm;
/*************** WebLLM logic ***************/
const messages = [
  {
    content: "You are a helpful AI agent helping users.",
    role: "system",
  },
];

const availableModels = webllm.prebuiltAppConfig.model_list.map(
  (m) => m.model_id,
);
let selectedModel = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
//selectedModel = "DeepSeek-R1-Distill-Qwen-7B-q4f16_1-MLC";
//selectedModel = "DeepSeek-R1-Distill-Qwen-1.5B-q4f16_1-MLC"; //this will be faster/better.  
//selectedModel = "TinyLlama-1.1B-Chat-v0.4-q4f16_1-MLC";
//selectedModel = "Qwen2.5-Coder-7B-Instruct-q4f32_1-MLC";

// Callback function for initializing progress
function updateEngineInitProgressCallback(report) {
  console.log("initialize", report.progress);
  document.getElementById("download-status").textContent = report.text;
}

// Create engine instance
const engine = new webllm.MLCEngine();
engine.setInitProgressCallback(updateEngineInitProgressCallback);

async function initializeWebLLMEngine() {
  document.getElementById("download-status").classList.remove("hidden");
  selectedModel = document.getElementById("model-selection").value;
  const config = {
    temperature: 0.5,
    top_p: 1,
    sliding_window_size: 1024,  //do we have to use this as 1024 or 2048?  
    context_window_size: -1,
    attention_sink_size: 4, 
    repetition_penalty: 1.0
//    max_new_tokens: 300
//    max_tokens: 300
  };
  await engine.reload(selectedModel, config);

}

async function streamingGenerating(messages, onUpdate, onFinish, onError) {
  try {
    let curMessage = "";
    let usage;
    const completion = await engine.chat.completions.create({
      stream: true,
      messages,
      max_tokens: 512,
      stream_options: { include_usage: true },
//      response_format: {
//        type: "json_object",
//        schema: schema,
//      } as webllm.ResponseFormat,      
    });
    for await (const chunk of completion) {
      const curDelta = chunk.choices[0]?.delta.content;
      if (curDelta) {
        curMessage += curDelta;
      }
      if (chunk.usage) {
        usage = chunk.usage;
      }
      onUpdate(curMessage);
      //cancel here if needed.  
      if (stopllm){
        stopllm = false;
        onFinish(curMessage, usage);
        engine.interruptGenerate();
        return;
      }
    }
    const finalMessage = await engine.getMessage();
    onFinish(finalMessage, usage);
  } catch (err) {
    onError(err);
  }
}


function createMessages(input){
  //parse meta language especially @@question ==answer.  
  //and create the JSON for this.  
  //find all @@ and ==
  let qs = [];
  let as = [];
  let startIndex = 0;

  while (startIndex < input.length) {
    let index = input.indexOf("@@", startIndex);
    if (index === -1) {
      break;
    }
    qs.push(index);
    startIndex = index + 1;
  }
  startIndex = 0;
  while (startIndex < input.length) {
    let index = input.indexOf("==", startIndex);
    if (index === -1) {
      break;
    }
    qs.push(index);
    startIndex = index + 1;
  }

  let ms = [];
  if (qs.length == as.length){
    for (mi=0; mi<qs.length; mi++){
      const question = {
        content: qs[i],
        role: "user"

      };
      ms.push(question);
      const answer = {
        content: as[mi], 
        role: "assistant"
      };
      ms.push(answer);
    }

  }
  return ms;


}
/*************** UI logic ***************/
export function onMessageSend() {
  const input = document.getElementById("user-input").value.trim();
  const message = {
    content: input,
    role: "user",
  };
  if (input.length === 0) {
    return;
  }
  document.getElementById("send").disabled = true;

  const messages = [
    {
      content: $('#prompt').val(),
      role: "system",
    },
  ];
  let myms = createMessages(input);
  if (myms.length > 0){
    messages.concat(myms);
  }
  else{
    messages.push(message);
  }
  appendMessage(message);

  document.getElementById("user-input").value = "";
  document
    .getElementById("user-input")
    .setAttribute("placeholder", "Generating...");

  const aiMessage = {
    content: "typing...",
    role: "assistant",
  };
  appendMessage(aiMessage);

  const onFinishGenerating = (finalMessage, usage) => {
    updateLastMessage(finalMessage);
    if (ChatLocalDone !== undefined){
      ChatLocalDone(finalMessage);
    }
  
    document.getElementById("send").disabled = false;
    const usageText =
      `prompt_tokens: ${usage.prompt_tokens}, ` +
      `completion_tokens: ${usage.completion_tokens}, ` +
      `prefill: ${usage.extra.prefill_tokens_per_s.toFixed(4)} tokens/sec, ` +
      `decoding: ${usage.extra.decode_tokens_per_s.toFixed(4)} tokens/sec`;
    document.getElementById("chat-stats").classList.remove("hidden");
    document.getElementById("chat-stats").textContent = usageText;
  };

  streamingGenerating(
    messages,
    updateLastMessage,
    onFinishGenerating,
    console.error,
  );
}

function appendMessage(message) {
  const chatBox = document.getElementById("chat-box");
  const container = document.createElement("div");
  container.classList.add("message-container");
  const newMessage = document.createElement("div");
  newMessage.classList.add("message");
  newMessage.textContent = message.content;

  if (message.role === "user") {
    container.classList.add("user");
  } else {
    container.classList.add("assistant");
  }

  container.appendChild(newMessage);
  chatBox.appendChild(container);
  chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message


}

function updateLastMessage(content) {
  const messageDoms = document
    .getElementById("chat-box")
    .querySelectorAll(".message");
  const lastMessageDom = messageDoms[messageDoms.length - 1];
  lastMessageDom.textContent = content;
  let statuscontent = content.slice(content.length-50);
  $("#chat-status").val(statuscontent);
  if (lastread == 0 && content.length > 200 && ChatLocalUpdate !== undefined){
    ChatLocalUpdate(content);
  }
  else if (lastread !=0 && reading == false && ChatLocalUpdate !== undefined){
    ChatLocalUpdate(content.slice(lastread, lastread+200));
  }

}

/*************** UI binding ***************/
availableModels.forEach((modelId) => {
  const option = document.createElement("option");
  option.value = modelId;
  option.textContent = modelId;
  document.getElementById("model-selection").appendChild(option);
});
document.getElementById("model-selection").value = selectedModel;
document.getElementById("download").addEventListener("click", function () {
  initializeWebLLMEngine().then(() => {
    document.getElementById("send").disabled = false;
  });
});
document.getElementById("send").addEventListener("click", function () {
  onMessageSend();
});
