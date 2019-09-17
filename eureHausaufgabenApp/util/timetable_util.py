from FetchUnits import Units
from FetchUnits import JsonPlanParser
from threading import Thread
import os

"""
def get_closest_subject_day_string(save_file, Subject):
    plan_parser = JsonPlanParser(save_file)
    subject_json = plan_parser.get_subject_json(Subject, onlyNotDone=True)
    full_subject_json = JsonPlanParser.remove_empty_days(subject_json)
    for week in full_subject_json:
        if len(week) > 0:
            return week[list(week.keys())[0]]["lessons"][0]["time"]["date"]
"""

"""
def get_time_table_download_info(save_file):
    temp_file_path = "{}.temp".format(save_file)

    if os.path.isfile(save_file):
        return "DONE"
    elif os.path.isfile(temp_file_path):
        temp_file_text = open(temp_file_path, mode="r").read()
        return temp_file_text
"""

"""
def get_time_table(units_school_name, user_name, user_password, save_file):
    units = Units(username=user_name, password=user_password, shool=units_school_name, head_less=True, detailed=True, class_plan=True ,debug_file_out="{}.temp".format(save_file))
    t = Thread(target=__get_and_save_time_table, args=[units, save_file, ])
    t.start()
    return


def __get_and_save_time_table(units : Units, save_file):
    temp_file_path = "{}.temp".format(save_file)
    try:
        units.get_data(debug=True, week_count=2)
    except Exception as e:
        temp_file = open(temp_file_path, mode="w")
        temp_file.write("Error : " + str(e))
        temp_file.close()
        raise e
    units.parse_plan(save=True, save_file=save_file, auto_kill=True, delete_log=True, debug=True)
    try:
        units.browser.quit()
    except:
        pass
    if os.path.isfile(save_file):
        os.remove(save_file)
    os.remove(temp_file_path)
"""