
function tokenize(input) {
    return input
        .replace(/\(/g, ' ( ')
        .replace(/\)/g, ' ) ')
        .trim()
        .split(/\s+/);
}

function parse(tokens) {
    if (tokens.length === 0) {
        throw new SyntaxError("Unexpected EOF");
    }

    let token = tokens.shift();

    if (token === '(') {
        let list = [];
        while (tokens[0] !== ')') {
            list.push(parse(tokens));
        }
        tokens.shift(); // remove ')'
        return list;
    } else if (token === ')') {
        throw new SyntaxError("Unexpected )");
    } else {
        return atom(token);
    }
}

function atom(token) {
    if (!isNaN(token)) {
        return Number(token);
    } else {
        return token;
    }
}

function parseSExpression(input) {
    const tokens = tokenize(input);
    return parse(tokens);
}
// Example 2
const input3 = "(if (> x 0) (+ x 1) (- x 1))";
const parsed3 = parseSExpression(input3);
console.log("Example 2 - Input S-expression:", input3);
console.log("Example 2 - Parsed S-expression:", JSON.stringify(parsed3, null, 2));
