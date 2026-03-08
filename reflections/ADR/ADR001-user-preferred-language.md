### Title
ADR001: Store user preferred language in DB

### Date
2026-03-04

### Status
Proposed

### Context
We are going to add i18n and l10n support to this app. There will be translations added for supporting at least two languages (English `en-CA` and Chinese `zh-CN`). We need a way of determing and keeping track of user's preferred language. 

### Decision
Store user's preferred language in DB users table and let it be part of the user's profile. Use Varchar column to store language code like 'en-CA' (ISO 639-1 + ISO 3166-1). Use accept-language header to detect the user's preferred language for first-time users. User can always change their preferred language through the app and this will update their profile. 

### Alternatives
- Store user's preferred language in local storage. 
  Pros: No need for migration. 
  Cons: The preferrence will get cleared when browser data (local storage) is cleared, and the user will have to choose again if the preferred language is different thant what the accept-language header specifies. 
- Language-Specific Subdirectories: Use URLs like example.com/en/ or example.com/fr/. 
  Pros: If this is a public webpage it will be sharable while maintaing the preferred language.
  Cons: This parttern does not work very well since this is an SPA. And This is a user based application so it is not used for sharing links.
- Only rely on accept-language headers:
  Pros: No need for migration. Handled by browser.
  Cons: Cannot provide custom settings for preferred language. 


### Consequences
- Requires database migration to add `preferred_language` column to users table.
- API responses should include user's preferred language
- Frontend needs to respect and allow changing this preference
- Fallback to accept-language header when user preference is null

### Edge Cases
- Existing users:
  Since existing users do not have preferred language, automatically detect it from accept-language header and set it on first request after we starting supporting language. 
- What happens if accept-language header is missing:
  Default to 'en-CA'
- How to handle unsupported languages:
  We will only support English(en-CA) and Chinese(zh-CN). Any other will default to en-CA. 
- How to handle same language different region:
  If the browser sends en-US. We will use the best match (which is en-CA).