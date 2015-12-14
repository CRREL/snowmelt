import re
import json

EXTENTS_FILE = 'snow_extents.txt'
EXTENTS_REG = re.compile(
    r'^"(?P<division>\w+)", "(?P<district>\w+)", '
    r'"(?P<watershed>[\S\s^\"]+)", (?P<extents>[\S\s]+)\n$'
)


def main():

    extents_dict = {}
    extents_file = open(EXTENTS_FILE, 'r')
    for line in extents_file:
        if line[0] != '#':
            attrs = EXTENTS_REG.match(line).groupdict()            
            extents = [int(coord) for coord in attrs['extents'].split(', ')]
            watershed = [attrs['watershed'], extents]
            # print watershed
            try:
                districts = extents_dict[attrs['division']]
            except KeyError:
                extents_dict[attrs['division']] = {}
            try:
                watersheds = extents_dict[attrs['division']][attrs['district']]
            except KeyError:
                watersheds = []
            watersheds.append(watershed)
            extents_dict[attrs['division']][attrs['district']] = watersheds
    extents_file.close()
    print extents_dict

    print '-' * 64

    # output = json.dumps(extents_dict, sort_keys=True, indent=4)

    # output_file = open('extents_dict.txt', 'w')
    # output_file.write(output)
    # output_file.close()

    print 'EXTENTS = {'
    for division in sorted(extents_dict.iterkeys()):
        print '    \'{0}\': {{'.format(division.lower())
        for district in sorted(extents_dict[division].iterkeys()):
            print '        \'{0}\': ['.format(district.lower())
            for watershed in extents_dict[division][district]:
                print '            {0},'.format(watershed)
            print '        ],'
        print '    },'
    print '}'

if __name__ == '__main__':
    main()
