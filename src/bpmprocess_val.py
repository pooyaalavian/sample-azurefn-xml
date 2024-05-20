from src.xml_parser import get_one_to_one, get_one_to_many, empty_object, merge_objects, Element



KEYS_MAIN = [
    'ProjectName',
    'ProgramDisplay',
    'QuotingCurrencyDisplay',
    'SourcingBoardDate',
    'bpm_id',
    'QuotingCurrencyRateUSD',
    'PeakVolume',
    'FirstYearVolume',
]

KEYS_ORG = [
    'bpm_id',
    'orga_level',
    'orga_node',
    'orga_label_en',
]

KEYS_PROG = [
    'OffToolSampleDate',
    'ProgID',
    'ProgramCode',
    'ProgramName',
    'ProgramYear',
    'StartOfProduction',
    'bpm_id',
    'item_code',
    'item_id',
]

KEYS_COMMODITIES = [
    'bpm_id',
    'fam_label_en',
    'fam_level',
    'fam_node',
]

KEYS_ITEM = [
    'APQPAssessmentPoints',
    'ItemDescription',
    'ItemID',
    'ItemNumber',
    'ItemVersion',
    'NPV',
    'PPAPLeadTimeInWeeks',
    'PaidDuty',
    'PaidShipping',
    'PartNumber',
    'RelatedRFQID',
    'Revision',
    'SopPiecePrice',
    'StatusCode',
    'SupOTSLeadTimeInWeeks',
    'SupplierName',
    'UnitCode',
    'currencyrate',
    'priceforallneededtools',
]

KEYS_ITEM_INCENTIVE = [
    'CostReductionSum',
    'IncentiveYear',
    'SustainedSUM',
]

KEYS_ITEM_YEARLY_DETAILS = [
    'SupplierName',
    'YearID',
    'AIF',
    'Volume',
    'RFPItemID',
    'BIDescription',
    'BI',
    'PiecePrice',
]

def empty_item(*,yearly_prefix='Yearly_', incentive_prefix='Incentive_'):
    keys = (
        KEYS_ITEM 
        + [yearly_prefix+k for k in KEYS_ITEM_YEARLY_DETAILS]
        + [incentive_prefix+k for k in KEYS_ITEM_INCENTIVE]
    )
    return empty_object(keys)

def empty_program():
    return empty_object(KEYS_PROG)

def get_organization(processNode:Element):
    try:
        obj = get_one_to_one(processNode, './/Organization', KEYS_ORG)
    except Exception as e:
        print(e)
        obj = empty_object(KEYS_ORG)
    return obj

def get_commodity(processNode:Element):
    try:
        obj = get_one_to_one(processNode, './/Commodity', KEYS_COMMODITIES)
    except Exception as e:
        print(e)
        obj = empty_object(KEYS_COMMODITIES)
    return obj

def get_items_arr(processNode:Element):
    def flattener(node:Element, obj):
        years = []
        incentives = []
        for year in node.findall('.//Yearly'):
            y = {k:None for k in KEYS_ITEM_YEARLY_DETAILS}
            for attr in year.findall('./'):
                if attr.tag in KEYS_ITEM_YEARLY_DETAILS:
                    y[attr.tag]=attr.text            
            years.append(y )
        for incentive in node.findall('./Incentive/Incentive'):
            c = {k:None for k in KEYS_ITEM_INCENTIVE}
            for attr in incentive.findall('./'):
                if attr.tag in KEYS_ITEM_INCENTIVE:
                    c[attr.tag]=attr.text
            incentives.append(c)
        
        if len(years)==0:
            years = [empty_object(KEYS_ITEM_YEARLY_DETAILS)]
        if len(incentives)==0:
            incentives = [empty_object(KEYS_ITEM_INCENTIVE)]
        arr = []
        for y in years:
            for c in incentives:
                tmp = merge_objects(obj, y, second_prefix='Yearly_')
                tmp = merge_objects(tmp, c, second_prefix='Incentive_')
                arr.append(tmp)
        
        return arr 

    results = get_one_to_many(processNode,'.//Item',KEYS_ITEM, additional_fn=flattener)
    return results

def get_programs_arr(processNode:Element):
    return get_one_to_many(processNode, 'Program/Program', KEYS_PROG)

def get_process(processNode:Element):
    try:
        proc = get_one_to_one(processNode,'.',KEYS_MAIN)
        org = get_organization(processNode)
        com = get_commodity(processNode)
        proc = merge_objects(proc, org, second_prefix='Organization_')
        proc = merge_objects(proc, com, second_prefix='Commodity_')
        results = [proc]
    except Exception as e:
        print(e)
        return []
    
    items = get_items_arr(processNode)
    if len(items)==0:
        items = [empty_item()]
    # for item in items:
    #     tmp = merge_objects(proc, item, 'Item_')
    #     results.append(item)
    results = [merge_objects(r, item, second_prefix='Item_') for r in results for item in items]
    
    programs = get_programs_arr(processNode)
    if len(programs)==0:
        programs = [empty_program()]
    results = [merge_objects(r, prog, second_prefix='Program_') for r in results for prog in programs]

    return results 