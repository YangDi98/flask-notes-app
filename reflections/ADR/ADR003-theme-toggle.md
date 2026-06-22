### Title
ADR003: Theme Toggle
### Date
2026-06-21

### Status
Proposed

### Context
I would like to add a theme toggle for my notes app. There are a few decisions to make:  
- System prefers-color-scheme detection vs explicit user toggle? 
- Store preference in localStorage vs backend profile? 
- How to avoid flash of wrong theme on load?

### Decision
- Detect system preferred color scheme to display the theme if the user does not manually toggle another theme. 
- Store theme preference in localStorage if there the user chooses a theme. 
- To avoid flashing wrong theme on load, do not display the frontend until the theme is retrieved from localStorage or confirmed it is not there. Block inline `<script>` in `index.html` `<head>`. Do not use v-if on App because the user will see blank white screen and then corrct theme. Script runs before the browser paints anything at all. 
- Theme fallback order: localStorage -> system settings -> default

### Alternatives
- We can also store theme preference in the database. However this will require a migration (add a column to a table), and updating the theme will require a API call which can fail. Since this is a less important feature, localStorage is acceptable. 
- No system color scheme detection: this is acceptable too but nice to have. 

### Consequences
- Theme preference will be lost if user clears localStorage. This is acceptable for this feature. 

