# Standard library imports
import itertools
import operator
import os
import os.path as path
import sys

# RDKit imports for chemical structure handling
from rdkit import Chem
from rdkit.Chem import AllChem, Draw

# Import amino acid definitions
from p2smi.utilities.aminoacids import all_aminos

aminodata = all_aminos  # Current dictionary of amino acids

# Custom exceptions for specific error conditions


class CustomError(Exception):
    pass


class NoCysteineError(CustomError):
    pass


class BondSpecError(CustomError):
    pass


class FormatError(CustomError):
    pass


class UndefinedAminoError(CustomError):
    pass


class UndefinedPropertyError(CustomError):
    pass


class SmilesError(CustomError):
    pass


def add_amino(name):
    # Add an amino acid to aminodata if it exists in all_aminos and isn't already included
    if name in all_aminos and name not in aminodata:
        aminodata[name] = all_aminos[name]
        return True
    else:
        raise UndefinedAminoError(f"{name} not recognised as valid amino acid")


def remove_amino(name):
    # Remove an amino acid from aminodata if it exists
    if name in aminodata:
        del aminodata[name]
    else:
        raise UndefinedAminoError(f"{name} not found in amino acids")


def print_possible_aminos():
    # Return a list of all possible amino acid names
    return list(all_aminos.keys())


def print_included_aminos():
    # Return a list of currently included amino acid names
    return list(aminodata.keys())


def return_available_residues(out="Letter"):
    # Return a list of available residue properties (default: 'Letter')
    return [properties[out] for properties in aminodata.values()]


def return_constraint_resis(constraint_type):
    # Return amino acid names that satisfy a given constraint type
    return [
        name
        for name, properties in aminodata.items()
        if properties.get(constraint_type)
    ]


def property_to_name(property, value):
    # Find and return the aa name where the given property matches the specified value
    for name, properties in aminodata.items():
        if properties.get(property) == value:
            return name
    raise UndefinedAminoError(f"Amino-acid {value} for {property} not found")


def gen_all_pos_peptides(pepliblen):
    # Generate all possible peptide sequences of a given length
    amino_keys = list(aminodata.keys())
    for pep in itertools.product(amino_keys, repeat=pepliblen):
        yield pep


def gen_all_matching_peptides(pattern):
    # Generate all peptide sequences matching a given pattern,
    # where "X" (or "x") is treated as a wildcard for any amino acid.
    pattern = (
        pattern.replace("x", "X")
        if isinstance(pattern, str)
        else ["X" if resi == "x" else resi for resi in pattern]
    )
    amino_keys = list(aminodata.keys())
    for pep in itertools.product(amino_keys, repeat=pattern.count("X")):
        pep = list(pep)
        outpep = []
        for resi in pattern:
            if resi != "X":
                # If residue is not a wildcard, use it directly or convert
                if resi in aminodata:
                    outpep.append(resi)
                else:
                    outpep.append(property_to_name("Letter", resi))
            else:
                outpep.append(pep.pop(0))
        yield outpep


def can_ssbond(peptideseq):
    # Check if the peptide can form a disulphide bond.
    # Must have at least two residues with a "disulphide" constraint.
    disulphides = return_constraint_resis("disulphide")
    locs = [
        loc
        for loc, resi in enumerate(peptideseq)
        if resi in disulphides or property_to_name("Letter", resi) in disulphides
    ]
    if len(locs) < 2:
        return False
    # Find the pair with the greatest separation
    pos_pairs = sorted(
        [(pair, abs(pair[0] - pair[1])) for pair in itertools.combinations(locs, 2)],
        key=operator.itemgetter(1),
        reverse=True,
    )
    best_pair = pos_pairs[0]
    if best_pair[1] <= 2:
        return False
    # Build the pattern: "SS" prefix followed by "C" at the bond positions, "X" otherwise
    pattern = "SS" + "".join(
        ["C" if i in best_pair[0] else "X" for i in range(len(peptideseq))]
    )
    return peptideseq, pattern


def can_htbond(peptideseq):
    # Check if peptide qualifies for hydrogen bonding (length >= 5 or exactly 2)
    if len(peptideseq) >= 5 or len(peptideseq) == 2:
        return peptideseq, "HT"
    return False


