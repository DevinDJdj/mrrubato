#nearley-railroad grammar/grammar.ne -o grammar/grammar.html
main -> (statement "\n"):+
statement -> "foo" | "bar"