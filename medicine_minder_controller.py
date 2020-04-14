import sys
sys.dont_write_bytecode = True
import datetime as dt
from itertools import izip, groupby
import collections
import traceback
from jinja2 import Environment, FileSystemLoader

import generate_medicine_minder_reports
import data_handlers.emailmanager as emailmanager



def format_iso_date_string(iso_date):
    try:
        iso_in_datetime = dt.datetime.strptime(iso_date, '%Y-%m-%d')
        return iso_in_datetime.strftime('%Y-%b-%d')
    except:
        return iso_date


def render_a_report_to_html_via_jinja(report_data, template_filename):
    file_loader = FileSystemLoader('html_templates')
    env = Environment(loader=file_loader)
    env.filters['format_iso_date_string'] = format_iso_date_string
    template = env.get_template(template_filename)
    template.globals['now'] = dt.datetime.utcnow
    html = template.render(report_data)
    return html


def group_flagged_medicines_by_person(all_flagged_medicines):
    if not all_flagged_medicines:
        # empty dataset (no flagged names today)
        return

    header = all_flagged_medicines[0]
    data = all_flagged_medicines[1:]
    all_flagged_medicines_dict = [ dict(izip(header, d)) for d in data ]

    # https://stackoverflow.com/questions/16176469/how-do-i-group-this-list-of-dicts-by-the-same-month
    # https://stackoverflow.com/questions/51060140/itertools-group-by-multiple-keys
    grouping_key = ['IdPerson','Email','NameFirst','NameLast']
    group_medicine_by_person = groupby( all_flagged_medicines_dict, key=lambda x:tuple(x[k] for k in grouping_key) )

    group_medicine_by_person_list_of_dict=[]
    for k, v in group_medicine_by_person:
        dict_temp = dict(izip(grouping_key, k))
        dict_temp['medicine_set']=list(v)
        group_medicine_by_person_list_of_dict.append(dict_temp)
    return group_medicine_by_person_list_of_dict


def main(debug=True):
    print 'SUCCESS: started Medicine Minder alarm processing'

    try:
        minder = generate_medicine_minder_reports.Medicine_Minder_Report_Manager()
        all_flagged_medicines = minder.pull_all_flagged_person_medicines_for_today()
        if all_flagged_medicines:
            print 'SUCCESS: extracted all the flagged reports (%i data records)' % ( len(all_flagged_medicines)-1 )
        else:
            print 'SUCCESS: process ran successfully, but no reports were flagged today'
            return

        today_flagged_medicine_grouped_dataset = group_flagged_medicines_by_person(all_flagged_medicines)
        print 'SUCCESS: grouped dataset for Jinja rendering'

        html_set = []
        for report_data in today_flagged_medicine_grouped_dataset:
            html_set.append( (report_data['Email'], render_a_report_to_html_via_jinja(report_data, template_filename='medicine_report_for_person.html')) )
            print 'SUCCESS: generated new report for user "%s"' % ( report_data['IdPerson'] )
    except Exception as e:
        print 'ERROR: encountered issues generating reports. Returning early.'
        print e
        print traceback.format_exc()
        return

    if not debug:
        try:
            smtpServer = emailmanager.connect_to_gmail_smtp()
            print 'SUCCESS: connected to smtp email server'
        except:
            print 'ERROR: cannot setup smtpServer. Will not be able to send any emails. Exiting...'
            sys.exit(0)
    else:
        print 'WARNING: debug mode is enabled - will not connect to smtp or send live emails'

    try:
        subject='Expiring Medication Warning from Medicine Minder'
        message=subject

        for recipient, html_content in html_set:
            if not debug:
                emailmanager.send_html_email_via_smtp(
                      subject
                    , message
                    , recipientList=[recipient]
                    , fromEmail='example_from_user@gmail.com'
                    , smtpServer=smtpServer
                    , ccList=[]
                    , attachmentPaths=[]
                    , message_html=html_content
                )
                #print 'SUCCESS: sent email to "%s"' % recipient
            else:
                print 'WARNING: did not attempt to send email to "%s" because debug mode is enabled' % recipient
                print html_content

    except Exception as e:
        error_subject = 'ERROR: failed to send Minder report'
        if not debug:
            emailmanager.send_html_email_via_smtp(
                  subject=error_subject
                , message='%s\n\n%s' % ( e, traceback.format_exc() )
                , recipientList=['example_email@gmail.com']
                , fromEmail='example_from_user@gmail.com'
                , smtpServer=smtpServer
                , ccList=[]
                , attachmentPaths=[]
                , message_html=None
            )
            print 'SUCCESS: sent an error email "%s" to "%s"' % (subject, recipientList)
        else:
            print 'WARNING: did not attempt send error email because debug mode is enabled'
        print error_subject
        print e
        print traceback.format_exc()

    finally:
        if not debug:
            emailmanager.disconnect_from_gmail_smtp(smtpServer)
            print 'SUCCESS: disconnected from smtp email server'


if __name__ == '__main__':
    #debug=False #uncomment to actually send emails
    try:
        main(debug)
    except:
        main() #default debug=True
    print 'done'