def can_scntbond(peptideseq, strict=False):
    # Check for sidechain to C-terminal bond via n-terminal constraint.
    locs = [
        num + 3
        for num, resi in enumerate(peptideseq[3:])
        if resi in return_constraint_resis("cterm")
        or property_to_name("Letter", resi) in return_constraint_resis("cterm")
    ]
    if len(locs) == 0 or (len(locs) > 1 and strict):
        return False
    if not strict:
        # "SC" prefix with "Z" at the constrained position, "X" elsewhere
        pattern = ["SC"] + [
            "Z" if num == locs[-1] else "X" for num, _ in enumerate(peptideseq)
        ]
        return peptideseq, "".join(pattern)
    return False


def can_scctbond(peptideseq, strict=False):
    # Check for sidechain to C-terminal bond using n-term and ester constraints.
    esters = return_constraint_resis("ester")
    nterms = return_constraint_resis("nterm")
    locs = [
        (num, "N")
        for num, resi in enumerate(peptideseq[:-3])
        if resi in nterms or property_to_name("Letter", resi) in nterms
    ]
    locs += [
        (num, "E")
        for num, resi in enumerate(peptideseq[:-3])
        if resi in esters or property_to_name("Letter", resi) in esters
    ]
    if len(locs) == 0 or (len(locs) > 1 and strict):
        return False
    if not strict:
        pattern = ["SC"] + [
            locs[0][1] if num == locs[0][0] else "X" for num, _ in enumerate(peptideseq)
        ]
        return peptideseq, "".join(pattern)
    return False


def can_scscbond(peptideseq, strict=False):
    # Check for sidechain-to-sidechain bond formation.
    nterms = return_constraint_resis("nterm")
    cterms = return_constraint_resis("cterm")
    esters = return_constraint_resis("ester")
    locs = {"nterms": [], "cterms": [], "esters": []}
    for loc, resi in enumerate(peptideseq):
        for bondtype, bondname in [
            (nterms, "nterms"),
            (cterms, "cterms"),
            (esters, "esters"),
        ]:
            if resi in bondtype or property_to_name("Letter", resi) in bondtype:
                locs[bondname].append(loc)
    if not locs["cterms"] or not (locs["nterms"] or locs["esters"]):
        return False
    # Generate all possible pairs with separation of at least 2
    possible_pairs = [
        (pair, abs(pair[0] - pair[1]))
        for pair in itertools.product(locs["cterms"], locs["nterms"] + locs["esters"])
        if abs(pair[0] - pair[1]) >= 2
    ]
    if not possible_pairs:
        return False
    best_pair = max(possible_pairs, key=operator.itemgetter(1))[0]
    # Build pattern with "SC" prefix and appropriate bond code at the best pair positions
    pattern = "SC" + "".join(
        [
            (
                "Z"
                if num == best_pair[0]
                else (
                    "N"
                    if num == best_pair[1] and best_pair[1] in locs["nterms"]
                    else (
                        "E"
                        if num == best_pair[1] and best_pair[1] in locs["esters"]
                        else "X"
                    )
                )
            )
            for num, _ in enumerate(peptideseq)
        ]
    )
    return peptideseq, pattern


def what_constraints(peptideseq):
    # Return a list of all applicable constraint results for a peptide sequence
    return [
        result
        for func in [can_ssbond, can_htbond, can_scctbond, can_scntbond, can_scscbond]
        if (result := func(peptideseq))
    ]


def aaletter2aaname(aaletter):
    # Convert an amino acid letter to its full name
    for name, properties in all_aminos.items():
        if properties["Letter"] == aaletter:
            return name


def gen_library_strings(
    liblen,
    ssbond=False,
    htbond=False,
    scctbond=False,
    scntbond=False,
    scscbond=False,
    linear=False,
):
    # Generate a library of peptide strings based on specified bond constraints
    filterfuncs = []
    if ssbond:
        filterfuncs.append(can_ssbond)
    if htbond:
        filterfuncs.append(can_htbond)
    if scctbond:
        filterfuncs.append(can_scctbond)
    if scntbond:
        filterfuncs.append(can_scntbond)
    if scscbond:
        filterfuncs.append(can_scscbond)
    for sequence in gen_all_pos_peptides(liblen):
        for func in filterfuncs:
            if trialpeptide := func(sequence):
                yield trialpeptide
    if linear:
        for peptide in gen_all_pos_peptides(liblen):
            yield (peptide, "")


