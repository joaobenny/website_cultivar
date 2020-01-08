# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
import calendar
import datetime
import requests
from datetime import date
import werkzeug
import json
#import pygeoip

from odoo import http
from odoo.http import request


class WebsiteCultivar(http.Controller):
    @http.route('/page/homepage', type='http', auth="public", website=True)
    def cultivar_home(self, **post):
        events = request.env['event.event'].sudo().search([]) # Gets all events on database
        posts = request.env['blog.post'].sudo().search([]) # Gets all posts on database   
        ip = requests.get('http://ip.42.pl/raw').text
        
        #ip = request.httprequest.environ["REMOTE_ADDR"] # Gets client IP
       # if ip == "127.0.0.1": # If running on server
          #  ip = "auto:ip"
           # print ("\nClient IP: Local Host\n")
       # else:
           # print ("\nClient IP: " + ip) 
 
        ip_url = "http://api.ipstack.com/"+ip+"?access_key=0fd42ce53c04501a1881ffd8bc9c00c0"
        reply_ip = requests.get(ip_url)
        ip_content = reply_ip.json()
        lat = ip_content["latitude"]
        lon = ip_content["longitude"]
   
        api_key = "0a9f4d7f438a0ccd2bbe98e8ae6d7b30"        
        #api_key = "b58a7a944556a73bd18f96fce1c44bdb"
        #url = "https://api.apixu.com/v1/forecast.json?key={0}&q={1}&days=7".format(api_key, ip)
        #url = "http://api.openweathermap.org/data/2.5/forecast?q=Fundão,pt&appid=36d4ffcd46186c2b0dc224fa7bb109d8&units=metric"
        #url = "https://api.darksky.net/forecast/0a9f4d7f438a0ccd2bbe98e8ae6d7b30/40.1408,-7.5018?units=si"
        url = "https://api.darksky.net/forecast/"+api_key+"/"+str(lat)+","+str(lon)+"?units=si"
        reply = requests.get(url)
        reply.raise_for_status()
        content = reply.json()
        weather = content["daily"]
        print ("Weather API Status Code: {}".format(reply.status_code))
	     #print ("Client Location based on its IP in the API: {}".format(ip_content["city"]))
        #print ("Client Location based on its IP in the API: {}".format(content["latitude"]["longitude"]))
        print ("\n\n")

    # Calendar code #

        calendar.setfirstweekday(0)  # Monday, first day of the week
        months_name = ['JAN.', 'FEV.', 'MAR.', 'ABR.', 'MAIO.', 'JUN.',
                       'JUL.', 'AGO.', 'SET.', 'OUT.', 'NOV.', 'DEZ.']
        days_name = ["Segunda", "Terça", "Quarta",
            "Quinta", "Sexta", "Sábado", "Domingo"]
        today = datetime.datetime.date(datetime.datetime.now()) # Today date (YYYY-MM-DD)
        current_date = re.split('-', str(today)) # YYYY-MM-DD -> [YYYY, MM, DD]
        current_month_id = int(current_date[1])  # Current month number (1-12)
        current_month = months_name[current_month_id-1]  # Current month name
        current_day = int(current_date[2])
        current_year = int(current_date[0])

        # Month stores every week with respective days (0 = not month day)
        month = calendar.monthcalendar(current_year, current_month_id)
        
        ev_dates = []  # Stores all events dates (0- Date_begin, 1- Date_end, 2- Name)
        date_format = "%Y-%m-%d %H:%M:%S"
        for e in events:
            conv_begin = datetime.datetime.strptime(e.date_begin, date_format)
            conv_end = datetime.datetime.strptime(e.date_end, date_format)
            start = date(conv_begin.year, conv_begin.month, conv_begin.day)
            end = date(conv_end.year, conv_end.month, conv_end.day)
            ev_dates.append((start, end, e.name, e.id))

        # Function to return calendar day moon phase
        def moon_phases(day, month, year):
            ages = [18, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7]
            offsets = [-1, 1, 0, 1, 2, 3, 4, 5, 7, 7, 9, 9]
            all_phases = ["Lua nova", "Lua crescente", "Quarto crescente", "Lua crecente convexa",
                            "Lua cheia", "Lua minguante convexa", "Quarto minguante", "Lua minguante"]
            if day == 31:
                day = 1
            days_into_phase = ((ages[(year + 1) % 19] + ((day + offsets[month-1]) % 30) + (year < 1900)) % 30)
            i = int((days_into_phase + 2) * 16/59.0)
            if i > 7:
                i = 7
            phase = all_phases[i]
            
            return phase

        cal = [] # Stores 31 days info (0- Day, 1- Day Name, 2- Events, 3- Month Number, 4- Month Name,
        # 5- Year, 6- Weekday or Weekend, 7- Events ID, 8- Min Temp, 9- Max Temp, 10- Weather Icon)
        first_skip = False # Bool to check if calendar started from current days
        while len(cal) < 31:
            for w in xrange(0, len(month)):
                week = month[w]
                for d in xrange(0, 7):
                    day = week[d]
                    if day < current_day and first_skip == False: # Continue if day is before current day
                        continue
                    elif day != 0 and len(cal) < 31: # Adds day to cal[] if cal doesn't has 31 days
                        if days_name[d] == days_name[5] or days_name[d] == days_name[6]:
                            cal.append([day, days_name[d], "", current_month_id, current_month,
                             current_year, True, "-1",
                             "", "", "", moon_phases(day,current_month_id,current_year)])
                        else:
                            cal.append([day, days_name[d], "", current_month_id, current_month,
                             current_year, False, "-1",
                             "", "", "", moon_phases(day,current_month_id,current_year)])
                        first_skip = True # Current day already added
            if current_month_id == 12: # If it's the last month then jumps to next year
                current_year += 1
                current_month_id = 0
            # Jumps to the next month every time the month ends and cal length < 31
            month = calendar.monthcalendar(current_year, current_month_id+1)
            current_month = months_name[current_month_id]
            current_month_id += 1

        # Set events to all days shown (website: shows current day + 30 days)
        for i in cal:
            day_date = date(i[5], i[3], i[0])
            for e in ev_dates:
                if  e[0] <= day_date <= e[1]:
                    e_name = e[2]
                    # If statement to add all events names and IDs that day has
                    if i[2] == "":
                        i[2] = e_name
                        i[7] = e[3]
                        continue
                    else: # days with >1 event, separates names with ,
                        i[2] += ", " + e_name
                        i[7] = str(i[7]) + "-" + str(e[3])
        
        # Set Weather Information for first 7 days
        for i in xrange(0,7):
	         #cal[i][8] = int(round(weather[i]["day"]["mintemp_c"]))
            #cal[i][9] = int(round(weather[i]["day"]["maxtemp_c"]))
            #cal[i][10] = weather[i]["day"]["condition"]["icon"]
            cal[i][8] = int(round(weather['data'][i]['temperatureMin']))
            cal[i][9] = int(round(weather['data'][i]['temperatureMax']))
            cal[i][10] = weather["data"][i]["icon"]


        c_day = cal[0] # Stores current day info from cal[]
        del cal[0] # Deletes current day from calendar

    # End of Calendar Code #

        return request.render("website.homepage", {'events': events, 'calendar': cal, "today": c_day, "posts": posts})

    @http.route(['/event/<model("event.event"):event>/register'], type='http', auth="public", website=True)
    def event_register(self, event, **post):
        allevents = request.env['event.event'].sudo().search([])
        events = []
        for ev in allevents:
            if ev.date_begin > event.date_begin:
                events.append(ev)
                if len(events) >= 20:
                    break
        values = {
            'event': event,
            'main_object': event,
            'range': range,
            'registrable': event.sudo()._is_event_registrable(),
            'events': events
        }
        return request.render("website_event.event_description_full", values)

    # Event Inquiry "Main Page", this def is to render page (and send data to xml)
    @http.route('/event/inquiry', type='http', auth="public", website=True)
    def event_inquiry(self, **kwargs):
        # states = request.env['res.country.state'].search([])
        products_type = request.env['event.product.type'].sudo().search([('parent_id', '=', False)])
        product = request.env['event.product'].sudo().search([])
        partner_type = request.env['res.partner.type'].sudo().search([])
        event_type = request.env['event.type'].sudo().search([])
        periodo = request.env['event.recurrence'].sudo().search([])
        distritos = request.env['res.country.state'].sudo().search([('country_id', '=', 185)])
        concelhos = request.env['res.county'].sudo().search([])
        freguesia = request.env['res.county.local'].sudo().search([])
        
        return http.request.render('website_cultivar.event_inquiry', {
            'products_type': products_type,
            'products': product,
            'partner_type': partner_type,
            'event_type': event_type,
            'periodo': periodo,
            'distritos': distritos,
            'concelhos': concelhos,
            'freguesias': freguesia
        })

    # Event Inquiry Process (send data to database)
    @http.route('/event/inquiry/process', type='http', auth="public", website=True)
    def event_inquiry_process(self, **kwargs):
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value

        # Verify if new register hasn't an used email
        if request.env['res.users'].sudo().search_count([('login','=', values['email'])]) > 0:
        
            mail = values['email']
            return http.request.render('website_cultivar.event_inquiry_error', {'mail': mail} )

        # Adds new user to DB, else:
        new_user = http.request.env['res.users'].sudo().create({'name': values['entidade_nome'], 'login': values['email'], 'email': values['email'], 'password': values['password']})

        # # Add the user to the company group
        # company_group = request.env['ir.model.data'].sudo().get_object('website_cultivar', 'company_group')
        # company_group.users = [(4, new_user.id)]

        # Remove 'Contact Creation' permission        
        contact_creation_group = request.env['ir.model.data'].sudo().get_object('base', 'group_partner_manager')
        contact_creation_group.users = [(3,new_user.id)]

        # Also remove them as an employee
        human_resources_group = request.env['ir.model.data'].sudo().get_object('base', 'group_user')
        human_resources_group.users = [(3,new_user.id)]

        # Modify the users partner record, state_id': values['state'],
        new_user.partner_id.write({'name': values['entidade_nome'], 'street': values['entidade_endereco'],
         'zip': values['entidade_zip'], 'city': values['entidade_localidade'], 'state_id': values['entidade_distrito'],
         'partner_type': values['entidade_tipo'], 'concelho': values['entidade_concelho'], 'freguesia': values['entidade_freguesia']})
         # '': values['entidade_freguesia'], '':['entidade_concelho']

        if 'pessoa_nome' in values:
            insert_pessoa = {'parent_id': new_user.partner_id.id}
            insert_pessoa['name'] = values['pessoa_nome']
            if 'pessoa_tel' in values: insert_pessoa['phone'] = values['pessoa_tel']
            if 'pessoa_email' in values: insert_pessoa['email'] = values['pessoa_email']        
            new_contact = request.env['res.partner'].sudo().create(insert_pessoa)

        if 'evento_local' in values:
            insert_local = {'parent_id': new_user.partner_id.id}
            insert_local['city'] = values['evento_local']
            insert_local['type'] = "other" # Partner type: Other address
            if 'evento_distrito' in values: insert_local['state_id'] = values['evento_distrito']
            if 'evento_concelho' in values: insert_local['concelho'] = values['evento_concelho']
            if 'evento_freguesia' in values: insert_local['freguesia'] = values['evento_freguesia']        
            event_local = request.env['res.partner'].sudo().create(insert_local)

        insert_event = {'address_id': event_local.id, 'organizer_id': new_user.partner_id.id}

        if 'evento_nome' in values: insert_event['name'] = values['evento_nome']
        if 'date_begin' in values: insert_event['date_begin'] = values['date_begin']
        if 'date_end' in values: insert_event['date_end'] = values['date_end']
        if 'evento_edicao' in values: insert_event['e_anos'] = values['evento_edicao']
        if 'evento_descricao' in values: insert_event['description'] = values['evento_descricao']
        if 'evento_tipo' in values: insert_event['event_type_id'] = values['evento_tipo']
        if 'is_recurrent' in values: insert_event['recurrent'] = values['is_recurrent']
        if 'evento_perio' in values: insert_event['recurrence_id'] = values['evento_perio']
        
        # Extra data
        insert_event['website_published'] = True # Makes event visible on /events
        
        new_listing = request.env['event.event'].sudo().create(insert_event)

        return http.request.render('website_cultivar.event_inquiry_success')
