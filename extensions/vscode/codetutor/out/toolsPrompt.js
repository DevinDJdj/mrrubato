"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ToolResultMetadata = exports.ToolUserPrompt = void 0;
const prompt_tsx_1 = require("@vscode/prompt-tsx");
const promptElements_1 = require("@vscode/prompt-tsx/dist/base/promptElements");
const vscode = __importStar(require("vscode"));
const toolParticipant_1 = require("./toolParticipant");
class ToolUserPrompt extends prompt_tsx_1.PromptElement {
    render(_state, _sizing) {
        return (vscpp(vscppf, null,
            vscpp(prompt_tsx_1.UserMessage, null,
                "Instructions: ",
                vscpp("br", null),
                "- The user will ask a question, or ask you to perform a task, and it may require lots of research to answer correctly. There is a selection of tools that let you perform actions or retrieve helpful context to answer the user's question. ",
                vscpp("br", null),
                "- If you aren't sure which tool is relevant, you can call multiple tools. You can call tools repeatedly to take actions or gather as much context as needed until you have completed the task fully. Don't give up unless you are sure the request cannot be fulfilled with the tools you have. ",
                vscpp("br", null),
                "- Don't make assumptions about the situation- gather context first, then perform the task or answer the question. ",
                vscpp("br", null),
                "- Don't ask the user for confirmation to use tools, just use them."),
            vscpp(History, { context: this.props.context, priority: 10 }),
            vscpp(PromptReferences, { references: this.props.request.references, priority: 20 }),
            vscpp(prompt_tsx_1.UserMessage, null, this.props.request.prompt),
            vscpp(ToolCalls, { toolCallRounds: this.props.toolCallRounds, toolInvocationToken: this.props.request.toolInvocationToken, toolCallResults: this.props.toolCallResults })));
    }
}
exports.ToolUserPrompt = ToolUserPrompt;
const dummyCancellationToken = new vscode.CancellationTokenSource().token;
/**
 * Render a set of tool calls, which look like an AssistantMessage with a set of tool calls followed by the associated UserMessages containing results.
 */
class ToolCalls extends prompt_tsx_1.PromptElement {
    async render(_state, _sizing) {
        if (!this.props.toolCallRounds.length) {
            return undefined;
        }
        // Note- for the copilot models, the final prompt must end with a non-tool-result UserMessage
        return vscpp(vscppf, null,
            this.props.toolCallRounds.map(round => this.renderOneToolCallRound(round)),
            vscpp(prompt_tsx_1.UserMessage, null, "Above is the result of calling one or more tools. The user cannot see the results, so you should explain them to the user if referencing them in your answer."));
    }
    renderOneToolCallRound(round) {
        const assistantToolCalls = round.toolCalls.map(tc => ({ type: 'function', function: { name: tc.name, arguments: JSON.stringify(tc.input) }, id: tc.callId }));
        return (vscpp(prompt_tsx_1.Chunk, null,
            vscpp(prompt_tsx_1.AssistantMessage, { toolCalls: assistantToolCalls }, round.response),
            round.toolCalls.map(toolCall => vscpp(ToolResultElement, { toolCall: toolCall, toolInvocationToken: this.props.toolInvocationToken, toolCallResult: this.props.toolCallResults[toolCall.callId] }))));
    }
}
/**
 * One tool call result, which either comes from the cache or from invoking the tool.
 */
class ToolResultElement extends prompt_tsx_1.PromptElement {
    async render(state, sizing) {
        const tool = vscode.lm.tools.find(t => t.name === this.props.toolCall.name);
        if (!tool) {
            console.error(`Tool not found: ${this.props.toolCall.name}`);
            return vscpp(prompt_tsx_1.ToolMessage, { toolCallId: this.props.toolCall.callId }, "Tool not found");
        }
        const tokenizationOptions = {
            tokenBudget: sizing.tokenBudget,
            countTokens: async (content) => sizing.countTokens(content),
        };
        const toolResult = this.props.toolCallResult ??
            await vscode.lm.invokeTool(this.props.toolCall.name, { input: this.props.toolCall.input, toolInvocationToken: this.props.toolInvocationToken, tokenizationOptions }, dummyCancellationToken);
        return (vscpp(prompt_tsx_1.ToolMessage, { toolCallId: this.props.toolCall.callId },
            vscpp("meta", { value: new ToolResultMetadata(this.props.toolCall.callId, toolResult) }),
            vscpp(promptElements_1.ToolResult, { data: toolResult })));
    }
}
class ToolResultMetadata extends prompt_tsx_1.PromptMetadata {
    toolCallId;
    result;
    constructor(toolCallId, result) {
        super();
        this.toolCallId = toolCallId;
        this.result = result;
    }
}
exports.ToolResultMetadata = ToolResultMetadata;
/**
 * Render the chat history, including previous tool call/results.
 */