def gen_library_from_file(filepath, ignore_errors=False):
    # Generate peptide library entries from a file, ignoring commented/empty lines.
    with open(filepath) as peptides:
        for line in peptides:
            if line.startswith("#") or not line.strip():
                continue
            try:
                sequence, bond_def = map(str.strip, line.split(";"))
                if len(sequence.split(",")) == 1 and sequence not in all_aminos:
                    # Convert single-letter sequence to full names
                    sequence = [aaletter2aaname(letter) for letter in sequence]
                else:
                    sequence = sequence.split(",")
                yield constrained_peptide_smiles(sequence, bond_def)
            except Exception:
                if ignore_errors:
                    yield (None, None, None)
                else:
                    raise


def nmethylate_peptide_smiles(smiles):
    # N-methylate a peptide SMILES structure using substructure replacement
    mol = Chem.MolFromSmiles(smiles)
    n_pattern = Chem.MolFromSmarts("[$([Nh1](C)C(=O)),$([NH2]CC=O)]")
    methylated_pattern = Chem.MolFromSmarts("N(C)")
    rmol = AllChem.ReplaceSubstructs(
        mol, n_pattern, methylated_pattern, replaceAll=True
    )
    return Chem.MolToSmiles(rmol[0], isomericSmiles=True)


def nmethylate_peptides(structs):
    # Apply N-methylation to a sequence of peptide structures
    for struct in structs:
        seq, bond_def, smiles = struct
        if smiles:
            yield seq, bond_def, nmethylate_peptide_smiles(smiles)


def return_smiles(resi):
    # Get the standard SMILES for a residue
    return return_constrained_smiles(resi, "SMILES")


def return_constrained_smiles(resi, constraint):
    # Return the SMILES string for a residue based on a specific constraint type
    try:
        return aminodata[resi][constraint]
    except KeyError:
        try:
            return aminodata[property_to_name("Letter", resi)][constraint]
        except UndefinedAminoError:
            try:
                return aminodata[property_to_name("Code", resi)][constraint]
            except UndefinedAminoError:
                raise UndefinedAminoError(f"{resi} not recognised as amino acid")


def linear_peptide_smiles(peptideseq):
    # Generate a linear peptide SMILES string by sequentially connecting residues
    if not peptideseq:
        return None
    combsmiles = "O"  # Starting oxygen atom
    for resi in peptideseq:
        combsmiles = combsmiles[:-1] + return_smiles(resi)
    return combsmiles


def bond_counter(peptidesmiles):
    # Count and return the highest bond number found in the SMILES string
    return max([int(num) for num in peptidesmiles if num.isdigit()], default=0)


def pep_positions(linpepseq):
    # Calculate starting positions of residues in the linear peptide SMILES
    positions = []
    location = 0
    for resi in linpepseq:
        positions.append(location)
        location += len(return_smiles(resi)) - 1
    return positions


