import {
	BasePromptElementProps,
	PromptElement,
	PromptSizing,
	UserMessage, 
    useKeepWith,
} from '@vscode/prompt-tsx';
import * as vscode from 'vscode';



export interface PromptProps extends BasePromptElementProps {
	userQuery: string;
}


export class PlayPrompt extends PromptElement<PromptProps, void> {
	render(_state: void, _sizing: PromptSizing) {
        const KeepWith = useKeepWith();
		return (
			<>
				<UserMessage>
					You are a cat! Reply in the voice of a cat, using cat analogies when
					appropriate. Be concise to prepare for cat play time. Give a small random
					python code sample (that has cat names for variables).
				</UserMessage>
			</>
		);
	}
}

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