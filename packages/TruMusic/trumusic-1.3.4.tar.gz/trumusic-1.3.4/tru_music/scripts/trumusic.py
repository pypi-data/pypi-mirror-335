#!/usr/bin/env python

import argparse

from tru_music import TruMusic


def list_str(values):
    return values.split(',')


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Run TruMusic Functions',
    )

    parser.add_argument(
        '-d', '--dry_run',
        action='store_true',
        dest='dry_run',
        help='Dry run mode',
        default=False,
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        dest='quiet',
        help='All prompts are skipped and continue with defaults',
        default=False,
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='Enable verbose logging',
    )

    parser.add_argument(
        '-a', '--artist',
        dest='artist',
        help="Filter by album artist",
        type=str.lower,
    )

    parser.add_argument(
        '-t', '--title',
        dest='title',
        help="Filter by album title",
        type=str.lower,
    )

    parser.add_argument(
        '-l', '--link',
        dest='link',
        help="Specify a link to download the album",
    )

    parser.add_argument(
        '-f', '--file_format',
        dest='file_format',
        help=f"Format of the files to be uploaded. Supported file formats: {TruMusic.supported_file_extensions}",
        default='mp3',
    )

    args = parser.parse_args()

    if not args.link:
        if not args.artist:
            args.artist = input(f"Artist: ")

        if not args.title:
            args.title = input(f"Album (optional): ")

    if args.file_format not in TruMusic.supported_file_extensions:
        parser.error(f"Invalid file format specified: {args.file_format}")

    return args


def main():
    args = parse_args()

    trumusic = TruMusic(
        ext=args.file_format,
        dry_run=args.dry_run,
        quiet=args.quiet,
        verbose=args.verbose,
        artist_name=args.artist,
        album_name=args.title,
        link=args.link,
    )

    trumusic.run()


if __name__ == '__main__':
    main()