def constrained_peptide_smiles(peptideseq, pattern):
    # Generate a constrained peptide SMILES string based on a bonding pattern
    valid_codes = {
        "C": "disulphide",
        "Z": "cterm",
        "N": "nterm",
        "E": "ester",
        "X": "",  # 'X' indicates no constraint
    }
    smiles = "O"  # Start with oxygen atom

    if not pattern:
        return peptideseq, "", linear_peptide_smiles(peptideseq)

    if pattern[:2] == "HT":
        # Handle hydrogen bond patterns
        smiles = linear_peptide_smiles(peptideseq)
        bond_num = str(bond_counter(smiles) + 1)
        smiles = smiles[0] + bond_num + smiles[1:-5] + bond_num + smiles[-5:-1]
        return peptideseq, pattern, smiles

    for resi, code in zip(peptideseq, pattern[2:]):
        smiles = smiles[:-1]
        if code in valid_codes:
            smiles += (
                return_constrained_smiles(resi, valid_codes[code])
                if valid_codes[code]
                else return_smiles(resi)
            )
        elif code == "X":
            smiles += return_smiles(resi)
        else:
            raise BondSpecError(f"{code} in pattern {pattern} not recognised")

    # Edit N- or C-terminus based on non-wildcard parts of the pattern
    pattern_for_fixing = pattern.replace("X", "")
    if pattern_for_fixing == "SCN":  # N acts as N-term binding to C-term
        smiles = smiles[:-5] + "*(=O)"
    elif pattern_for_fixing == "SCE":  # E (ester) binds the C-term
        smiles = smiles[:-5] + "*(=O)"
    elif pattern_for_fixing == "SCZ":  # Z indicates C-term on a sidechain bond
        smiles = "N*" + smiles[1:]

    # Replace placeholder '*' with an incremented bond number
    bond_number = str(bond_counter(smiles) + 1)
    smiles = smiles.replace("*", bond_number)

    return peptideseq, pattern, smiles


def gen_structs_from_seqs(
    sequences,
    ssbond=False,
    htbond=False,
    scctbond=False,
    scntbond=False,
    scscbond=False,
    linear=False,
):
    # Generate peptide structures from sequences applying specified bonding constraints
    funcs = [
        (ssbond, can_ssbond),
        (htbond, can_htbond),
        (scctbond, can_scctbond),
        (scntbond, can_scntbond),
        (scscbond, can_scscbond),
    ]
    for seq in sequences:
        for check, func in funcs:
            if check and (result := func(seq)):
                seq, bonddef = result
                yield constrained_peptide_smiles(seq, bonddef)
        if linear:
            yield (seq, "", linear_peptide_smiles(seq))


def gen_library_structs(
    liblen,
    ssbond=False,
    htbond=False,
    scctbond=False,
    scntbond=False,
    scscbond=False,
    linear=False,
):
    # Generate peptide structures for library based on sequence length and constraints
    for peptideseq, bond_def in gen_library_strings(
        liblen, ssbond, htbond, scctbond, scntbond, scscbond, linear
    ):
        if bond_def == "":
            yield (peptideseq, "", linear_peptide_smiles(peptideseq))
        else:
            yield constrained_peptide_smiles(peptideseq, bond_def)


def filtered_output(output, filterfuncs, key=None):
    # Filter the output items based on provided functions
    for out_item in output:
        if key:
            if all(func(key(out_item)) for func in filterfuncs):
                yield out_item
        else:
            if all(func(out_item) for func in filterfuncs):
                yield out_item


def get_constraint_type(bond_def):
    # Determine the constraint type from a bond definition string
    type_id, defi = bond_def[:2], bond_def[2:]
    if defi == "":
        return "linear" if type_id == "" else type_id
    if type_id == "SS" and all(char in ["X", "C"] for char in defi):
        return "SS"
    if type_id == "SC":
        if all(char in ["X", "Z", "E", "N"] for char in defi):
            if defi.count("X") == len(defi) - 1:
                if "N" in defi or "E" in defi:
                    return "SCCT"
                if "Z" in defi:
                    return "SCNT"
            elif defi.count("X") == len(defi) - 2:
                return "SCSC"
    raise BondSpecError(f"{bond_def} not recognised as valid bond_def")


def count_constraint_types(inlist, ignore_errors=False):
    # Count the number of peptides for each constraint type
    count_dict = {
        "linear": 0,
        "SS": 0,
        "HT": 0,
        "SCSC": 0,
        "SCCT": 0,
        "SCNT": 0,
    }
    for pep in inlist:
        try:
            count_dict[get_constraint_type(pep[1])] += 1
        except Exception:
            if ignore_errors:
                continue
            else:
                raise
    return count_dict


def save_3Dmolecule(sequence, bond_def):
    # Generate and save a 3D structure file (SDF) for peptide with given bond definition
    fname = f"{''.join(sequence)}_{bond_def}.sdf"
    _, _, smiles = constrained_peptide_smiles(sequence, bond_def)
    mol = Chem.MolFromSmiles(smiles)
    AllChem.EmbedMolecule(mol)
    AllChem.UFFOptimizeMolecule(mol)
    writer = AllChem.SDWriter(fname)
    writer.write(mol)
    return fname


