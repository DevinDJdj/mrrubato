declare global {
	interface HTMLCanvasElement extends EventTarget {readonly _:never;}
	interface HTMLImageElement extends EventTarget {readonly _:never;}
	interface HTMLVideoElement extends EventTarget {readonly _:never;}
	interface Navigator {readonly _:never;}
	type PretrainedProcessorOptions = any;
}

declare module '@huggingface/transformers' {
	export interface MgpstrProcessor {
		batch_decode(...args:any[]):any
	}
}

export {}