# Config file that contains watershed extents by division/district.

EXTENTS = {
    'nad': {
        'nae': [
            ['Connecticut River', [1820000, 2266000, 1958000, 2734000]],
        ],
        'nab': [
            ['Upper Susquehanna River', [1558000, 2140000, 1740000, 2410000]],
        ],
    },
    'mvd': {
        'mvp': [
            ['Red River', [-351108, 2498740, 145082, 3000000]],
            # ['Red River', [-351108, 2498740, 450812, 2944780]], old extents v2
            # ['Red River', [-234000, 2494000, 68000, 2896000]], old extents
        ],
        'mvs': [
            ['Kaskaskia River', [498000, 1672000, 670000, 1938000]],
        ],
    },
    'nwd': {
        'nwo': [
            ['South Platte River', [-878000, 1784000, -384000, 2086000]],
        ],
    },
    'lrd': {
        'lrl': [
            ['Salt River', [866000, 1646000, 980000, 1766000]],
        ]
    }
}

TOP_DIR = '/fire/study/snow/nohrsc_gdal'
SRC_DIR = '/fire/study/snow/rawdata'

ARCHIVE_DIR = '/fire/study/snow/archive/misc/SNODAS'
ARCHIVE_DIR_2012 = '/fire/study/snow/rawdata_2012'

