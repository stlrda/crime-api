# crime-api

This repository is still in development, but contains the neccessary containers to routinely extract SLMPD crime data and serve it from the same database.

API can be accessed from http://api.stldata.org (You will automatically be redirected to documentation)

Legacy Endpoints will be deprecated in a future release; Currently used to power http://app.stldata.org.

> More details will follow soon.

## Valid Crime Categories
For the current endpoints, these categories (case-insensitive) are supported for queries requesting `category`:
```
 Fraud
 Simple Assault
 Loitering/Begging
 Arson
 Offense Against Family
 Sex Offense
 DWI/DUI
 Forgery
 Disorderly Conduct
 Embezzlement
 Aggravated Assault
 Robbery
 Other
 Stolen Property
 Burglary
 Weapons Offense
 Rape
 VMCSL
 Vehicle Theft
 Larceny
 Destruction of Property
 Liquor Laws
 Homicide
```
