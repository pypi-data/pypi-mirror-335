#!/bin/bash

cd "$(dirname "$0")"
antlr4 -visitor -no-listener -Dlanguage=Python3 AtoLexer.g4 AtoParser.g4
