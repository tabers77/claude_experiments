# Skill: spec_from_text

**Purpose**: Turn vague business input into a testable spec

**Use when**:
- Converting PM requirements to technical specs
- Business cases need structure
- Requirements are ambiguous
- Need to surface missing information early

---

## Process

When converting free-form text to spec:

1) **Parse requirements and constraints**
   - What is being asked for?
   - What are the explicit constraints?
   - What's the success criteria?

2) **Generate structured spec** (YAML or JSON)
   - Clear, machine-readable format
   - Versioned and diffable

3) **List assumptions made**
   - What did you infer that wasn't stated?
   - What defaults did you choose?

4) **Surface open questions**
   - What's ambiguous?
   - What decisions need stakeholder input?

5) **Identify implied constraints**
   - Performance requirements?
   - Security requirements?
   - Compatibility requirements?

---

## Output Format

```yaml
# Spec: [Feature Name]
# Generated from: [source description]
# Date: [date]

## Requirements
goals:
  - [goal 1]
  - [goal 2]

constraints:
  - [constraint 1]
  - [constraint 2]

success_criteria:
  - [criterion 1]
  - [criterion 2]

## Structured Spec
[YAML/JSON structure specific to the domain]

## Assumptions
- [assumption 1]: [reasoning]
- [assumption 2]: [reasoning]

## Open Questions
1. [question] - [why it matters]
2. [question] - [why it matters]

## Implied Constraints
- [constraint]: [inferred from]
```

---

## Example Usage

```
/spec_from_text
Convert this PM template into:
- BusinessCaseSpec
- Required capabilities
- Explicit constraints

[paste PM text here]
```

Or:

```
/spec_from_text
Turn this Slack thread into a feature spec:
[paste conversation]
```
