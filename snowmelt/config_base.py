# Base configuration file that contains watershed extents by division/district.

TOP_DIR = '/fire/study/snow/nohrsc_gdal'

# This is where we look for source files to process.
SRC_DIR = '/fire/study/snow/rawdata'
ARCHIVE_DIR = '/fire/study/snow/archive/misc/SNODAS'
ARCHIVE_DIR_2012 = '/fire/study/snow/rawdata'

# This is where we store the nationwide prepped data sets.
# Unzipped data and CONUS wide tif files will be store in two dirs
# inside PROCESSED_SRC_DIR.
PROCESSED_SRC_DIR = '/fire/study/snow/nohrsc_gdal'

# Where we find the headers we need when preparing our source data.
HEADER_KEY_DIR = '/fire/study/snow/nohrsc_gdal/key'

# These three locations are the base directories for our output files.
DSS_BASE_DIR = '/fire/study/snow/nohrsc_gdal'
HISTORY_BASE_DIR = '/fire/study/snow/nohrsc_gdal'
ASC_BASE_DIR = '/fire/study/snow/nohrsc_gdal'

# If this is set to True, the three base dirs above will be ignored and
# all results will be tossed into TOP_DIR/division/district/results_sn/.../
LEGACY_DIRECTORY_STRUCTURE = False

SCP_TARGET_STR = \
    'cwmsgrids@cpc-cwms2.usace.army.mil:/netapp/cwmsgrids/data/watershed/{0}/{1}/'

KEEP_PROCESSED_SRC_DATA = False
SUBPROCESS_QUIET = True

