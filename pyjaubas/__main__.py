import argparse
from . import bas


LOOKUP_TABLES = {
    "smg1": bas.SuperMarioGalaxy1SoundTable,
    "smg2": bas.SuperMarioGalaxy2SoundTable
}


def dump(args):
    if args.lookup in LOOKUP_TABLES:
        soundtbl = LOOKUP_TABLES[args.lookup]()
    else:
        soundtbl = bas.JAUSoundIdTable(args.lookup)
    soundanm = bas.from_file(soundtbl, args.bas, not args.little_endian)
    bas.dump_json(soundanm, args.json)
    print("Successfully dumped data to JSON file.")


def pack(args):
    if args.lookup in LOOKUP_TABLES:
        soundtbl = LOOKUP_TABLES[args.lookup]()
    else:
        soundtbl = bas.JAUSoundIdTable(args.lookup)
    soundanm = bas.from_json(soundtbl, args.json)
    bas.write_file(soundanm, args.bas, not args.little_endian)
    print("Successfully packed BAS data.")


def main():
    parser = argparse.ArgumentParser(description="")
    subs = parser.add_subparsers(dest="command", help="Command")
    subs.required = True

    dump_parser = subs.add_parser("tojson", description="Dump BAS data to JSON file.")
    pack_parser = subs.add_parser("tobas", description="Pack JSON file as BAS data.")

    for sub_parser in [dump_parser, pack_parser]:
        sub_parser.add_argument("-le", "--little_endian", action="store_true", help="Data is little-endian?")
        sub_parser.add_argument("lookup", help="Path to sound lookup table.")

    dump_parser.add_argument("bas", help="Path to BAS data.")
    dump_parser.add_argument("json", help="Path to JSON file.")
    dump_parser.set_defaults(func=dump)

    pack_parser.add_argument("json", help="Path to JSON file.")
    pack_parser.add_argument("bas", help="Path to BAS data.")
    pack_parser.set_defaults(func=pack)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
