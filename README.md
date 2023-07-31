# Normalize tables

## What's this about?

- Motivation: [Zero System's job application take-home assignment](./docs/zeros_assignment.md).
- App's job: capture customer's transform rationales on standardizing their spreadsheets then feed it back into the AI 

## What it does?

Use it here, [Normalize employee health insurance tables](https://table-normalizer.streamlit.app).

- you upload a table and fix the AI transform errors
- your fix of each error must include a better field mapping rationale or
  value transform rationale
- your better rationales are then fed back into the AI system


## Zero specified three requirements.

- [x] Code on GitHub [this repo]
- [x] An interface in which you can perform such an operation. Place the interface in the
public domain for testing work. [see here](https://table-normalizer.streamlit.app/)
- [x] thoughts on edge cases and how they can be overcome (table below)

### Edge cases table


| Edge case                                             |  Future Solution      |
--------------------------------------------------------|-----------------------|
| different departments have contradictory rationales   | `rationales` per dept. |             
| if no days are greater than 12 we cant distinguish month and day | assume USA until otherwise, log & report |
| what if no columns match?                             | log & report |  
| Bad data: different names on same row                 | log & report |
| Annual or quarterly unit costs                        | text similarity to select prompt examples | 
| foreign language words and styles (names, etc)        | text similarity to select prompt examples |        
| prompt grow in size exceeding LLM's limit             | text similarity to select prompt examples |        
| one column is composite of two columns                | design a secondary prompt to handle ambiguous issue w/ composite examples and rationales |
| new rationale contradicts existing one                | run test transform on past inputs of high similarity; use LLM to predict conflict diff; use LLM to solve conflict diff| 

## Most important design feature

The examples will continually be improved upon by the user feedback corrections
and rationales so that the LLM's predictions will continually improve. 

Tech note: To bootstrap the "retraining" process the developer has created two initial sets of example
transforms by using two rows from `table_A.csv` and `table_B.csv` files. 


## Design rationale

The problem is that we know very little about the customer's transform
expectations and data. The first step to attack this problem is to experiment
with a process to accelerate how we learn about the customer's transform
expectations and data, ie. a tool that puts both of the customer's assumptions and our assumptions to
the test. In this line of attack, the intention of this prototype is to capture
the customer's transform expectations as corrections and rationales and feed it
into the AI system.

- Prioritize feedback loop over transform logic. We need customer input before we can optimize transform logic. We need ground
truth.
- Prioritize natural language rationales over code. Maintaining rationales in the customer's natural language is cheaper than
maintaining code for both the developer and the customer. 


### Assumptions

- The objective of the app is to reduce customer toil around manually
  normalizing the table.
- The business objective of our company is to deliver a valuable app with low cost
  (risk, time, maintenance).
- The customer does not currently understand what is feasible or what her
  transform expectations are.
- Its cheaper and OK with the customer to add requirements as the tool breaks
  rather than over-engineer the requirements in fear of upsetting the customer.


### Zero's suggested approaches

These were accepted.

- normalize col names - yes 
- normalize value formats - yes

The rest of Zero's suggestions were not accepted.

#### Manual template bootstrap

- **Zero's suggestion:** *upload template* 
- **Rationale for not accepting:** Here we bootstrap the transform system by having the developer analyze the
template table to make the initial rationales.
This is cheaper.

#### drop irrelevant columns

- **Zero's suggestion:** *drop irrelevant columns*
- **Rationale for not accepting:** These columns might be needed in the future,
  especially in case the LLM or user picked the wrong column. Furthermore, we
  are expecting the LLM to use these extra columns as context to generate
  associations with style and language to make the completion.

#### Ambiguous columns

- **Zero's suggestion:** *system asks user to decide between two potential col matches* 
- **Rationale for not accepting:** Its cheaper if we let the LLM decide, and then
capture the mistake if its wrong as a new user rationale. Furthermore, one column might end up being
the compound of two or more columns. For example a full name could be the
compound of three columns, first, last, and middle.

#### Code

- **Zero's suggestion:** *auto-generate code or pseudocode user checks.* 
- **Rationale for not accepting:** Its cheaper for both the user and developer to
  handle natural language transform rationales than code. Furthermore code is
  more brittle. When scope increases to handle large files we will then need to
  generate code. At this juncture we are just trying to capture customer
  feedback to see if we are on the right track.

### Summary of Zero's suggestions

| Zero's suggestion                           | Implementation                      |
----------------------------------------------|-------------------------------------|
| user loads template                         | developer does manual analysis      |
| user views candidate col matches & rationale| LLM guesses, user corrects          |
| user confirm of col match triggers transform| LLM guesses, user corrects          |
| user confirms/edits transform logic         | user updates rationales, not code   |
| EXTRA: retrain w/ user correction feedback  | Backend retrain partially done, UI bugs, ran out of time.           |
| EXTRA: retrain w/ synthetic tables          | ran out of time                     |


### Zero's user journey

- User: upload template table of examples
- App: LLM summarizes columns as a description
- User: upload table
- App: LLM generates transform code
- User: correct LLM's transform code
- App: Execute code
- User: validate transform is correct

### Boris's user journey

- User: hand template table of examples to developer
- Developer: template table examples -> Developer analysis -> initial `rationales`
- User: upload table 
- App: raw table + `examples` and `rationales` -> LLM -> transformed table 
- User: fixes AI prediction will update the table of `examples` and
  `rationales`, and update the prompt
- App: test new rationales gives same output on historic data [future]

