# Prompt Quality Scoring Criteria

## Overview
This document defines a scoring framework to evaluate the quality of prompts used in AI/LLM systems. Each criterion is scored from **0 to 10**, and the final score is calculated as the **average of all criteria**.

---

## 1. Clarity (0–10)
**Definition:**  
Evaluates whether the prompt is easy to understand and has a clear goal.

**Checks:**
- Is the instruction simple and unambiguous?
- Is the objective स्पष्ट and direct?
- Are there any vague or confusing terms?

---

## 2. Specificity / Details (0–10)
**Definition:**  
Evaluates whether sufficient details and requirements are provided.

**Checks:**
- Are requirements clearly defined?
- Is the scope well specified?
- Are constraints or expectations included?

---

## 3. Context (0–10)
**Definition:**  
Checks whether background information, audience, or use case is mentioned.

**Checks:**
- Is relevant context provided?
- Is the target audience defined?
- Is the use case or scenario clear?

---

## 4. Output Format & Constraints (0–10)
**Definition:**  
Checks whether the expected output format, tone, or length is specified.

**Checks:**
- Is the output format defined (table, JSON, markdown, etc.)?
- Are constraints like length or tone specified?
- Are formatting instructions clear?

---

## 5. Persona Defined (0–10)
**Definition:**  
Confirms whether the prompt assigns a specific role to the model.

**Checks:**
- Does the prompt define a role (e.g., "You are an Azure architect")?
- Is the role relevant to the task?
- Does the role guide the response effectively?

---

## Final Score Calculation

The final score is calculated as the **average of all five criteria**:


---

## Evaluation Template

| Criteria                     | Score (0–10) |
|-----------------------------|-------------|
| Clarity                     |             |
| Specificity / Details       |             |
| Context                     |             |
| Output Format & Constraints |             |
| Persona Defined             |             |
| **Final Score (Average)**   |             |

---

## Example

| Criteria                     | Score |
|-----------------------------|-------|
| Clarity                     | 8     |
| Specificity / Details       | 7     |
| Context                     | 6     |
| Output Format & Constraints | 9     |
| Persona Defined             | 8     |
| **Final Score**             | 7.6   |

---

## Summary
A high-quality prompt should:
- Be clear and easy to understand  
- Provide sufficient details  
- Include relevant context  
- Define output format and constraints  
- Assign a meaningful persona  

This scoring system helps standardize prompt evaluation in AI and agent-based systems.
