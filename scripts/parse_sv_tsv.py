
def parse(vcf_reader):
    variants = []
    nr_of_vars = 0
    nr_filtered = 0
    ref_version = "Unknown"
    header = False
    min_nr_progs = 2    # Define the number of programs that need to call the variant for it to continue

    for line in vcf_reader:
        line = line.rstrip().split()

        if not header:
            # Try finding a reference genome file
            if line[0] == "##Reference":
                ref_version = "\t".join(line)

            # Parse in header line
            if line[0] == "CHR1":
                header = line

            continue

        nr_of_vars += 1

        # Filter out variants with filter tag
        if line[header.index('CUSTOM_FILTER')] != "PASS":
            #print("[DEBUG] Found filter: " + str(line[header.index('CUSTOM_FILTER')]))
            nr_filtered += 1
            continue

        '''
        # Filter out variants that do not get called by min_nr_progs
        if int(line[header.index('NPROGS')]) < min_nr_progs:
            nr_filtered += 1
            continue
        '''

        start_chrom = line[header.index('CHR1')]
        start = line[header.index('POS1')]
        end_chrom = line[header.index('CHR2')]
        end = line[header.index('POS2')]
        ref = None
        alt = None
        if start_chrom == end_chrom:
            length = int(end) - int(start)
        else:
            length = None

        # Find sv_type
        svtypes = []
        progs = line[header.index('PROGS')]
        for prog in progs.split(","):
            if "SVTYPE_" + prog in header:
                svtypes.append(line[header.index("SVTYPE_" + prog)])
        svtypes = list(dict.fromkeys(svtypes))
        if 'deletion' in svtypes and 'DEL' in svtypes:
            svtypes.remove('deletion')
        if 'DUP' in svtypes and 'tandem-duplication' in svtypes:
            svtypes.remove('tandem-duplication')
        if 'inversion' in svtypes and 'INV' in svtypes:
            svtypes.remove('inversion')
        if len(svtypes) == 1:
            sv_type = svtypes[0]
        elif len(svtypes) == 0:
            sv_type = None
        else:
            if "BND" in svtypes:
                svtypes.remove('BND')
                if len(svtypes) == 1:
                    sv_type = svtypes[0]
                else:
                    print("Unknown SV combination! Please check!")
                    print(svtypes)
                    sv_type = None
            else:
                print("Unknown SV combination! Please check!")
                print(svtypes)
                sv_type = None

        # Reformat types
        sv_type.replace("deletion", "DEL")

        #print([start_chrom, start, end_chrom, end, ref, alt, length, sv_type])
        variants.append([start_chrom, start, end_chrom, end, ref, alt, length, sv_type])

    print("[INFO] Reference version: " + ref_version)

    return(variants, nr_of_vars, nr_filtered)