class History extends prompt_tsx_1.PromptElement {
    render(_state, _sizing) {
        return (vscpp(prompt_tsx_1.PrioritizedList, { priority: this.props.priority, descending: false }, this.props.context.history.map((message) => {
            if (message instanceof vscode.ChatRequestTurn) {
                return (vscpp(vscppf, null,
                    vscpp(PromptReferences, { references: message.references, excludeReferences: true }),
                    vscpp(prompt_tsx_1.UserMessage, null, message.prompt)));
            }
            else if (message instanceof vscode.ChatResponseTurn) {
                const metadata = message.result.metadata;
                if ((0, toolParticipant_1.isTsxToolUserMetadata)(metadata) && metadata.toolCallsMetadata.toolCallRounds.length > 0) {
                    return vscpp(ToolCalls, { toolCallResults: metadata.toolCallsMetadata.toolCallResults, toolCallRounds: metadata.toolCallsMetadata.toolCallRounds, toolInvocationToken: undefined });
                }
                return vscpp(prompt_tsx_1.AssistantMessage, null, chatResponseToString(message));
            }
        })));
    }
}
/**
 * Convert the stream of chat response parts into something that can be rendered in the prompt.
 */
function chatResponseToString(response) {
    return response.response
        .map((r) => {
        if (r instanceof vscode.ChatResponseMarkdownPart) {
            return r.value.value;
        }
        else if (r instanceof vscode.ChatResponseAnchorPart) {
            if (r.value instanceof vscode.Uri) {
                return r.value.fsPath;
            }
            else {
                return r.value.uri.fsPath;
            }
        }
        return '';
    })
        .join('');
}
/**
 * Render references that were included in the user's request, eg files and selections.
 */
class PromptReferences extends prompt_tsx_1.PromptElement {
    render(_state, _sizing) {
        return (vscpp(prompt_tsx_1.UserMessage, null, this.props.references.map(ref => (vscpp(PromptReferenceElement, { ref: ref, excludeReferences: this.props.excludeReferences })))));
    }
}
class PromptReferenceElement extends prompt_tsx_1.PromptElement {
    async render(_state, _sizing) {
        const value = this.props.ref.value;
        if (value instanceof vscode.Uri) {
            const fileContents = (await vscode.workspace.fs.readFile(value)).toString();
            return (vscpp(Tag, { name: "context" },
                !this.props.excludeReferences && vscpp("references", { value: [new prompt_tsx_1.PromptReference(value)] }),
                value.fsPath,
                ":",
                vscpp("br", null),
                "``` ",
                vscpp("br", null),
                fileContents,
                vscpp("br", null),
                "```",
                vscpp("br", null)));
        }
        else if (value instanceof vscode.Location) {
            const rangeText = (await vscode.workspace.openTextDocument(value.uri)).getText(value.range);
            return (vscpp(Tag, { name: "context" },
                !this.props.excludeReferences && vscpp("references", { value: [new prompt_tsx_1.PromptReference(value)] }),
                value.uri.fsPath,
                ":",
                value.range.start.line + 1,
                "-$",
                vscpp("br", null),
                value.range.end.line + 1,
                ": ",
                vscpp("br", null),
                "```",
                vscpp("br", null),
                rangeText,
                vscpp("br", null),
                "```"));
        }
        else if (typeof value === 'string') {
            return vscpp(Tag, { name: "context" }, value);
        }
    }
}
class Tag extends prompt_tsx_1.PromptElement {
    static _regex = /^[a-zA-Z_][\w.-]*$/;
    render() {
        const { name } = this.props;
        if (!Tag._regex.test(name)) {
            throw new Error(`Invalid tag name: ${this.props.name}`);
        }
        return (vscpp(vscppf, null,
            '<' + name + '>',
            vscpp("br", null),
            vscpp(vscppf, null,
                this.props.children,
                vscpp("br", null)),
            '</' + name + '>',
            vscpp("br", null)));
    }
}
//# sourceMappingURL=toolsPrompt.js.map