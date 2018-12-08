"""Camera-related procedures"""
from .selenium import ChromeDriver, Action
from .path import Paths


p = Paths()

#creds = p.key_dict['webcam_api']

ip_list = [p.elutuba_ipc, p.garage_ipc, p.kamin_ipc]

ip = ip_list[0]


class AmcrestWeb:
    """Selenium-based controls for automating boring camera tasks"""
    def __init__(self, ip, creds, driver_path='/usr/bin/chromedriver'):
        self.ip = ip
        self.driver = ChromeDriver(driver_path)
        self.act = Action(self.driver)
        self.url = 'http://{}'.format(ip)
        self.creds = creds

    def login(self):
        # Load the website
        self.driver.get(self.url)
        # Login
        self.act.clear('//div/input[@id="login_user"]')
        self.act.enter('//div/input[@id="login_user"]', self.creds['user'])
        self.act.enter('//div/input[@id="login_psw"]', self.creds['password'])
        # Click login button
        self.act.click('//div/a[@id="b_login"]')

    def goto_motion(self):
        self.login()
        # Click the Setup tab
        self.act.click('//li[@id="tab_set"]/a')
        # Click the Event section
        self.act.click('//ul[@id="set-menu"]/li[@category="event"]/a')
        # Click the Video Detection section
        self.act.click('//li[@category="event"]/ul/li[@filename="videoDetectConfig"]/span')

    def goto_storage(self):
        self.login()
        # Click the Setup tab
        self.act.click('//li[@id="tab_set"]/a')
        # Click the Storage section
        self.act.click('//ul[@id="set-menu"]/li[@category="storage"]/a')
        # Click the Schedule section
        self.act.click('//li[@category="storage"]/ul/li[@filename="recordPlanConfig"]/span')

    def toggle_motion_detect(self, set_motion=None):
        self.goto_motion()

        if set_motion is not None:
            # We'll send some JavaScript to the browser to set the checkbox value
            checkbox_val = 'true' if set_motion else 'false'
            self.driver.execute_script("document.getElementById('v_m_enable').checked = {};".format(checkbox_val))
        else:
            # Toggle the "Motion Detect" Box
            self.act.click('//label[@class="ui-checkbox"]/input[@id="v_m_enable"]')
        # Click the Save button
        self.act.click('//div[@id="page_videoDetectConfig"]/div/div/div/a[text()="Save"]')

    def set_alert_schedule(self, sched_list):

        self.goto_motion()
        self.act.click('//div[@id="page_videoDetectConfig"]/div/div/div[label[text() = "Schedule"]]/a[text() = "Setup"]')
        day_btns = act.get_elem('//div[@class="ui-timeplan-button"]/a[text() = "Setup"]', single=False)
        sched_list = [
            {
                # Weekend
                'days': [0, 6],
                'times': ['0:00-03:50', '22:00-23:59']
            }, {
                # Weekdays
                'days': list(range(1, 6)),
                'times': ['0:00-03:50', '07:30-16:20', '22:00-23:59']
            }
        ]

        for sched in sched_list:
            days = sched['days']
            times = sched['times']
            for day in days:
                # Open the scheduling box for the given day
                day_btns[day].click


sched_list = [
    {
        # Weekend
        'days': [0, 6],
        'times': ['0:00-03:50', '22:00-23:59']
    }, {
        # Weekdays
        'days': list(range(1, 6)),
        'times': ['0:00-03:50', '07:30-16:20', '22:00-23:59']
    }
]

js = """
    function sleep(ms) {{
      return new Promise(resolve => setTimeout(resolve, ms));
    }}
    var sched_list = {};
    var time_fields = [0,2,4];
    var day_btns = document.getElementsByClassName('ui-timeplan-button')[2].getElementsByTagName('a');
    // For each item in schedule
    for (i=0; i<sched_list.length; i++) {{
        var sched = sched_list[i];
        var days = sched['days'];
        var times = sched['times'];
        var time_section = document.getElementsByClassName('ui-timesection')[2];
        var time_rows = time_section.getElementsByClassName('ui-form-item');
        // For each day in schedule
        for (j=0; j<days.length; j++) {{
            var day = days[j];
            console.log("Working on day: " + day);
            // Click the day button
            day_btns[day].click();
            await sleep(500);
            // First, set all times as false
            for (k=1; k<7; k++) {{
                time_rows[k].getElementsByTagName('label')[0].firstElementChild.checked = false;
            }}
            
            // Then, set the times we want to use
            for (k=0; k<times.length; k++) {{
                // Populate times
                var time_cnt = k + 1;
                if (time_cnt < 7) {{
                    var time_row = time_rows[time_cnt];
                    var time = times[k];
                    console.log("Adding time " + time);
                    var time_split = time.split("-");
                    // Check the period time
                    time_row.getElementsByTagName('label')[0].firstElementChild.checked = true;
                    
                    var start_div = time_row.getElementsByTagName('div')[0];
                    var end_div = time_row.getElementsByTagName('div')[1];
                    for (x=0; x<time_fields.length; x++) {{
                        var time_field_elem = start_div.children[time_fields[x]];
                        time_field_elem.focus();
                        await sleep(100);
                        if (x < 2) {{
                            time_field_elem.value = time_split[0].split(':')[x];
                        }} else {{
                            time_field_elem.value = "00";
                        }}
                        
                        var time_field_elem = end_div.children[time_fields[x]];
                        time_field_elem.focus();
                        await sleep(100);
                        if (x < 2) {{
                            time_field_elem.value = time_split[1].split(':')[x];
                        }} else {{
                            time_field_elem.value = "00";
                        }}
                         
                    }}
                    console.log("Appended times");
                    await sleep(1000)
                }}
            }}
        }}
    }}
""".format(sched_list)

print(js)