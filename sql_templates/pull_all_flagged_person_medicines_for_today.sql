-- pull full set of reports for all flagged Person
select pers.nameFirst, pers.nameLast, pers.email
, alarm.idPerson, med.name, med.expiry, med.type
, coalesce(med.brand, '') as Brand
, coalesce(med.serialNumber, '') as SerialNumber
, alarm.daysWarning

--todo - still not quite right. If run after noon, goes to the *next* julian day
--being 12PM noon based means a standard midnight-based calendar day crosses *two* julian day
--would need further tweaking, but did not bother for now (assume we always run this in morning)

--NOTES:
-- (1) expiry would have been specified in localtime, so need to do same for current time (which is otherwise UTC);
-- (2) +0.5 on dates because Julian days do not count from midnight, but from noon https://stackoverflow.com/a/38284918/2683104
-- (3) +1 at end of calculation because we want the interval, *including* today (e.g. 10 day - 1 day = 9 day. But we want to include the first day, so add 1 more.)
, cast(
      julianday(med.expiry)                               -- Note: 1
    - (cast(julianday('now','localtime') as int) + 0.5)   -- Note: 1, 2
    + 1                                                   -- Note: 3
as int) as daysToExpiry

, case
    -- cast to int forces flooring / round down (i.e. conservative)
    when cast( julianday(med.expiry) - (cast(julianday('now','localtime') as int) + 0.5) + 1 as int ) <= 0 then '**EXPIRED**'
    when cast( julianday(med.expiry) - (cast(julianday('now','localtime') as int) + 0.5) + 1 as int ) <= alarm.daysWarning then 'warning'
    when cast( julianday(med.expiry) - (cast(julianday('now','localtime') as int) + 0.5) + 1 as int ) >= 0 then 'OK'
    else 'unknown'
end as medicineState

from Medicine med

join Person pers
on pers.Id = alarm.IdPerson
and LOWER(pers.enabled) = 'true'

join AlarmConfiguration alarm
on alarm.idMedicine = med.Id
and alarm.idPerson in (
    select distinct alarm.IdPerson
    from AlarmConfiguration alarm
    join Medicine med
    on med.Id = alarm.IdMedicine
    and LOWER(med.enabled) = 'true'
    where LOWER(alarm.enabled) = 'true'
    and DATE('now', alarm.daysWarning||' day') >= med.expiry
    order by alarm.IdPerson, alarm.IdMedicine, alarm.IdAlarm
)

where lower(med.enabled) = 'true'
order by alarm.idPerson, daysToExpiry, med.name