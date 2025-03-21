import sys
import asyncio
from .cli.parser import create_parser
from .cli.commands import handle_api_command, handle_tags_command
from .API.base import APIRegistryCMD

def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.list:
        info = APIRegistryCMD.get_all_api_info()
        print("Available APIs:")
        for name, availability in info:
            print(f" - {name}: {availability}")
        sys.exit(0)
    
    if not args.api:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.tags:
            tags = asyncio.run(handle_tags_command(args.api))
            print(f"{args.api.capitalize()} tags: {tags}")
        else:
            nsfw = True if args.nsfw else False
            if args.sfw:
                nsfw = False

            result = asyncio.run(handle_api_command(args.api, nsfw, args.query, args.limit))
            print(f"{args.api.capitalize()} result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
