from app.extensions import socketio,client

# year (int | str) – 4-digit year
# month (int | str) – month (1-12)
# day (int | str) – day (1-31)
# week (int|str) – ISO week (1-53)
# day_of_week (int | str)-weekday number or name (0-6 or Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
# hour (int|str) – hour (0-23)
# minute (int|str) – minute (0-59)
# second (int|str) – second (0-59)
# start_date (datetime | str) – the earliest possible date / time (inclusive)
# end_date (datetime | str) – the latest possible date / time (inclusive)
# timezone (datetime.tzinfo | str) – time zone used for date / time calculation (default is the scheduler time zone)

def check_shift_plan():
    res = []
    list_users = []
    with client.app.app_context():
        list_shift_plan = client.db.shift_plan.find({})
        for shift_plan in list_shift_plan:
            if shift_plan["EmployeeIDs"]:
                list_users = shift_plan["EmployeeIDs"]
            if shift_plan["OrganizationUnitIDs"]:
                for org in shift_plan["OrganizationUnitIDs"]:
                    lst_user = client.db.user.find({"OrganizationUnitID":org})
                    if lst_user:
                        list_users = list(lst_user)
            item = {
                "RepeatConfig":shift_plan["RepeatConfig"],
                "users":list_users,
                "RepeatType":shift_plan["RepeatType"],
                "WorkingShiftIDs":shift_plan["WorkingShiftIDs"],
                "WorkingShiftNames":shift_plan["WorkingShiftNames"]

            }
            res.append(item)
    socketio.emit('schedule_shift_plan', res)
