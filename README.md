# snapchat-story-saver

I needed a simple way to archive public Snapchat stories from specific creators/accounts without having to manually record my screen or deal with sketchy, ad-filled web downloaders. This tool fetches the public story page, extracts the media assets from the embedded state, and saves them locally.

It skips already downloaded snaps by checking the snap ID, so you can run it on a cron or run it daily to keep a local archive.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/snapchat-story-saver.git
   cd snapchat-story-saver
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To download the current public story of a user:

```bash
python saver.py snapchat_username
```

By default, it saves everything into `./stories/<username>`. You can change the base directory with `--output`:

```bash
python saver.py snapchat_username --output D:\Archive\Snapchat
```

If you want more detailed output during extraction:

```bash
python saver.py snapchat_username --verbose
```

<!-- refreshed: 2026-09-13 -->
