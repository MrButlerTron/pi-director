Some code I created with lots of help from chatgpt to director a browser to the defined Liftingcast page.
This is to be used in conjuction with local command line scripts which will use the operating systems hostname variable to pass the hostname of the computer to webserver.

The JSON file contains the meet URL for liftingcast, and then some arrays which will determine the URL passed back to the computer.

I have added a page split with 2 IFRAMES to handle situations where one computer/Pi is displaying 2 Boards.


This needs to be run with something that can serve Python Flask apps.

Copy pi.test.json to pi.json before running.
