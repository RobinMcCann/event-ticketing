A small webapp built on Flask (Python) and PostgreSQL.


## Current functionality:
- User registation and login.
- Creating tickets with link, with 1-8 uses.
- Viewing tickets through link.
- Marking tickets as used.
- Tickets are used up after they are claimed enough times.
- Dashboard where user can choose to order tickets, view their ordered tickets and log out.
- User can change their password.
- Admin user which has extended privileges (created upon running the containeer setup)




## Coming:
- Option for user to change their email address
- Admin user functionality for managing users and tickets. (Currently none at all exist.)
- Nicer layout (maybe)

## To run the app:

Make sure you have docker installed. Clone the repo and run `docker-compose up`