# pylint: disable=too-many-arguments

"""Library json module."""

import _thread
import os
import sys
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from appdirs import user_data_dir
from filelock import FileLock

from youtube_sync.library_data import LibraryData, Source
from youtube_sync.types import VidEntry
from youtube_sync.ytdlp import YtDlp


def _get_library_json_lock_path() -> str:
    """Get the library json path."""
    out = os.path.join(user_data_dir("youtube-sync"), "library.json.lock")
    return out


_FILE_LOCK = FileLock(_get_library_json_lock_path())


def _to_channel_url(source: Source, channel_name: str) -> str:
    from .rumble.rumble_extra import to_channel_url as to_channel_url_rumble
    from .youtube.youtube import to_channel_url as to_channel_url_youtube

    if source == Source.YOUTUBE:
        return to_channel_url_youtube(channel_name)
    elif source == Source.RUMBLE:
        return to_channel_url_rumble(channel_name)
    elif source == Source.BRIGHTEON:
        return f"https://www.brighteon.com/channels/{channel_name}"
    raise ValueError(f"Unknown source: {source}")


def _find_missing_downloads(
    vids: list[VidEntry], dst_video_path: Path
) -> list[VidEntry]:
    """Find missing downloads."""
    out: list[VidEntry] = []
    for vid in vids:
        file_path = vid.file_path
        full_path = dst_video_path / file_path
        if not full_path.exists():
            # if error
            if not vid.error:
                out.append(vid)
            else:
                warnings.warn(f"Skipping {vid.url} because it is marked as an error.")
    all_have_a_date = all(vid.date for vid in out)
    if all_have_a_date:
        # sort oldest first
        out.sort(key=lambda vid: vid.date)  # type: ignore
    return out


def _make_library(
    channel_name: str,
    channel_url: str | None,  # None means auto-find
    source: Source,
    library_path: Path,
) -> "Library":
    url = channel_url or _to_channel_url(source=source, channel_name=channel_name)
    if library_path.exists():
        raise FileExistsError(f"Library file already exists: {library_path}")
    library = Library(
        channel_name=channel_name,
        channel_url=url,
        source=source,
        json_path=library_path,
    )
    library.load()
    return library


_YT_DLP = YtDlp()


