# Medicine Minder

Keep track of items having limited quantity or shelf life, and send a warning email if any are nearing expiry. The original use case is to monitor medications and warn if stock is getting low so that the prescription can be refilled in time.

The script runs a query to see if any medications are expiring soon. If so, it identifies who needs to be notified and generates an html report using ![Jinja](https://jinja.palletsprojects.com/en/2.11.x/). The report is then emailed automatically.

![sample notification email](images/sample_email.jpg)

## Medicine (Items to be tracked)
An SQLite database is used to keep track of each medicine, its expiry, and other details:
![sample notification email](images/medicine.jpg)

## Person (People to be notified for each item)
Users are defined in another table:
![sample notification email](images/person.jpg)

## Alarm Configuration
A linking table specifies which users needs to be notified for which medicine:
![sample notification email](images/alarm_configuration.jpg)