EXTENTS = {
    'iwr': {
        'hec': [
            ['Russian River', [-2320000, 2014000, -2258000, 2154000]],
            ['Upper Susquehanna River', [1558000, 2140000, 1740000, 2410000]],
            ['Minnesota River', [-112000, 2244000, 234000, 2602000]],
        ],
    },
    'lrd': {
        'lrb': [
            ['Genesee River', [1428000, 2230000, 1508000, 2400000]],
        ],
        'lre': [
            ['Lake Winnebago', [500000, 2294000, 656000, 2556000]],
        ],
        'lrh': [
            ['Scioto River', [1004000, 1810000, 1154000, 2056000]],
            ['Big Sandy River', [1114000, 1624000, 1288000, 1796000]],
            ['Little Sandy River', [1096000, 1732000, 1158000, 1812000]],
            ['Twelvepole River', [1152000, 1728000, 1212000, 1796000]],
            ['Hocking River', [1112000, 1878000, 1220000, 1960000]],
            ['Little Kanawha River', [1164000, 1824000, 1354000, 1970000]],
            ['Muskingum River', [1098000, 1904000, 1268000, 2110000]],
            ['Kanawha River', [1182000, 1544000, 1410000, 1870000]],
            ['Guyandotte River', [1166000, 1692000, 1298000, 1814000]],
        ],
        'lrl': [
            ['Mill Creek', [968000, 1840000, 998000, 1884000]],
            ['Ohio River', [584000, 1566000, 1028000, 2004000]],
            ['Salt River', [866000, 1646000, 980000, 1766000]],
            ['Little Wabash River', [608000, 1674000, 698000, 1860000]],
            ['Upper Wabash River', [730000, 1946000, 978000, 2090000]],
            ['Middle Wabash River', [708000, 1714000, 942000, 1982000]],
            ['Whitewater River', [900000, 1844000, 968000, 1958000]],
            ['Great Miami River', [930000, 1838000, 1056000, 2028000]],
            ['Little Miami River', [980000, 1824000, 1058000, 1952000]],
            ['Kentucky River', [924000, 1606000, 1176000, 1818000]],
            ['Licking River', [968000, 1678000, 1150000, 1850000]],
            ['Green River', [720000, 1528000, 998000, 1694000]],
        ],
        'lrp': [
            ['Upper Ohio River', [1244000, 1942000, 1300000, 1976000]],
            ['Monongahela River', [1306000, 1818000, 1448000, 2064000]],
            ['Beaver River', [1216000, 1944000, 1356000, 2194000]],
            ['Allegheny River', [1280000, 2002000, 1494000, 2298000]],
        ],
    },
    'mvd': {
        'mvp': [
            ['Eau Galla River', [284000, 2404000, 326000, 2460000]],
            ['Minnesota River', [-112000, 2244000, 234000, 2602000]],
            ['Mississippi River Headwaters', [24000, 2526000, 254000, 2760000]],
            ['Mississippi River Navigation', [48000, 2204000, 564000, 2646000]],
            ['Red River North', [-356000, 2494000, 150000, 2950000]],
            ['Souris River', [-498000, 2748000, -260000, 2910000]],
        ],
        'mvr': [
            ['Mississippi River', [162000, 1810000, 636000, 2338000]],
            ['Des Moines River', [-14000, 1932000, 390000, 2368000]],
            ['Iowa River', [168000, 2006000, 444000, 2338000]],
            ['Illinois River', [396000, 1824000, 842000, 2276000]],
        ],
        'mvs': [
            ['Mississippi River', [400000, 1564000, 610000, 1860000]],
            ['Illinois River', [400000, 1772000, 552000, 1910000]],
            ['Cuivre River', [356000, 1758000, 462000, 1828000]],
            ['Meramec River', [360000, 1612000, 500000, 1752000]],
            ['St. Francis River', [454000, 1548000, 512000, 1668000]],
            ['Big Muddy River', [550000, 1626000, 646000, 1746000]],
            ['Salt River', [280000, 1780000, 426000, 1944000]],
            ['Kaskaskia River', [498000, 1672000, 670000, 1938000]],
        ],
    },
    'nad': {
        'nab': [
            ['Chemung River', [1466000, 2218000, 1598000, 2336000]],
            ['Juniata River', [1438000, 2000000, 1592000, 2136000]],
            ['Main Stem Susquehanna River', [1512000, 2004000, 1696000, 2162000]],
            ['Upper Susquehanna River', [1558000, 2140000, 1740000, 2410000]],
            ['West Branch Susquehanna River', [1418000, 2066000, 1632000, 2252000]],
        ],
        'nap': [
            ['Delaware River', [1620000, 1920000, 1838000, 2384000]],
        ],
        'nae': [
            ['Blackstone River', [1946000, 2344000, 2012000, 2408000]],
            ['Housatonic River', [1820000, 2240000, 1896000, 2404000]],
            ['Thames River', [1916000, 2268000, 1992000, 2396000]],
            ['Connecticut River', [1820000, 2266000, 1958000, 2734000]],
            ['Merrimack River', [1892000, 2384000, 2030000, 2612000]],
        ],
    },
    'nwd': {
        'nwd': [
            ['Above Fort Peck', [-1394000, 2460000, -740000, 2998000]],
            ['Big Horn River', [-1132000, 2226000, -850000, 2634000]],
            ['Chariton River', [180000, 1798000, 310000, 2012000]],
            ['Gavins Point to Sioux City', [-316000, 2136000, 38000, 2770000]],
            ['Missouri River', [-1394000, 1552000, 510000, 3044000]],
            ['North Platte River', [-1080000, 1964000, -384000, 2298000]],
            ['Oahe to Fort Randall', [-644000, 2188000, -184000, 2452000]],
            ['South Platte River', [-878000, 1784000, -384000, 2086000]],
        ],
        'nwp': [
            ['Cowlitz River', [-2070000, 2838000, -1918000, 2922000]],
            ['Umpqua River', [-2240000, 2496000, -2068000, 2660000]],
            ['Tualatin River', [-2120000, 2770000, -2054000, 2838000]],
            ['Crooked River', [-2006000, 2512000, -1854000, 2668000]],
            ['Willamette River', [-2174000, 2548000, -1988000, 2850000]],
            ['Willow Creek', [-1840000, 2682000, -1800000, 2732000]],
            ['Rogue River', [-2296000, 2412000, -2088000, 2534000]],
            ['Columbia River', [-2144000, 2522000, -1694000, 2920000]],
        ],
        'nws': [
            ['Kootenai River', [-1544000, 2908000, -1370000, 3064000]],
            ['Columbia River', [-1942000, 2782000, -1442000, 3132000]],
            ['Cedar River', [-1976000, 2950000, -1906000, 3046000]],
            ['Pend Oreille River', [-1608000, 2630000, -1234000, 3074000]],
            ['Chehalis River', [-2104000, 2886000, -1998000, 3032000]],
            ['Skagit River', [-1986000, 3020000, -1804000, 3176000]],
            ['Puyallup River', [-1992000, 2908000, -1908000, 2980000]],
            ['Green River', [-1980000, 2934000, -1900000, 3010000]],
        ],
        'nww': [
            ['Powder River', [-1750000, 2582000, -1642000, 2670000]],
            ['Columbia River', [-1798000, 2746000, -1678000, 2872000]],
            ['Mill Creek', [-1766000, 2726000, -1654000, 2820000]],
            ['NF Clearwater River', [-1616000, 2636000, -1394000, 2844000]],
            ['Lower Snake River', [-1772000, 2454000, -1336000, 2928000]],
            ['Malheur River', [-1816000, 2436000, -1656000, 2590000]],
            ['Boise River', [-1676000, 2402000, -1482000, 2508000]],
            ['Willow Creek', [-1292000, 2308000, -1228000, 2404000]],
            ['Little Wood River', [-1520000, 2334000, -1408000, 2450000]],
            ['Upper Snake River', [-1592000, 2198000, -1098000, 2522000]],
            ['Middle Snake River', [-1802000, 2186000, -1482000, 2656000]],
        ],
    },
    'pod': {
        'poa': [
            ['Chena River', [-2830000, 5228000, -2634000, 5324000]],
        ],
    },
    'spd': {
        'spa': [
            ['Pecos River', [-916000, 744000, -490000, 1486000]],
            ['Arkansas River', [-912000, 1564000, -516000, 1872000]],
            ['Canadian River', [-858000, 1330000, -626000, 1604000]],
            ['Rio Grande', [-1260000, 360000, -517000, 1766000]],
            ['Rio Hondo', [-914000, 1158000, -770000, 1226000]],
        ],
        'spk': [
            ['Upper Colorado River', [-1430000, 1452000, -806000, 2362000]],
            ['Weber River', [-1352000, 2050000, -1236000, 2164000]],
            ['Provo River', [-1326000, 2016000, -1238000, 2074000]],
            ["Parley's Canyon Creek", [-1368000, 1946000, -1268000, 2110000]],
            ['Tulare Lakebed', [-2180000, 1546000, -1942000, 1822000]],
            ['San Joaquin River', [-2238000, 1758000, -1968000, 2030000]],
            ['Sacramento River', [-2296000, 1936000, -1962000, 2420000]],
            ['Truckee River', [-2068000, 1996000, -1872000, 2200000]],
        ],
        'spl': [
            ['Gila River', [-1722000, 973000, -1079000, 1563000]],
        ],
    },
}

PROJECT_EXTENTS = {
    'missouri_river': [
        ['Missouri River', [-1399054, 1546181, 514768, 3049874]],
    ],
}
