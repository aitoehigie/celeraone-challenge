# encoding: utf8
#
# Author: Felipe Godói Rosário - 17/11/2016
# This code creates a small uWSGI application called GitHub navigator that 
# searches GitHub repositories by given search term and present them as html page

#!flask/bin/python

import os, sys
import logging, logging.handlers, ConfigParser, argparse, ssl
import json
import urllib
from datetime import datetime

from flask import Flask, redirect, request, render_template

if __name__=='__main__':
    try:
        # Configuration of command line arguments
        parser = argparse.ArgumentParser(description='Searches GitHub \
            repositories by given search term and present them as html page')
        parser.add_argument('-i', '--ip', help='ip address of the server', 
            dest='ip', default='0.0.0.0')
        parser.add_argument('-p', '--port', help='port of the server', 
            dest='port', default=8080, type=int)
        args = vars(parser.parse_args())
        
        app = Flask(__name__)

        @app.route('/navigator', methods=['GET'])
        def navigator():
            try:
                service_url = 'https://api.github.com/search/repositories?'
                search_term = request.args.get('search_term', '')
                if len(search_term) > 0:
                    url = service_url + urllib.urlencode({'q': search_term})
                    uh = urllib.urlopen(url)
                    data = uh.read()

                    try: js = json.loads(str(data))
                    except: js = {}
                    
                    if 'items' not in js:
                        return "Error accessing Github API"
                    
                    items = js['items']
                    items.sort(key=lambda x: x['created_at'], reverse=True)
                    items = items[:5]
                    
                    for i in range(len(items)):
                        items[i]['order'] = i + 1
                        items[i]['created'] = datetime.strptime(items[i]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                        
                        try:
                            commit_url = 'https://api.github.com/repos/' + \
                                items[i]['owner']['login'] + '/' + \
                                items[i]['name'] + '/commits'
                            uh = urllib.urlopen(commit_url)
                            data = uh.read()
                            commit_js = json.loads(str(data))
                            last_commit = commit_js[0]
                            items[i]['last_commit'] = last_commit
                        except:
                            items[i]['last_commit']['sha'] = 'Error retrieving last commit'
                    
                    return render_template('template.html', items=items,
                        search_term=search_term)
                else:
                    return "No search_term informed"
            except:
                return "Error accessing Github API"

        app.run(host=args['ip'], port=args['port'])
        
    except:
        sys.exit(str(sys.exc_info()[0]) + " - " + str(sys.exc_info()[1]) + " - " + str(sys.exc_info()[2]))