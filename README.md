# chaven

Chaven is the starting point for all capsulers in armada. It is used to create 
accounts, add API keys and manage service access.

## Requirements

* PostgreSQL 9.4 or newer
* LDAP-compatible server like OpenLDAP or 389DS
 
## Security

API keys and CREST/ESI authentication tokens are stored encrypted in the 
database. This encryption only protects file-based access and not the runtime. 
Armada relies on continuous updating of a capsuler's data. To do that, API keys 
must be decryptable by the system, without user input. This is a tradeoff to 
on-demand refresh of data, where API keys can be encrypted by the user and only 
unlockable by the user. While on-demand supports better encryption, it 
severly limits the capabilities of the system and is detrimental to the user 
experience. 