class Library:
    """Represents the library"""

    def __init__(
        self,
        channel_name: str,
        channel_url: str,
        source: Source | str,
        json_path: Path,
    ) -> None:
        if isinstance(source, str):
            source = Source.from_str(source)
        self.source = source
        self.ytdlp = _YT_DLP
        self.channel_url = channel_url
        self.channel_name = channel_name
        self.lib_path = json_path
        self.out_dir = json_path.parent
        self.load()
        assert isinstance(self.libdata, LibraryData)

    @property
    def path(self) -> Path:
        """Get the path."""
        return self.lib_path

    @staticmethod
    def create(
        channel_name: str,
        channel_url: str | None,  # None means auto-find
        media_output: Path,
        source: Source,
        # None means place the library at the root of the media_output
        library_path: Path | None = None,
    ) -> "Library":
        library_path = library_path or media_output / "library.json"
        out = _make_library(
            channel_name=channel_name,
            channel_url=channel_url,
            source=source,
            library_path=library_path,
        )
        return out

    @staticmethod
    def get_or_create(
        channel_name: str,
        channel_url: str | None,  # None means auto-find
        media_output: Path,
        source: Source,
        # None means place the library at the root of the media_output
        library_path: Path | None = None,
    ) -> "Library":
        library_path = library_path or media_output / "library.json"
        if library_path.exists():
            library_or_err = Library.from_json(library_path)
            if isinstance(library_or_err, Library):
                return library_or_err
            warnings.warn(
                f"Error loading library: {library_or_err}, falling back to create."
            )

        return Library.create(
            channel_name=channel_name,
            channel_url=channel_url,
            media_output=media_output,
            source=source,
            library_path=library_path,
        )

    @staticmethod
    def from_json(json_path: Path) -> "Library | Exception | FileNotFoundError":
        """Create from json."""
        with _FILE_LOCK:
            lib_or_err = LibraryData.from_json(json_path)
        if not isinstance(lib_or_err, LibraryData):
            return lib_or_err
        libdata = lib_or_err
        channel_name = libdata.channel_name
        channel_url = libdata.channel_url
        source = libdata.source
        return Library(
            channel_name=channel_name,
            channel_url=channel_url,
            source=source,
            json_path=json_path,
        )

    def __repr__(self) -> str:
        return self.libdata.to_json_str()

    def __str__(self) -> str:
        return self.libdata.to_json_str()

    def __eq__(self, value):
        if not isinstance(value, Library):
            return False
        return self.libdata == value.libdata

    def _empty_data(self) -> LibraryData:
        return LibraryData(
            channel_name=self.channel_name,
            channel_url=self.channel_url,
            source=self.source,
            vids=[],
        )

    def known_vids(self, load=True) -> list[VidEntry]:
        """Get the downloaded vids."""
        if load:
            self.load()
        assert self.libdata is not None
        return self.libdata.vids.copy()

    def find_missing_downloads(self) -> list[VidEntry]:
        """Find missing downloads."""
        return _find_missing_downloads(self.libdata.vids, self.out_dir)

    def load(self) -> list[VidEntry]:
        """Load json from file."""
        # self.libdata = _load_json(self.library_json_path)
        # return self.libdata.vids
        with _FILE_LOCK:
            lib_or_err = LibraryData.from_json(self.lib_path)
        if isinstance(lib_or_err, FileNotFoundError):
            lib_or_err = self._empty_data()
            self.libdata = lib_or_err
        elif isinstance(lib_or_err, Exception):
            raise lib_or_err
        elif isinstance(lib_or_err, LibraryData):
            self.libdata = lib_or_err
        else:
            raise ValueError(f"Unexpected return type {type(lib_or_err)}")
        assert isinstance(lib_or_err, LibraryData)
        assert self.channel_name == lib_or_err.channel_name
        assert self.channel_url == lib_or_err.channel_url
        assert self.source == lib_or_err.source
        self.channel_name = self.libdata.channel_name
        self.channel_url = self.libdata.channel_url
        self.source = self.libdata.source
        return self.libdata.vids.copy()

    def save(self, overwrite=False) -> Exception | None:
        """Save json to file."""
        data = self.libdata or self._empty_data()
        text = data.to_json_str()
        with _FILE_LOCK:
            self.lib_path.parent.mkdir(parents=True, exist_ok=True)
            if self.lib_path.exists() and not overwrite:
                return FileExistsError(f"{self.lib_path} exists.")
            self.lib_path.write_text(text, encoding="utf-8")
        return None

    def merge(self, vids: list[VidEntry], save: bool) -> None:
        """Merge the vids into the library."""
        self.load()
        assert self.libdata is not None
        self.libdata.merge(vids)
        if save:
            self.save(overwrite=True)

    def download_missing(
        self,
        download_limit: int | None,
        yt_dlp_uses_docker: bool,
        max_concurrent_downloads: int = 1,
        max_concurrent_conversions: int = 4,
    ) -> None:
        """Download the missing files using thread pools.

        Args:
            download_limit: Maximum number of files to download or None for unlimited
            yt_dlp_uses_docker: Whether to use Docker for yt-dlp
            max_concurrent_downloads: Maximum number of concurrent downloads
            max_concurrent_conversions: Maximum number of concurrent conversions
        """
        from youtube_sync.ytdlp import check_keyboard_interrupt, set_keyboard_interrupt

        assert yt_dlp_uses_docker is False, "Docker not supported yet."
        # Create thread pools with appropriate sizes
        download_pool = ThreadPoolExecutor(max_workers=max_concurrent_downloads)
        convert_pool = ThreadPoolExecutor(max_workers=max_concurrent_conversions)

        try:
            download_count = 0
            while True:
                # Check for keyboard interrupt
                if check_keyboard_interrupt():
                    print("Detected previous keyboard interrupt. Aborting downloads.")
                    break

                if (download_limit is not None) and (download_count >= download_limit):
                    break

                # Find missing downloads
                missing_downloads = self.find_missing_downloads()
                if not missing_downloads:
                    break

                # Determine how many to download in this batch
                remaining_limit = (
                    None if download_limit is None else download_limit - download_count
                )
                batch_size = (
                    len(missing_downloads)
                    if remaining_limit is None
                    else min(len(missing_downloads), remaining_limit)
                )

                if batch_size <= 0:
                    break

                # Prepare download list
                downloads_to_process = []
                for i in range(batch_size):
                    vid = missing_downloads[i]
                    next_url = vid.url
                    next_mp3_path = self.out_dir / vid.file_path
                    downloads_to_process.append((next_url, next_mp3_path))

                print(
                    f"\n#######################\n# Downloading {batch_size} missing files\n"
                    "###################"
                )

                try:
                    # Submit downloads to thread pools
                    futures = self.ytdlp.download_mp3s(
                        downloads=downloads_to_process,
                        download_pool=download_pool,
                        convert_pool=convert_pool,
                    )

                    # Process results as they complete
                    for i, future in enumerate(futures):
                        # Check for keyboard interrupt
                        if check_keyboard_interrupt():
                            print(
                                "Detected keyboard interrupt. Skipping remaining results."
                            )
                            break

                        vid = missing_downloads[i]
                        try:
                            _, _, error = future.result()
                            if error is not None:
                                print(f"Error downloading {vid.url}: {error}")
                                self.mark_error(vid)
                            else:
                                print(f"Successfully downloaded {vid.url}")
                        except KeyboardInterrupt:
                            print(
                                "KeyboardInterrupt detected while processing results. Stopping download."
                            )
                            set_keyboard_interrupt()
                            break
                        except Exception as e:  # pylint: disable=broad-except
                            stacktrace_str = traceback.format_exc()
                            print(f"Error downloading {vid.url}: {e}")
                            print(stacktrace_str)
                            self.mark_error(vid)

                    # Update download count
                    download_count += batch_size

                    # Check for keyboard interrupt after batch
                    if check_keyboard_interrupt():
                        print(
                            "Detected keyboard interrupt after batch. Stopping downloads."
                        )
                        break

                except KeyboardInterrupt:
                    print(
                        "KeyboardInterrupt detected. Stopping download and shutting down thread pools."
                    )
                    set_keyboard_interrupt()
                    # Don't raise here, let the outer try/finally handle cleanup
                    break

        except KeyboardInterrupt:
            print("KeyboardInterrupt detected. Shutting down thread pools.")
            set_keyboard_interrupt()
        finally:
            # Ensure pools are shut down properly
            print("Shutting down download pool...")
            download_pool.shutdown(wait=False, cancel_futures=True)
            print("Shutting down conversion pool...")
            convert_pool.shutdown(wait=False, cancel_futures=True)

            # Re-raise KeyboardInterrupt to notify the main thread
            if sys.exc_info()[0] is KeyboardInterrupt:
                _thread.interrupt_main()
                raise

    def mark_error(self, vid: VidEntry) -> None:
        """Mark the vid as an error."""
        vid.error = True
        self.merge([vid], save=True)
        print(f"Marked {vid.url} as an error.")

    def date_range(self) -> tuple[datetime, datetime] | None:
        """Get the date range."""
        vids = self.load()
        dates = [vid.date for vid in vids if vid.date]
        if not dates:
            return None
        return min(dates), max(dates)
