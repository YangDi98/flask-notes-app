### Title
ADR004: Full-text Filter
### Date
2026-06-30

### Status
Proposed

### Context
Currently searching notes only search among titles. I would like to enable full-text search. There are a few decisions to make:  
- Filter on front end or backend?
- How to implement on the backend? Dynamically parsing the text on every query or creating a stored index column for the note content. 

### Decision
- Dynamically parsing the text on every query using the queries like the following example
```
  SELECT * 
FROM your_table_name 
WHERE to_tsvector('english', your_text_column) @@ to_tsquery('english', 'search_term');
```

- For now support English only. Postgresql does not have built-in dictionary support for Chinese. 


### Alternatives
- Use client-side filtering only. However this does not work well with our infinite scroll. 
- Creating a stored index column for the note content. This would be the standard production approach and it is very efficient and suitable for tables with a large number of rows. We will look into this in the future since it requires more learning and changes. For now we are just looking for a quick start. 
- Supporting mixed language. This will require creating a stored index column and we will look into this in the future. 

### Consequences
- This is only efficient enough for small tables with a few thousands of rows. Good enough for a quick start.
- This will support searching English notes only. It will fail to search correctly if the notes are in a different language. 