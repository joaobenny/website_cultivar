# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
import calendar
import datetime

from odoo import http
from odoo.http import request


class WebsiteCultivar(http.Controller):

    @http.route('/page/homepage', type='http', auth="public", website=True)
    def cultivar_home(self, **post):

        events = request.env['event.event'].sudo().search([])

    # Calendar code #

        calendar.setfirstweekday(0)  # Monday, first day of the week
        months_name = ['JAN.', 'FEV.', 'MAR.', 'ABR.', 'MAIO.', 'JUN.',
                       'JUL.', 'AGO.', 'SET.', 'OUT.', 'NOV.', 'DEZ.']
        days_name = ["Segunda", "Terça", "Quarta",
            "Quinta", "Sexta", "Sábado", "Domingo"]
        today = datetime.datetime.date(datetime.datetime.now()) # Today (YYYY-MM-DD)
        current_date = re.split('-', str(today)) # YYYY-MM-DD -> [YYYY, MM, DD]
        current_month_id = int(current_date[1])  # Current month number (1-12)
        current_month = months_name[current_month_id-1]  # Current month name
        current_day = 30#int(current_date[2])
        current_year = int(current_date[0])

        # Month stores every week with respective days (0 = not month day)
        month = calendar.monthcalendar(current_year, current_month_id)
        
        ev_dates = []  # Stores all events dates (0- Date_begin, 1- Date_end, 2- Name)
        for e in events:
            DATE_FORMAT_STR = "%Y-%m-%d %H:%M:%S"
            ev_dates.append((datetime.datetime.strptime(e.date_begin, DATE_FORMAT_STR),
                             datetime.datetime.strptime(
                                 e.date_end, DATE_FORMAT_STR),
                             e.name))

        cal = [] # Stores 31 days info (0- Day, 1- Day Name, 2- Events, 3- Month Number, 4- Month Name, 5- Year)
        first_skip = False # Bool to check if calendar started from current day
        while len(cal) < 31:
            for w in xrange(0, len(month)):
                week = month[w]
                for d in xrange(0, 7):
                    day = week[d]
                    if day < current_day and first_skip == False: # Continue if day is before current day
                        continue
                    elif day != 0 and len(cal) < 31: # Adds day to cal[] if cal doesn't has 31 days
                        if days_name[d] != "Sábado" or days_name[d] != "Domingo":
                            cal.append([day, days_name[d], "", current_month_id, current_month,
                             current_year, "diadasemana"])
                        else:
                            cal.append([day, days_name[d], "", current_month_id, current_month,
                             current_year, "fimdesemana"])
                        first_skip = True # Current day already added
            if current_month_id == 12: # If it's the last month then jumps to next year
                current_year += 1
                current_month_id = 0
            # Jumps to the next month every time the month ends and cal length < 31
            month = calendar.monthcalendar(current_year, current_month_id+1)
            current_month = months_name[current_month_id]
            current_month_id += 1

        # Set events to all days shown (website: always shows current day + 30 days)
        for i in cal:
            for e in ev_dates:
                if (i[0] >= e[0].day and i[0] <= e[1].day) and (i[3] == e[0].month and i[5] == e[0].year):
                    e_name = e[2]
                    # If statement to add all events that day has
                    if i[2] == "":
                        i[2] = e_name
                        continue
                    else:
                        i[2] += ", " + e_name

        c_day = cal[0] # Stores current day info from cal[]
        del cal[0] # Deletes current day from calendar

    # End of Calendar Code #

        return request.render("website.homepage", {'events': events, 'calendar': cal, "today": c_day})
