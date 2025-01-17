import typescript from '@rollup/plugin-typescript';

export default {

    // ...
	input: {
		grammar: 'grammar.js',
        python: 'python.js'
	},
	output: {
		// ...
		entryFileNames: 'entry-[name].js', 
        format: 'cjs'
	}, 
    plugins: [typescript()], 

};