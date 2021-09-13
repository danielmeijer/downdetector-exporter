import time
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import requests
from bs4 import BeautifulSoup
import hjson
import os
import re

class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        html = requests.get(os.environ['downdetector_url'])
        soup = BeautifulSoup(html.text, 'html.parser')

        # GET SCRIPT WHERE DATA IS LOCATED
        raw_output = soup.find('script', text = re.compile('window.DD.chartTranlations*'), attrs = {'type' : 'text/javascript'})
        raw_output = raw_output.extract

        # CLEAR VARIABLE TO OUTPUT ONLY JSON
        downdetector_json = str(raw_output).split("window.DD.currentServiceProperties =")
        downdetector_json = downdetector_json[1]
        # REMOVE SCRIPT TAG
        downdetector_json = str(downdetector_json).split("</script>")
        downdetector_json = downdetector_json[0]
        # CLEAR JSON
        downdetector_json = downdetector_json.replace("\'", "\"") # replace single quotes in string for double quotes (fixes mixed quotes in output)
        
        parsed_json=hjson.loads(downdetector_json)

        print("Downdetector status for : "+ os.environ['downdetector_url'] + " is " + parsed_json["status"])

        ### STATUS ###

        if parsed_json["status"] == "success": 
            downdetector_current_status="0"  
        elif parsed_json["status"] == "warning":
            downdetector_current_status="1"
        else: 
            downdetector_current_status="2"

        downdetector_status = GaugeMetricFamily("downdetector_status", 'Shows if downdetector consider the service down.')
        downdetector_status.add_metric(["status"], downdetector_current_status)
        yield downdetector_status

        ### MIN and MAX baseline ###
        
        downdetector_max_baseline = GaugeMetricFamily("downdetector_max_baseline", 'Max baseline for Downdetector')
        downdetector_max_baseline.add_metric(["max_baseline"], parsed_json["max_baseline"])
        yield downdetector_max_baseline

        downdetector_min_baseline = GaugeMetricFamily("downdetector_min_baseline", 'Min baseline for Downdetector.')
        downdetector_min_baseline.add_metric(["min_baseline"], parsed_json["min_baseline"])
        yield downdetector_min_baseline


        ### INFORMS ###
        downdetector_informs = GaugeMetricFamily("downdetector_informs", 'Informs received from Downdetector.')
        downdetector_informs.add_metric(["downdetector_informs"], parsed_json["series"]["reports"]["data"][-1]["y"])
        yield downdetector_informs


        # TODO: Convert date to POSIX Time Format
        # downdetector_informs_date = GaugeMetricFamily("downdetector_informs", 'Date extrations.')
        # downdetector_informs_date.add_metric(["downdetector_informs_date"],parsed_json["series"]["reports"]["data"][-1]["x"])
        # yield downdetector_informs_date

        ### CURRENT EXPECTED BASELINE ###

        downdetector_baseline = GaugeMetricFamily("downdetector_baseline", 'Baseline received from Downdetector.')
        downdetector_baseline.add_metric(["downdetector_baseline"], parsed_json["series"]["baseline"]["data"][-1]["y"])
        yield downdetector_baseline


if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(CustomCollector())
    while True:
        time.sleep(1)
