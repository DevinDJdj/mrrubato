"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PlayPrompt = void 0;
const prompt_tsx_1 = require("@vscode/prompt-tsx");
class PlayPrompt extends prompt_tsx_1.PromptElement {
    render(_state, _sizing) {
        const KeepWith = (0, prompt_tsx_1.useKeepWith)();
        return (vscpp(vscppf, null,
            vscpp(prompt_tsx_1.UserMessage, null, "You are a cat! Reply in the voice of a cat, using cat analogies when appropriate. Be concise to prepare for cat play time. Give a small random python code sample (that has cat names for variables).")));
    }
}
exports.PlayPrompt = PlayPrompt;
/*
export class ToolPrompt extends PromptElement {
    async render(_state: void, sizing: PromptSizing) {
        const result = await vscode.lm.invokeTool("get_alerts", {
            parameters: null,
            tokenizationOptions: {
                tokenBudget: sizing.tokenBudget,
                countTokens: (text, token) => sizing.countTokens(text, token),
            },
        });

        return <ToolResult data={result} priority={20} />;
    }
}
*/ 
//# sourceMappingURL=prompts.js.map