def write_molecule(
    smiles,
    peptideseq,
    bond_def,
    outfldr,
    type="sdf",
    write="structure",
    return_struct=False,
    new_folder=True,
):
    # Write the molecule either as a drawn image or as a 3D structure file.
    twodfolder = threedfolder = outfldr
    if not return_struct and new_folder:
        twodfolder = path.join(outfldr, "2D-Files")
        threedfolder = path.join(outfldr, "3D-Files")

    bond_def = f"_{bond_def}" if bond_def else "_linear"
    try:
        name = peptideseq + bond_def
    except TypeError:
        try:
            name = (
                "".join([aminodata[resi]["Letter"] for resi in peptideseq]) + bond_def
            )
        except KeyError:
            name = ",".join(peptideseq) + bond_def

    mymol = Chem.MolFromSmiles(smiles)
    if not mymol:
        raise SmilesError(f"{smiles} returns None molecule")
    mymol.SetProp("_Name", name)

    if write == "draw":
        if not path.exists(twodfolder):
            os.makedirs(twodfolder)
        Draw.MolToFile(mymol, path.join(twodfolder, name + ".png"), size=(1000, 1000))
    elif write == "structure":
        if not path.exists(threedfolder):
            os.makedirs(threedfolder)
        AllChem.EmbedMolecule(mymol)
        AllChem.UFFOptimizeMolecule(mymol)
        if return_struct:
            return Chem.MolToMolBlock(mymol)
        else:
            with open(path.join(threedfolder, name + "." + type), "wb") as handle:
                handle.write(Chem.MolToMolBlock(mymol))
    else:
        raise TypeError(f'"write" must be set to "draw" or "structure", got {write}')
    return True


def write_library(inputlist, outloc, write="text", minimise=False, write_to_file=False):
    # Write the peptide library output to file (text, drawn images, or structure files).
    count = 0
    if write == "text":
        with open(outloc, "w") as f:
            for peptide in inputlist:
                try:
                    seq, bond_def, smiles = peptide
                    bond_def = bond_def if bond_def else "linear"
                    f.write(f"{','.join(seq)}-{bond_def}: {smiles}\n")
                    count += 1
                except Exception as e:
                    print(e)
    elif write in {"draw", "structure"}:
        if write_to_file:
            with open(outloc, "w") as out:
                for peptide in inputlist:
                    peptideseq, bond_def, smiles = peptide
                    if not peptideseq and not bond_def and not smiles:
                        continue
                    mol = Chem.MolFromSmiles(smiles)
                    AllChem.EmbedMolecule(mol)
                    AllChem.UFFOptimizeMolecule(mol)
                    try:
                        name = peptideseq + bond_def
                    except TypeError:
                        try:
                            name = (
                                "".join(
                                    [aminodata[resi]["Letter"] for resi in peptideseq]
                                )
                                + bond_def
                            )
                        except KeyError:
                            name = ",".join(map(str, peptideseq)) + bond_def
                    mol.SetProp("_Name", name)
                    molstr = Chem.MolToMolBlock(mol)
                    out.write(molstr + "\n$$$$\n")
                    count += 1
        else:
            for peptide in inputlist:
                seq, bond_def, smiles = peptide
                try:
                    write_molecule(smiles, seq, bond_def, outloc, write=write)
                    count += 1
                except Exception as e:
                    print(e)
    else:
        raise TypeError(f'"write" must be set to "draw" or "structure", got {write}')
    return count


def main(pattern, out_file):
    # Main function: generate peptides matching a pattern and write to file.
    print(f"Writing all peptides for pattern {pattern}")
    out_f = f"{out_file}.sdf"
    peptides = gen_all_matching_peptides(pattern)
    structures = gen_structs_from_seqs(peptides, True, True, True, True, True, True)
    write_library(structures, out_f, "structure", False, True)


if __name__ == "__main__":
    # Execute main with command-line arguments
    main(*sys.argv[1:], sys.argv[0])
