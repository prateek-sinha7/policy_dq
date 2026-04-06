# Feature: Policy Driven Data Quality Validator

## requirements

system validates structured datasets

inputs:
CSV
JSON

rules:
required field
type check
regex
range
unique
cross-field validation

outputs:
console summary
JSON report
Markdown report

exit non-zero if severity threshold exceeded

rules must load from:
local YAML or JSON
MCP source


## design

architecture:

CLI layer separate from business logic

modules:

parsers
rules loader
validators
reporters
MCP client

validation flow:

load dataset
load rules
run validators
collect errors
generate reports

tradeoff:

used eval for cross-field rules for simplicity


## tasks

1 create project structure

2 implement parsers

3 implement rule loader

4 implement validators

5 implement validation engine

6 implement reporters

7 implement CLI

8 implement MCP integration

9 write unit tests

10 write integration tests