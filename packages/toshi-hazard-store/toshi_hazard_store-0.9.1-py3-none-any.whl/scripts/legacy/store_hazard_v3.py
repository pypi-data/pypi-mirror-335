"""Script to export an openquake calculation and save it with toshi-hazard-store."""

import argparse
import datetime as dt
import logging
from pathlib import Path

from toshi_hazard_store import model

try:
    from openquake.calculators.extract import Extractor

    from toshi_hazard_store.oq_import import export_meta_v3, export_rlzs_v3
except (ModuleNotFoundError, ImportError):
    print("WARNING: the transform module uses the optional openquake dependencies - h5py, pandas and openquake.")

log = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('nshm_toshi_client.toshi_client_base').setLevel(logging.INFO)
# logging.getLogger('urllib3').setLevel(logging.INFO)
# logging.getLogger('botocore').setLevel(logging.INFO)
# logging.getLogger('gql.transport.requests').setLevel(logging.WARN)

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
root_handler = log.handlers[0]
root_handler.setFormatter(formatter)

# log.debug('DEBUG message')
# log.info('INFO message')


def extract_and_save(args):
    """Do the work."""

    hdf5_path = Path(args.calc_id)
    if hdf5_path.exists():
        # we have a file path to work with
        extractor = Extractor(str(hdf5_path))
    else:
        calc_id = int(args.calc_id)
        extractor = Extractor(calc_id)

    # Save metadata record
    t0 = dt.datetime.utcnow()
    if args.verbose:
        print('Begin saving meta')

    tags = [tag.strip() for tag in args.source_tags.split(',')]
    srcs = [src.strip() for src in args.source_ids.split(',')]

    print(tags, srcs)

    meta = export_meta_v3(extractor, args.toshi_hazard_id, args.toshi_gt_id, args.locations_id, tags, srcs)

    if args.verbose:
        print("Done saving meta, took %s secs" % (dt.datetime.utcnow() - t0).total_seconds())

    if not args.meta_data_only:
        # new v3 realisations storage
        t0 = dt.datetime.utcnow()
        if args.verbose:
            print('Begin saving realisations (V3)')
        export_rlzs_v3(
            extractor,
            meta,
        )

        if args.verbose:
            t1 = dt.datetime.utcnow()
            print("Done saving realisations, took %s secs" % (t1 - t0).total_seconds())


def parse_args():
    parser = argparse.ArgumentParser(
        description='store_hazard.py (store_hazard) - extract oq hazard by calc_id and store it.'
    )
    parser.add_argument('calc_id', help='an openquake calc id OR filepath to the hdf5 file.')
    parser.add_argument('toshi_hazard_id', help='hazard_solution id.')
    parser.add_argument('toshi_gt_id', help='general_task id.')
    parser.add_argument('locations_id', help="identifier for the locations used (common-py ENUM ??)")
    parser.add_argument('source_tags', help='e.g. "hiktlck, b0.979, C3.9, s0.78"')
    parser.add_argument('source_ids', help='e.g. "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwODA3NQ==,RmlsZToxMDY1MjU="')

    parser.add_argument('-c', '--create-tables', action="store_true", help="Ensure tables exist.")
    parser.add_argument('-v', '--verbose', help="Increase output verbosity.", action="store_true")
    parser.add_argument('-m', '--meta-data-only', action="store_true", help="Do just the meta data, then stop.")

    args = parser.parse_args()

    return args


def handle_args(args):
    # if args.debug:
    #     print(f"Args: {args}")

    if args.create_tables:
        print('Ensuring tables exist.')
        ## model.drop_tables() #DANGERMOUSE
        model.openquake_models.migrate()  # ensure model Table(s) exist (check env REGION, DEPLOYMENT_STAGE, etc

    extract_and_save(args)


def main():
    handle_args(parse_args())


if __name__ == '__main__':
    main()  # pragma: no cover
