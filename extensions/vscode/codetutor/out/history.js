"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HistoryMessages = exports.History = exports.MyPrompt = void 0;
const prompt_tsx_1 = require("@vscode/prompt-tsx");
const vscode_1 = require("vscode");
/**
 * Including conversation history in your prompt is important as it allows the
 * user to ask followup questions to previous messages. However, you want to
 * make sure its priority is treated appropriately because history can
 * grow very large over time.
 *
 * We've found that the pattern which makes the most sense is usually to prioritize, in order:
 *
 * 1. The base prompt instructions, then
 * 1. The current user query, then
 * 1. The last couple turns of chat history, then
 * 1. Any supporting data, then
 * 1. As much of the remaining history as you can fit.
 *
 * For this reason, we split the history in two parts in the prompt, where
 * recent prompt turns are prioritized above general contextual information.
 */
class MyPrompt extends prompt_tsx_1.PromptElement {
    render() {
        return (vscpp(vscppf, null,
            vscpp(prompt_tsx_1.SystemMessage, { priority: 100 }, "Here are your base instructions. They have the highest priority because you want to make sure they're always included!"),
            vscpp(HistoryMessages, { history: this.props.history.slice(0, -2), priority: 0 }),
            vscpp(HistoryMessages, { history: this.props.history.slice(-2), priority: 80 }),
            vscpp(prompt_tsx_1.UserMessage, { priority: 90 }, this.props.userQuery),
            vscpp(prompt_tsx_1.UserMessage, { priority: 70 }, "With a slightly lower priority, you can include some contextual data about the workspace or files here...")));
    }
}
exports.MyPrompt = MyPrompt;
/**
 * We can wrap up this history element to be a little easier to use. `prompt-tsx`
 * has a `passPriority` attribute which allows an element to act as a 'pass-through'
 * container, so that its children are pruned as if they were direct children of
 * the parent. With this component, the elements
 *
 * ```
 * <HistoryMessages history={this.props.history.slice(0, -2)} priority={0} />
 * <HistoryMessages history={this.props.history.slice(-2)} priority={80} />
 * ```
 *
 * ...can equivalently be expressed as:
 *
 * ```
 * <History history={this.props.history} passPriority older={0} recentPriority={80} />
 * ```
 */
class History extends prompt_tsx_1.PromptElement {
    render() {
        return (vscpp(vscppf, null,
            vscpp(HistoryMessages, { history: this.props.history.slice(0, -2), priority: this.props.older }),
            vscpp(HistoryMessages, { history: this.props.history.slice(0, -2), priority: this.props.newer })));
    }
}
exports.History = History;
/**
 * The History element simply lists user and assistant messages from the chat
 * context. If things like tool calls or file trees are relevant for, your
 * case, you can make this element more complex to handle those cases.
 */
class HistoryMessages extends prompt_tsx_1.PromptElement {
    render() {
        const history = [];
        for (const turn of this.props.history) {
            if (turn instanceof vscode_1.ChatRequestTurn) {
                history.push(vscpp(prompt_tsx_1.UserMessage, null, turn.prompt));
            }
            else if (turn instanceof vscode_1.ChatResponseTurn) {
                history.push(vscpp(prompt_tsx_1.AssistantMessage, { name: turn.participant }, chatResponseToMarkdown(turn)));
            }
        }
        return (vscpp(prompt_tsx_1.PrioritizedList, { priority: 0, descending: false }, history));
    }
}
exports.HistoryMessages = HistoryMessages;
const chatResponseToMarkdown = (response) => {
    let str = '';
    for (const part of response.response) {
        if (response instanceof vscode_1.ChatResponseMarkdownPart) {
            str += part.value;
        }
    }
    return str;
};
//# sourceMappingURL=history.js.map