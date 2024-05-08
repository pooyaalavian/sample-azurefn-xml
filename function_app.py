import azure.functions as func
import logging
import requests 
import json 
import os 
from src.xml_parser import text_to_xml
from src.bpmprocess_val import get_process

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def call_api(bpmstatus, pagenum, pagesize):
    res = requests.get(
        f"{os.getenv('XML_SERVER_URL')}?bpmstatus={bpmstatus}&pagenum={pagenum}&pagesize={pagesize}&format=xml",
        headers={ 'ApiKey': os.getenv('XML_SERVER_API_KEY') }
    )
    if res.status_code > 399:
        raise ValueError(
            "Error in Ivalua API: "+res.text,
        )
    return res.text

@app.route(route="values", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def get_vals(req: func.HttpRequest) -> func.HttpResponse:
    
    pagenum = req.params.get('pagenum',1)
    pagesize = req.params.get('pagesize',10)
    bpmstatus = req.params.get('bpmstatus')
    output = req.params.get('output','json')
    if output not in ['json','csv']:
        return func.HttpResponse(
            'output must be either "json" or "csv".',
            status_code=400
        )

    if bpmstatus is None:
        return func.HttpResponse(
            "Please pass a bpmstatus",
            status_code=400
        )
        
    xml_text = call_api(bpmstatus, pagenum, pagesize)
    et = text_to_xml(xml_text)
    processes = et.findall('.//BPMProcess')
    arr = [get_process(p) for p in processes]
    arr = [item for sublist in arr for item in sublist]
    
    if output=='json':    
        return func.HttpResponse(
            json.dumps(arr),
            status_code=200
        )    
    if output=='csv':
        write_headers = req.params.get('headers','false').lower()=='true'
        delimiter = req.params.get('delimiter', ',')
        if delimiter == 'tab':
            delimiter = '\t'
        
        from src.csv_parser import arr_to_csv
        return func.HttpResponse(
            arr_to_csv(arr, write_headers, delimiter=delimiter),
            status_code=200
        )

def get_rowcount(bpmstatus):
    xml_text = call_api(bpmstatus, 1, 1 )
    et = text_to_xml(xml_text)
    return int(et.find('.//TotalPage').text)

@app.route(route="mappings", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def get_mappings(req: func.HttpRequest) -> func.HttpResponse:
    bpmstatus = req.params.get('bpmstatus')
    nsample = int(req.params.get('nsample','500'))
    if bpmstatus is None:
        return func.HttpResponse(
            "Please pass a bpmstatus",
            status_code=400
        )
    rows = min(nsample, get_rowcount(bpmstatus))
    pagesize = 40
    logging.info(f'Rows: {rows} - running {rows//pagesize+1} batches')
    all_relations = set()
    for pagenum in range(1, rows//pagesize+2):
        logging.info(f'Running batch {pagenum}')
        xml_text = call_api(bpmstatus, pagenum, pagesize)
        et = text_to_xml(xml_text)
        map = [(p.tag,c.tag) for p in et.iter() for c in p]
        # tmp = [(v,k) for k,v in map.items()]
        all_relations.update(map)
    all_relations = list(all_relations)
    data = []
    ROOT='BPM'
    for p,c in all_relations:
        while True:
            if p==ROOT:
                data.append(f'{p}.{c}')
                break
            potential_parents = [a for a in all_relations if a[1]==p and a[0]!=p]
            if len(potential_parents)==0:
                raise ValueError(f'No parent found for {p}')
            if len(potential_parents)>1:
                raise ValueError(f'Multiple parents found for {p}')
            parent = potential_parents[0][0]
            p, c = parent, f'{p}.{c}'
                
    data = sorted(data)
    return func.HttpResponse(
        json.dumps(data),
        status_code=200
    )


@app.route(route="nrows", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def get_nrows(req: func.HttpRequest) -> func.HttpResponse:
    bpmstatus = req.params.get('bpmstatus')
    if bpmstatus is None:
        return func.HttpResponse(
            "Please pass a bpmstatus",
            status_code=400
        )
    rows = get_rowcount(bpmstatus)
    return func.HttpResponse(
        json.dumps({"rows":rows}),
        status_code=200
    )

@app.route(route="help", methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)
def get_help(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
'''<html>
<head>
    <title>Sample XML parser API</title>
</head>
<body>
<h1>Sample XML parser API</h1>

Thank you for using the sample XML parser API. 
This API is designed to parse XML data from the Ivalua API and return it in JSON or CSV format.
There are four exposed endpoints:
<ul>
<li>
    <code>/help</code>: This page
</li>
<li>
    <code>/values</code>: This endpoint returns the parsed data from the Ivalua API.
    <p>
    Parameters:
    <ul>
        <li><code>bpmstatus</code> (required): The status of the BPM process to filter by. Valid values are "draft", "val", "ini", "app".</li>
        <li><code>pagenum</code>: The page number to retrieve. Default is 1.</li>
        <li><code>pagesize</code>: The number of items per page. Default is 10.</li>
        <li><code>output</code>: The output format. Default is JSON. Options are 'json' or 'csv'.</li>
        <li><code>headers</code>: Whether to include headers in the CSV output. Default is false.</li>
    </ul></p>
</li>
<li>
    <code>/mappings</code>: This endpoint returns a best effort mapping of the XML data.
    <p>
    Use this endpoint to get an idea of how the data is structured for generating your future pipelines.
    Should be used by developers and for debugging purposes.
    </p><p>Parameters:
    <ul>
        <li><code>bpmstatus</code> (required): The status of the BPM process to filter by. Valid values are "draft", "val", "ini", "app".</li>
        <li><code>nsample</code>: The number of samples to calculate the mappings based on. Default is 500. If the number of rows is less than this value, it will use the number of rows.</li>
    </ul></p>
</li>
<li>
    <code>/nrows</code>: This endpoint returns the number of rows in the XML data.
    <p>
    Parameters:
    <ul>
        <li><code>bpmstatus</code> (required): The status of the BPM process to filter by. Valid values are "draft", "val", "ini", "app".</li>
    </ul></p>
</li>
</body></html>''',
        status_code=200,
        mimetype='text/html'
    )